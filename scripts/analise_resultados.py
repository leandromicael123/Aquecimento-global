"""Comparações descritivas para interpretar os resultados do painel."""

import numpy as np
import pandas as pd

from estilo_iscte import Y, MESES, VAR_LABELS


def comparar_paises(dados):
    tabela = dados.groupby("pais")[Y].agg(
        media="mean",
        mediana="median",
        desvio_padrao="std",
        minimo="min",
        maximo="max",
        n="size",
    )
    tabela["meses_negativos_pct"] = dados.groupby("pais")[Y].apply(
        lambda serie: 100 * serie.lt(0).mean()
    )
    return tabela.reset_index().sort_values("media", ascending=False)


def comparar_periodos(dados):
    """Compara taxas mensais; não as confunde com inflação anual acumulada."""
    trabalho = dados.copy()
    trabalho["periodo"] = pd.cut(
        trabalho.ano,
        bins=[1999, 2009, 2019, 2025],
        labels=["2000–2009", "2010–2019", "2020–2025"],
    )
    resumo = (
        trabalho.groupby("periodo", observed=True)[Y]
        .agg(media="mean", mediana="median", desvio_padrao="std", observacoes="size")
        .reset_index()
    )
    nacional = trabalho.groupby(["pais", "periodo"], observed=True)[Y].mean().unstack()
    nacional["mudanca_2020_2025_vs_2010_2019"] = (
        nacional["2020–2025"] - nacional["2010–2019"]
    )
    return resumo, nacional.reset_index()


def decompor_variancia(dados, variaveis):
    """Decompõe a soma de quadrados, com ponderação pelo número de meses."""
    linhas = []
    for variavel in variaveis:
        media_global = dados[variavel].mean()
        medias = dados.groupby("pais_iso3")[variavel].transform("mean")
        total = ((dados[variavel] - media_global) ** 2).sum()
        dentro = ((dados[variavel] - medias) ** 2).sum()
        entre = ((medias - media_global) ** 2).sum()
        assert np.isclose(total, dentro + entre)
        linhas.append(
            {
                "Variável": VAR_LABELS[variavel],
                "Dentro (%)": 100 * dentro / total,
                "Entre (%)": 100 * entre / total,
            }
        )
    return pd.DataFrame(linhas)


def comparar_janelas_climaticas(dados):
    """Usa duas janelas completas de cinco anos, com 60 meses por país."""
    cedo = dados.loc[dados.ano.between(2001, 2005)]
    recente = dados.loc[dados.ano.between(2021, 2025)]
    assert cedo.groupby("pais_iso3").size().eq(60).all()
    assert recente.groupby("pais_iso3").size().eq(60).all()
    inicio = cedo.groupby("pais").anomalia_temperatura_c.mean()
    fim = recente.groupby("pais").anomalia_temperatura_c.mean()
    comparacao = pd.DataFrame({"2001–2005 (°C)": inicio, "2021–2025 (°C)": fim})
    comparacao["Diferença (°C)"] = fim - inicio
    return comparacao.reset_index().sort_values("Diferença (°C)", ascending=False)


def correlacoes_com_inflacao(dados):
    """Compara associações brutas, dentro do país e após dupla centração."""
    variaveis = [
        "anomalia_temperatura_c",
        "defice_hidrico_3m_z",
        "ln_pib_pc_ppc_ano_anterior",
        "peso_agricola_pct_ano_anterior",
    ]
    # A fórmula de dupla centração exige a grelha equilibrada país × data.
    n_paises = dados.pais_iso3.nunique()
    n_datas = dados.data.nunique()
    assert len(dados) == n_paises * n_datas
    assert not dados.duplicated(["pais_iso3", "data"]).any()
    colunas = [Y] + variaveis
    dentro = dados[colunas] - dados.groupby("pais_iso3")[colunas].transform("mean")
    dupla = (
        dentro
        - dados.groupby("data")[colunas].transform("mean")
        + dados[colunas].mean()
    )
    linhas = []
    for variavel in variaveis:
        linhas.append(
            {
                "Variável": VAR_LABELS[variavel],
                "Bruta": dados[Y].corr(dados[variavel]),
                "Dentro do país": dentro[Y].corr(dentro[variavel]),
                "Sem país e data": dupla[Y].corr(dupla[variavel]),
            }
        )
    return pd.DataFrame(linhas)


def resumir_perfil_sazonal(perfil):
    resumo = pd.DataFrame(
        {
            "País": perfil.index,
            "Mês máximo": [MESES[int(mes) - 1] for mes in perfil.idxmax(axis=1)],
            "Mês mínimo": [MESES[int(mes) - 1] for mes in perfil.idxmin(axis=1)],
            "Máximo centrado": perfil.max(axis=1),
            "Mínimo centrado": perfil.min(axis=1),
            "Amplitude (p.p. aprox.)": perfil.max(axis=1) - perfil.min(axis=1),
        }
    )
    return resumo.reset_index(drop=True).sort_values(
        "Amplitude (p.p. aprox.)", ascending=False
    )
