"""Estatísticas descritivas utilizadas no notebook de exploração."""

import pandas as pd

from estilo_iscte import VAR_LABELS, UNITS, Y


def estatisticas_globais(dados, variaveis):
    nomes = {
        "count": "N",
        "mean": "Média",
        "std": "DP",
        "min": "Mínimo",
        "25%": "Q1",
        "50%": "Mediana",
        "75%": "Q3",
        "max": "Máximo",
    }
    resumo = dados[variaveis].describe().T.rename(columns=nomes)
    resumo.insert(0, "Unidade", [UNITS[coluna] for coluna in resumo.index])
    resumo.insert(0, "Variável", [VAR_LABELS[coluna] for coluna in resumo.index])
    return resumo.reset_index(names="coluna")


def estatisticas_por_pais(dados):
    return (
        dados.groupby(["pais_iso3", "pais"])[Y]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )


def evolucao_agregada(dados):
    return dados.groupby("data")[Y].agg(["mean", "median"])


def decompor_dispersao(dados, variaveis):
    """Calcula os três desvios padrão; não são componentes aditivas."""
    linhas = []
    for variavel in variaveis:
        medias = dados.groupby("pais_iso3")[variavel].mean()
        desvios = dados[variavel] - dados.groupby("pais_iso3")[variavel].transform(
            "mean"
        )
        linhas.append(
            {
                "coluna": variavel,
                "Variável": VAR_LABELS[variavel],
                "Unidade": UNITS[variavel],
                "DP total": dados[variavel].std(),
                "DP entre médias": medias.std(),
                "DP dentro": desvios.std(),
            }
        )
    return pd.DataFrame(linhas)


def anomalias_anuais(dados):
    return dados.pivot_table(
        index="pais", columns="ano", values="anomalia_temperatura_c", aggfunc="mean"
    )
