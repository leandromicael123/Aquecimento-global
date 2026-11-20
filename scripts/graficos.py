"""Figuras do trabalho. Cada função cria uma figura e guarda PNG e SVG."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

from estilo_iscte import (
    AZUL,
    CINZA,
    LARANJA,
    PRETO,
    VERMELHO,
    MESES,
    Y,
    Y_LABEL,
    UNITS,
    VAR_LABELS,
    eixo,
    cabecalho_fig,
    mapa,
    pt,
    salvar,
)


def trajetorias_por_pais(dados, pasta):
    figura, eixos = plt.subplots(5, 3, figsize=(17, 17), sharex=True, sharey=True)
    for ax, (pais, grupo) in zip(eixos.flat, dados.groupby("pais", sort=True)):
        media_movel = grupo[Y].rolling(12, min_periods=12).mean()
        ax.plot(grupo.data, grupo[Y], color=AZUL, alpha=0.35, linewidth=0.7)
        ax.plot(grupo.data, media_movel, color=LARANJA, linewidth=1.6)
        eixo(ax, pais, "Ano", "100 × Δ ln IPC", zero=True)
        ax.xaxis.set_major_locator(mdates.YearLocator(10))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(labelbottom=True, labelleft=True)
    cabecalho_fig(
        figura,
        "Figura 2.1",
        "Trajetórias da inflação alimentar",
        "Mesma escala nos 15 países · frequência mensal · fevereiro de 2000 a dezembro de 2025",
    )
    legenda = [
        Line2D([0], [0], color=AZUL, label="Taxa mensal"),
        Line2D([0], [0], color=LARANJA, linewidth=2, label="Média móvel de 12 meses"),
    ]
    figura.legend(
        handles=legenda, loc="upper right", bbox_to_anchor=(0.96, 0.945), ncol=2
    )
    figura.subplots_adjust(
        left=0.07, right=0.97, top=0.885, bottom=0.075, hspace=0.52, wspace=0.25
    )
    salvar(
        figura,
        pasta / "01_trajetorias_por_pais",
        "Taxa logarítmica mensal, aproximadamente percentual. A média móvel é retrospetiva e não constitui ajuste sazonal.",
    )


def distribuicoes_nacionais(dados, pasta):
    medias = dados.groupby("pais")[Y].mean().sort_values()
    grupos = [dados.loc[dados.pais.eq(pais), Y] for pais in medias.index]
    figura, ax = plt.subplots(figsize=(12, 9))
    ax.boxplot(
        grupos,
        orientation="horizontal",
        tick_labels=medias.index,
        showfliers=False,
        patch_artist=True,
        widths=0.55,
        boxprops={"facecolor": "#D9DFFD", "edgecolor": AZUL},
        medianprops={"color": PRETO, "linewidth": 1.6},
        whiskerprops={"color": "#8592B4"},
        capprops={"color": "#8592B4"},
    )
    posicoes = np.arange(1, len(medias) + 1)
    ax.scatter(
        medias.values, posicoes, color=AZUL, s=34, zorder=4, label="Média mensal"
    )
    for posicao, valor in zip(posicoes, medias.values):
        ax.annotate(
            pt(valor),
            (valor, posicao),
            xytext=(7, 8),
            textcoords="offset points",
            fontsize=8,
            color=AZUL,
        )
    eixo(ax, "", Y_LABEL, "País")
    ax.axvline(0, color=CINZA, linewidth=0.7)
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.5)
    cabecalho_fig(
        figura,
        "Figura 2.2",
        "Distribuição da inflação alimentar",
        "Países ordenados pela média mensal",
    )
    figura.subplots_adjust(left=0.17, right=0.96, top=0.88, bottom=0.13)
    salvar(
        figura,
        pasta / "02_distribuicoes_nacionais",
        "Linha preta: mediana. Caixa: Q1–Q3. Bigodes: 1,5 × IQR. Pontos exteriores omitidos apenas da figura. Rótulos: médias.",
    )


def evolucao_da_media(mensal, pasta):
    figura, ax = plt.subplots(figsize=(13, 5.8))
    media_movel = mensal["mean"].rolling(12, min_periods=12).mean()
    mediana_movel = mensal["median"].rolling(12, min_periods=12).mean()
    ax.plot(
        mensal.index,
        mensal["mean"],
        color=AZUL,
        alpha=0.35,
        linewidth=0.8,
        label="Média mensal dos países",
    )
    ax.plot(
        mensal.index,
        media_movel,
        color=AZUL,
        linewidth=2.2,
        label="Média · média móvel 12 meses",
    )
    ax.plot(
        mensal.index,
        mediana_movel,
        color=LARANJA,
        linewidth=1.6,
        linestyle="--",
        label="Mediana · média móvel 12 meses",
    )
    eixo(ax, "", "Ano", Y_LABEL, zero=True)
    ax.legend(loc="upper left", fontsize=9)
    cabecalho_fig(
        figura,
        "Figura 2.3",
        "Evolução agregada da inflação alimentar",
        "Média e mediana · países com igual peso",
    )
    figura.subplots_adjust(left=0.085, right=0.97, top=0.84, bottom=0.18)
    salvar(
        figura,
        pasta / "03_evolucao_agregada",
        "Agregação não ponderada pela população ou despesa. Não representa uma taxa oficial de inflação mundial.",
    )


def dispersao_entre_dentro(variacao, pasta):
    colunas = [Y, "ln_pib_pc_ppc_ano_anterior", "peso_agricola_pct_ano_anterior"]
    unidades_curtas = ["aprox. %/mês", "log natural", "p.p. do PIB"]
    figura, eixos = plt.subplots(1, 3, figsize=(15, 5.5))
    for ax, variavel, unidade in zip(eixos, colunas, unidades_curtas):
        linha = variacao.set_index("coluna").loc[variavel]
        valores = [linha["DP entre médias"], linha["DP dentro"]]
        barras = ax.bar(
            ["Entre médias", "Dentro do país"],
            valores,
            color=[AZUL, "#8E9BE7"],
            width=0.58,
        )
        ax.bar_label(barras, labels=[pt(valor) for valor in valores], padding=5)
        eixo(
            ax,
            VAR_LABELS[variavel],
            "Componente descritiva",
            "Desvio padrão · " + unidade,
        )
        ax.set_ylim(0, max(valores) * 1.25)
    cabecalho_fig(
        figura,
        "Figura 2.4",
        "Onde se concentra a variabilidade?",
        "As escalas são próprias de cada variável · valores indicados sobre as barras",
    )
    figura.subplots_adjust(left=0.07, right=0.97, top=0.77, bottom=0.23, wspace=0.48)
    salvar(
        figura,
        pasta / "04_variabilidade_entre_dentro",
        "As medidas usam denominadores diferentes: não são parcelas aditivas da variância. As covariáveis económicas são anuais.",
    )


def mapa_anomalias(anual, pasta):
    figura, ax = plt.subplots(figsize=(15, 7.5))
    limite = float(np.abs(anual.to_numpy()).max())
    mapa(
        ax,
        anual,
        "",
        "Ano",
        "País",
        "Anomalia térmica (°C)",
        limites=(-limite, limite),
        divergente=True,
    )
    ax.set_xticks(np.arange(len(anual.columns))[::2], labels=anual.columns[::2])
    cabecalho_fig(
        figura,
        "Figura 2.5",
        "Anomalia térmica média por país e ano",
        "Azul: acima da referência local · vermelho: abaixo da referência local",
    )
    figura.subplots_adjust(left=0.14, right=0.95, top=0.84, bottom=0.16)
    salvar(
        figura,
        pasta / "05_anomalias_termicas",
        "Média anual das anomalias mensais face a 1991–2020. O ano 2000 inclui fevereiro a dezembro; os restantes incluem 12 meses.",
    )


def mapa_sazonal(perfil, pasta):
    tabela = perfil.copy()
    tabela.columns = MESES
    limite = float(np.abs(tabela.to_numpy()).max())
    figura, ax = plt.subplots(figsize=(13, 8))
    mapa(
        ax,
        tabela,
        "",
        "Mês do calendário",
        "País",
        "Desvio face à média do país (p.p. aprox.)",
        limites=(-limite, limite),
        divergente=True,
        anotacoes=True,
    )
    cabecalho_fig(
        figura,
        "Figura 3.1",
        "O padrão sazonal muda entre países",
        "Médias por mês do calendário após retirar a média de cada país",
    )
    figura.subplots_adjust(left=0.15, right=0.96, top=0.85, bottom=0.15)
    salvar(
        figura,
        pasta / "01_perfil_sazonal",
        "Cada célula identifica país e mês; o valor é a média centrada. Esta figura é descritiva e não realiza um teste estatístico.",
    )


def mapa_autocorrelacao(acfs, pasta):
    figura, eixos = plt.subplots(1, 2, figsize=(18, 8))
    nomes = [
        ("original", "Resposta original"),
        ("sem_calendario_tendencia", "Sem calendário e tendência linear"),
    ]
    for ax, (serie, titulo) in zip(eixos, nomes):
        valores = acfs.loc[acfs.serie.eq(serie)].pivot(
            index="pais", columns="desfasamento", values="acf"
        )
        mapa(
            ax,
            valores,
            titulo,
            "Desfasamento (meses)",
            "País",
            "Autocorrelação",
            limites=(-1, 1),
            divergente=True,
        )
        ax.set_xticks([0, 5, 11, 17, 23], labels=[1, 6, 12, 18, 24])
    cabecalho_fig(
        figura,
        "Figura 3.2",
        "Dependência temporal até 24 meses",
        "A retirada de componentes determinísticas não garante independência dos resíduos",
    )
    figura.subplots_adjust(left=0.09, right=0.96, top=0.83, bottom=0.15, wspace=0.42)
    salvar(
        figura,
        pasta / "02_autocorrelacao",
        "Correlação de cada série consigo própria a diferentes desfasamentos. As cores não representam significância estatística.",
    )


def serie_choques(choques, pasta):
    figura, ax = plt.subplots(figsize=(13, 6))
    ax.plot(
        choques.index,
        choques.media_transversal,
        color=AZUL,
        linewidth=1,
        label="Média transversal",
    )
    ax.plot(
        choques.index,
        choques.mediana_transversal,
        color=LARANJA,
        linewidth=0.9,
        linestyle="--",
        label="Mediana transversal",
    )
    maiores = choques.media_transversal.abs().nlargest(3).index
    for ordem, data in enumerate(sorted(maiores)):
        valor = choques.loc[data, "media_transversal"]
        ax.scatter(data, valor, color=AZUL, s=25, zorder=4)
        ax.annotate(
            f"{data:%m/%Y}\n{pt(valor)}",
            (data, valor),
            xytext=(7, 18 + 20 * (ordem % 2)),
            textcoords="offset points",
            fontsize=8,
            arrowprops={"arrowstyle": "-", "color": CINZA},
        )
    eixo(ax, "", "Ano", "Inflação centrada (p.p. aprox.)", zero=True)
    ax.margins(y=0.25)
    ax.legend(loc="upper left")
    cabecalho_fig(
        figura,
        "Figura 3.3",
        "Movimentos simultâneos da inflação alimentar",
        "Desvios face ao perfil mensal de cada país · todos os países com igual peso",
    )
    figura.subplots_adjust(left=0.09, right=0.97, top=0.83, bottom=0.17)
    salvar(
        figura,
        pasta / "03_choques_comuns",
        "Rótulos: três meses de maior desvio médio absoluto. A simultaneidade não identifica uma causa global ou um acontecimento específico.",
    )


def mapa_correlacoes(correlacao, pasta):
    figura, ax = plt.subplots(figsize=(13, 10))
    mapa(
        ax,
        correlacao,
        "",
        "País",
        "País",
        "Correlação de Pearson",
        limites=(-1, 1),
        divergente=True,
        anotacoes=True,
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    cabecalho_fig(
        figura,
        "Figura 3.4",
        "Associação contemporânea entre países",
        "Séries centradas pelo perfil país–mês · mesma janela temporal",
    )
    figura.subplots_adjust(left=0.16, right=0.95, top=0.87, bottom=0.22)
    salvar(
        figura,
        pasta / "04_correlacoes_paises",
        "Diagonal igual a 1 por construção. As células são correlações descritivas, sem correção adicional de tendência e sem teste de causalidade.",
    )


def extremos_por_pais(resumo, pasta):
    resumo = resumo.sort_values("percentagem")
    figura, ax = plt.subplots(figsize=(12, 8))
    barras = ax.barh(resumo.pais, resumo.percentagem, color=AZUL, height=0.62)
    rotulos = [
        f"{pt(linha.percentagem,1)}% · n={int(linha.uniao)}"
        for linha in resumo.itertuples()
    ]
    ax.bar_label(barras, labels=rotulos, padding=6, fontsize=9)
    ax.set_xlim(0, resumo.percentagem.max() * 1.3)
    eixo(ax, "", "Observações sinalizadas (%)", "País")
    ax.grid(axis="x", alpha=0.5)
    cabecalho_fig(
        figura,
        "Figura 3.5",
        "Onde se concentram os valores extremos?",
        "União das regras IQR global e nacional · sem excluir observações",
    )
    figura.subplots_adjust(left=0.17, right=0.96, top=0.85, bottom=0.16)
    salvar(
        figura,
        pasta / "05_extremos_por_pais",
        "Sinalização não implica erro. Cada país tem 311 observações; rótulos apresentam a percentagem e a contagem, sem dupla contagem.",
    )


def sensibilidade_da_media(sensibilidade, pasta):
    tabela = sensibilidade.sort_values("media_original")
    posicoes = np.arange(len(tabela))
    figura, ax = plt.subplots(figsize=(12, 8))
    ax.hlines(
        posicoes,
        tabela.media_original,
        tabela.media_cenario,
        color="#A7AFCB",
        linewidth=2,
    )
    ax.scatter(
        tabela.media_original, posicoes, color=AZUL, s=38, label="Amostra integral"
    )
    ax.scatter(
        tabela.media_cenario,
        posicoes,
        color=LARANJA,
        s=38,
        marker="s",
        label="Cenário: limites nos quantis 1% e 99%",
    )
    ax.set_yticks(posicoes, labels=tabela.pais)
    eixo(ax, "", "Inflação média mensal (aprox. %)", "País")
    ax.legend(loc="lower right", fontsize=9)
    cabecalho_fig(
        figura,
        "Figura 3.6",
        "Sensibilidade da média aos extremos",
        "Cenário descritivo separado · limites calculados dentro de cada país",
    )
    figura.subplots_adjust(left=0.17, right=0.96, top=0.85, bottom=0.16)
    salvar(
        figura,
        pasta / "06_sensibilidade_extremos",
        "O cenário não altera o painel original nem é uma decisão de tratamento. Mudanças nos coeficientes terão de ser avaliadas após estimação.",
    )
