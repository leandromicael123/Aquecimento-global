"""Leitura e verificações dos dados, sem alterar os valores de origem."""

from pathlib import Path

import numpy as np
import pandas as pd

CHAVE = ["pais_iso3", "data"]
ECONOMICAS = [
    "ln_pib_pc_ppc_ano_anterior",
    "peso_agricola_pct_ano_anterior",
]


def ler_painel(pasta_dados):
    ficheiro = Path(pasta_dados) / "painel_indicadores.csv"
    dados = pd.read_csv(ficheiro, parse_dates=["data"])
    return dados.sort_values(CHAVE).reset_index(drop=True)


def resumir_cobertura(dados):
    """Conta os meses por país e verifica a grelha completa país–mês."""
    meses = pd.date_range(dados.data.min(), dados.data.max(), freq="MS")
    paises = sorted(dados.pais_iso3.unique())
    grelha = pd.MultiIndex.from_product([paises, meses], names=CHAVE)
    observados = pd.MultiIndex.from_frame(dados[CHAVE])
    ausentes = grelha.difference(observados)
    cobertura = (
        dados.groupby(["pais_iso3", "pais"])
        .agg(meses=("data", "size"), inicio=("data", "min"), fim=("data", "max"))
        .reset_index()
    )
    resumo = {
        "linhas": len(dados),
        "colunas": len(dados.columns),
        "paises": len(paises),
        "meses": len(meses),
        "duplicados": int(dados.duplicated(CHAVE).sum()),
        "pares_ausentes": len(ausentes),
        "equilibrado": len(ausentes) == 0 and not dados.duplicated(CHAVE).any(),
    }
    return resumo, cobertura


def contar_omissos(dados):
    return pd.DataFrame(
        {
            "Coluna": dados.columns,
            "Tipo": [str(dados[coluna].dtype) for coluna in dados],
            "Omissos": [int(dados[coluna].isna().sum()) for coluna in dados],
            "Omissos (%)": [100 * dados[coluna].isna().mean() for coluna in dados],
        }
    )


def conferir_campos(dados, variaveis):
    """Interrompe a análise se houver chaves ou metadados incoerentes."""
    assert not dados.duplicated(CHAVE).any(), "Há pares país–mês repetidos."
    assert np.isfinite(dados[variaveis]).all().all(), "Há valores não finitos."
    assert dados.ano.eq(dados.data.dt.year).all()
    assert dados.mes.eq(dados.data.dt.month).all()
    assert dados.ano_dados_economicos.eq(dados.ano - 1).all()
    contagem = dados.groupby(["pais_iso3", "ano"])[ECONOMICAS].nunique()
    assert contagem.le(1).all().all(), "Uma covariável anual varia dentro do ano."


def conferir_transformacoes(dados, pasta_dados):
    anuais = pd.read_csv(Path(pasta_dados) / "dados_brutos_anuais.csv")
    comparacao = dados.merge(
        anuais[["pais_iso3", "ano", "pib_pc_ppc_2021", "peso_agricola_pct_pib"]],
        left_on=["pais_iso3", "ano_dados_economicos"],
        right_on=["pais_iso3", "ano"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_fonte"),
    )
    assert comparacao.pib_pc_ppc_2021.notna().all()
    erros = {
        "Log PIB do ano anterior": comparacao.ln_pib_pc_ppc_ano_anterior
        - np.log(comparacao.pib_pc_ppc_2021),
        "Peso agrícola do ano anterior": comparacao.peso_agricola_pct_ano_anterior
        - comparacao.peso_agricola_pct_pib,
        "Calor × log PIB": dados.calor_x_ln_pib
        - dados.anomalia_temperatura_c * dados.ln_pib_pc_ppc_ano_anterior,
        "Calor × peso agrícola": dados.calor_x_peso_agricola
        - dados.anomalia_temperatura_c * dados.peso_agricola_pct_ano_anterior,
    }
    conferencia = pd.DataFrame(
        [
            {"Verificação": nome, "Erro absoluto máximo": valores.abs().max()}
            for nome, valores in erros.items()
        ]
    )
    assert conferencia["Erro absoluto máximo"].max() < 1e-9
    return conferencia


def sinalizar_iqr(serie):
    """Sinaliza valores fora de Q1 − 1,5 IQR e Q3 + 1,5 IQR."""
    q1, q3 = serie.quantile([0.25, 0.75])
    amplitude = q3 - q1
    return (serie < q1 - 1.5 * amplitude) | (serie > q3 + 1.5 * amplitude)


def resumir_extremos(dados, variaveis):
    linhas = []
    for variavel in variaveis:
        sinalizados = sinalizar_iqr(dados[variavel])
        linhas.append(
            {
                "coluna": variavel,
                "Sinalizados": int(sinalizados.sum()),
                "Percentagem": 100 * sinalizados.mean(),
            }
        )
    return pd.DataFrame(linhas)
