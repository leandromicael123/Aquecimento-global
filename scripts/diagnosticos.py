"""Diagnósticos exploratórios e preparação de amostras comparáveis."""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import kruskal
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.multitest import multipletests

from estilo_iscte import Y
from preparacao import sinalizar_iqr

ESPECIFICACOES = {
    "desenvolvimento": [
        "anomalia_temperatura_c",
        "defice_hidrico_3m_z",
        "ln_pib_pc_ppc_ano_anterior",
        "calor_x_ln_pib",
    ],
    "agricultura": [
        "anomalia_temperatura_c",
        "defice_hidrico_3m_z",
        "peso_agricola_pct_ano_anterior",
        "calor_x_peso_agricola",
    ],
}


def perfil_sazonal(dados):
    trabalho = dados.assign(
        mes_calendario=dados.data.dt.month,
        inflacao_centrada=dados[Y] - dados.groupby("pais_iso3")[Y].transform("mean"),
    )
    return trabalho.pivot_table(
        index="pais",
        columns="mes_calendario",
        values="inflacao_centrada",
        aggfunc="mean",
    )


def ajustar_calendario(grupo, desfasamentos=12):
    """Regressão auxiliar: constante, tendência linear e 11 indicadores mensais."""
    grupo = grupo.sort_values("data").reset_index(drop=True)
    indicadores = pd.get_dummies(
        grupo.data.dt.month, prefix="mes", drop_first=True, dtype=float
    )
    indicadores.insert(0, "tendencia", np.arange(len(grupo)) / 12)
    desenho = sm.add_constant(indicadores)
    modelo = sm.OLS(grupo[Y], desenho).fit(
        cov_type="HAC", cov_kwds={"maxlags": desfasamentos, "use_correction": True}
    )
    return modelo


def testar_sazonalidade(dados):
    """Compara Kruskal com Wald/HAC; BH é aplicado por família de 15 testes."""
    linhas = []
    for iso, grupo in dados.groupby("pais_iso3"):
        amostras = [grupo.loc[grupo.data.dt.month.eq(mes), Y] for mes in range(1, 13)]
        _, p_kruskal = kruskal(*amostras)
        resultado = {
            "pais_iso3": iso,
            "pais": grupo.pais.iloc[0],
            "p_kruskal": p_kruskal,
        }
        for lag in (12, 24):
            modelo = ajustar_calendario(grupo, desfasamentos=lag)
            termos = [
                i
                for i, nome in enumerate(modelo.params.index)
                if nome.startswith("mes_")
            ]
            restricoes = np.eye(len(modelo.params))[termos]
            teste = modelo.wald_test(restricoes, scalar=True)
            resultado[f"p_hac_{lag}"] = float(teste.pvalue)
        linhas.append(resultado)
    testes = pd.DataFrame(linhas)
    for metodo in ("kruskal", "hac_12", "hac_24"):
        testes[f"q_{metodo}"] = multipletests(testes[f"p_{metodo}"], method="fdr_bh")[1]
    return testes


def diagnosticar_dependencia(dados):
    """Mede dependência na série original e após retirar calendário/tendência."""
    linhas = []
    acfs = []
    for iso, grupo in dados.groupby("pais_iso3"):
        grupo = grupo.sort_values("data").reset_index(drop=True)
        datas = pd.DatetimeIndex(grupo.data)
        assert datas.equals(pd.date_range(datas.min(), datas.max(), freq="MS"))
        modelo = ajustar_calendario(grupo)
        series = {"original": grupo[Y], "sem_calendario_tendencia": modelo.resid}
        for nome, serie in series.items():
            lb = acorr_ljungbox(serie, lags=[12], return_df=True).iloc[0]
            linhas.append(
                {
                    "pais_iso3": iso,
                    "pais": grupo.pais.iloc[0],
                    "serie": nome,
                    "acf_1": serie.autocorr(1),
                    "acf_12": serie.autocorr(12),
                    "ljung_box_12": lb.lb_stat,
                    "p_lb": lb.lb_pvalue,
                }
            )
            for lag in range(1, 25):
                acfs.append(
                    {
                        "pais": grupo.pais.iloc[0],
                        "serie": nome,
                        "desfasamento": lag,
                        "acf": serie.autocorr(lag),
                    }
                )
    tabela = pd.DataFrame(linhas)
    tabela["q_lb"] = np.nan
    for nome in tabela.serie.unique():
        mask = tabela.serie.eq(nome)
        tabela.loc[mask, "q_lb"] = multipletests(
            tabela.loc[mask, "p_lb"], method="fdr_bh"
        )[1]
    return tabela, pd.DataFrame(acfs)


def medir_choques_comuns(dados):
    """Retira o perfil país–mês e calcula média transversal e correlações."""
    trabalho = dados.assign(mes_calendario=dados.data.dt.month)
    trabalho["desvio"] = trabalho[Y] - trabalho.groupby(
        ["pais_iso3", "mes_calendario"]
    )[Y].transform("mean")
    matriz = trabalho.pivot(index="data", columns="pais", values="desvio")
    resumo = pd.DataFrame(
        {
            "media_transversal": matriz.mean(axis=1),
            "mediana_transversal": matriz.median(axis=1),
            "paises_positivos": matriz.gt(0).sum(axis=1),
            "dp_entre_paises": matriz.std(axis=1),
        }
    )
    return resumo, matriz.corr()


def conferir_inflacao(dados, pasta_dados):
    """Recalcula a resposta a partir do IPC publicado incluído no conjunto."""
    brutos = pd.read_csv(
        Path(pasta_dados) / "dados_brutos_mensais.csv", parse_dates=["data"]
    )
    brutos = brutos.sort_values(["pais_iso3", "data"])
    brutos["ipc_anterior"] = brutos.groupby("pais_iso3").ipc_alimentar_2015_100.shift(1)
    brutos["data_anterior"] = brutos.groupby("pais_iso3").data.shift(1)
    brutos["y_recalculada"] = 100 * np.log(
        brutos.ipc_alimentar_2015_100 / brutos.ipc_anterior
    )
    colunas = [
        "pais_iso3",
        "data",
        "data_anterior",
        "ipc_alimentar_2015_100",
        "ipc_anterior",
        "y_recalculada",
    ]
    conferencia = dados.merge(
        brutos[colunas], on=["pais_iso3", "data"], validate="one_to_one"
    )
    atual = conferencia.data.dt.to_period("M").astype("int64")
    anterior = conferencia.data_anterior.dt.to_period("M").astype("int64")
    assert atual.sub(anterior).eq(1).all()
    assert len(conferencia) == len(dados)
    conferencia["erro_absoluto"] = abs(conferencia[Y] - conferencia.y_recalculada)
    assert conferencia.erro_absoluto.max() < 1e-9
    return conferencia


def analisar_extremos(conferencia):
    resultado = conferencia.copy()
    resultado["iqr_global"] = sinalizar_iqr(resultado[Y])
    resultado["iqr_pais"] = resultado.groupby("pais_iso3")[Y].transform(sinalizar_iqr)
    selecionados = resultado.iqr_global | resultado.iqr_pais
    resumo = (
        resultado.groupby("pais")
        .agg(
            n=("data", "size"),
            globais=("iqr_global", "sum"),
            nacionais=("iqr_pais", "sum"),
        )
        .reset_index()
    )
    resultado["sinalizado"] = selecionados
    uniao = resultado.groupby("pais").sinalizado.sum()
    resumo["uniao"] = resumo.pais.map(uniao)
    resumo["percentagem"] = 100 * resumo.uniao / resumo.n
    return resultado.loc[selecionados].copy(), resumo


def sensibilidade_extremos(dados):
    """Aparagem de 1% em cada cauda por país, apenas como cenário descritivo."""
    trabalho = dados.copy()
    quantis = trabalho.groupby("pais_iso3")[Y]
    inferior = quantis.transform(lambda serie: serie.quantile(0.01))
    superior = quantis.transform(lambda serie: serie.quantile(0.99))
    trabalho["cenario_1_99"] = trabalho[Y].clip(lower=inferior, upper=superior)
    resumo = (
        trabalho.groupby("pais")
        .agg(
            media_original=(Y, "mean"),
            media_cenario=("cenario_1_99", "mean"),
            dp_original=(Y, "std"),
            dp_cenario=("cenario_1_99", "std"),
        )
        .reset_index()
    )
    resumo["diferenca_media"] = resumo.media_cenario - resumo.media_original
    return resumo


def preparar_amostras(dados):
    """Devolve a amostra completa de cada especificação e a interseção das duas."""
    amostras = {}
    linhas = []
    for nome, covariaveis in ESPECIFICACOES.items():
        colunas = ["pais_iso3", "pais", "data", Y] + covariaveis
        amostra = dados[colunas].dropna().copy()
        amostras[nome] = amostra
        linhas.append(
            {
                "Especificação": nome,
                "Observações": len(amostra),
                "Países": amostra.pais_iso3.nunique(),
                "Meses": amostra.data.nunique(),
                "Excluídas": len(dados) - len(amostra),
                "Covariáveis": ", ".join(covariaveis),
            }
        )
    todas = list(dict.fromkeys(sum(ESPECIFICACOES.values(), [])))
    amostras["comum"] = dados[["pais_iso3", "pais", "data", Y] + todas].dropna().copy()
    return amostras, pd.DataFrame(linhas)


def plano_alteracoes(sazonalidade, dependencia, extremos, correlacao, n_amostra):
    """Liga os resultados calculados a propostas concretas para os modelos."""
    n_sazonais = int(sazonalidade.q_hac_12.lt(0.05).sum())
    n_serial = int(
        dependencia.loc[dependencia.serie.eq("original"), "q_lb"].lt(0.05).sum()
    )
    pares = correlacao.to_numpy()[np.triu_indices(len(correlacao), 1)]
    propostas = [
        (
            "A01",
            "Alta",
            "Sazonalidade",
            f"{n_sazonais}/15 países com q < 0,05 no Wald/HAC(12).",
            "Comparar uma especificação com indicadores do mês do calendário; avaliar diferenças sazonais entre países.",
            "Comparar os resíduos e repetir os diagnósticos após estimação.",
        ),
        (
            "A02",
            "Alta",
            "Dependência temporal",
            f"{n_serial}/15 países sinalizados na resposta original.",
            "Usar inferência que considere dependência dentro do país e verificar dinâmica residual.",
            "Reexaminar ACF e resíduos; explicitar limites de apenas 15 grupos.",
        ),
        (
            "A03",
            "Alta",
            "Choques comuns",
            f"Correlação mediana entre pares: {np.median(pares):.3f}.",
            "Comparar modelos com e sem efeitos fixos de data completa, mantendo a mesma amostra.",
            "Comparar estabilidade dos coeficientes e dependência transversal dos resíduos.",
        ),
        (
            "A04",
            "Alta",
            "Extremos",
            f"{len(extremos)} observações sinalizadas; transformação do IPC conferida.",
            "Manter a amostra principal; confirmar registos junto da fonte e usar sensibilidade separada.",
            "Apresentar resultados integrais e de sensibilidade; justificar qualquer exclusão.",
        ),
        (
            "A05",
            "Alta",
            "Comparabilidade",
            f"{n_amostra} observações na amostra comum.",
            "Reutilizar exatamente os mesmos pares país–data e covariáveis para pooled, FE e RE dentro de cada especificação.",
            "Confirmar índices, número de linhas e controlos de calendário antes de comparar.",
        ),
        (
            "A06",
            "Média",
            "Interações e unidades",
            "Interações com variáveis económicas anuais não centradas.",
            "Centrar as covariáveis económicas como reparametrização e reconstruir interações; guardar as médias usadas.",
            "Confirmar previsões equivalentes e explicitar a interpretação dos efeitos principais.",
        ),
        (
            "A07",
            "Média",
            "Disponibilidade em tempo real",
            "O desfasamento anual não comprova a data de publicação.",
            "Documentar que a análise é retrospetiva; recolher versões históricas se o objetivo for previsão em tempo real.",
            "Registar datas de publicação antes de afirmar disponibilidade histórica.",
        ),
    ]
    return pd.DataFrame(
        propostas,
        columns=[
            "ID",
            "Prioridade",
            "Tema",
            "Evidência",
            "Alteração proposta",
            "Como verificar",
        ],
    )
