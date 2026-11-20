"""Estilo comum e utilitários de apresentação para os notebooks do trabalho."""

from pathlib import Path
import hashlib
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from IPython.display import display, Markdown

AZUL = "#0D28C2"
PRETO = "#171B26"
CINZA = "#595959"
GELO = "#F3F5FC"
GRELHA = "#DFE4F1"
TURQUESA = "#14BFB8"
LARANJA = "#F18D00"
VERMELHO = "#B42332"
ROXO = "#8517AC"
MESES = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]
Y = "inflacao_alimentar_log_pct"
Y_LABEL = "Inflação alimentar (100 × Δ ln IPC; aprox. %/mês)"
VAR_LABELS = {
    Y: "Inflação alimentar",
    "anomalia_temperatura_c": "Anomalia térmica",
    "defice_hidrico_3m_z": "Défice hídrico de 3 meses",
    "ln_pib_pc_ppc_ano_anterior": "Log PIB real por habitante (t−1)",
    "peso_agricola_pct_ano_anterior": "Peso agrícola no PIB (t−1)",
    "calor_x_ln_pib": "Calor × log PIB",
    "calor_x_peso_agricola": "Calor × peso agrícola",
}
UNITS = {
    Y: "100 × Δ ln IPC; aprox. %/mês",
    "anomalia_temperatura_c": "°C",
    "defice_hidrico_3m_z": "desvios padrão",
    "ln_pib_pc_ppc_ano_anterior": "log natural",
    "peso_agricola_pct_ano_anterior": "pontos percentuais do PIB",
    "calor_x_ln_pib": "°C × log PIB",
    "calor_x_peso_agricola": "°C × p.p. do PIB",
}
VARS = list(VAR_LABELS)


def pt(value, digits=2):
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", " ")


def configurar():
    installed = {font.name for font in font_manager.fontManager.ttflist}
    font = "Montserrat" if "Montserrat" in installed else "DejaVu Sans"
    plt.rcParams.update(
        {
            "font.family": font,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlecolor": PRETO,
            "text.color": PRETO,
            "axes.labelcolor": CINZA,
            "xtick.color": CINZA,
            "ytick.color": CINZA,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": GRELHA,
            "grid.color": GRELHA,
            "grid.linewidth": 0.7,
            "legend.frameon": False,
            "figure.dpi": 110,
            "savefig.facecolor": "white",
        }
    )
    return font


def dirs(root, etapa):
    tables = root / "resultados" / "tabelas" / etapa
    figures = root / "resultados" / "graficos" / etapa
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    return tables, figures


def tabela(df, titulo, precisao=3, formatos=None):
    formatters = {
        col: (lambda v, p=precisao: pt(v, p))
        for col in df.select_dtypes(include=np.number).columns
    }
    if formatos:
        formatters.update(formatos)
    styles = [
        {
            "selector": "caption",
            "props": [
                ("text-align", "left"),
                ("font-size", "15px"),
                ("font-weight", "bold"),
                ("color", AZUL),
                ("padding", "12px 0"),
            ],
        },
        {
            "selector": "th",
            "props": [
                ("background-color", "white"),
                ("color", PRETO),
                ("border-bottom", f"2px solid {AZUL}"),
                ("padding", "10px 12px"),
                ("text-align", "left"),
            ],
        },
        {
            "selector": "td",
            "props": [
                ("padding", "9px 12px"),
                ("border-bottom", f"1px solid {GRELHA}"),
                ("max-width", "470px"),
                ("white-space", "normal"),
            ],
        },
        {
            "selector": "",
            "props": [
                ("border-collapse", "collapse"),
                ("font-size", "12px"),
                ("font-family", "sans-serif"),
            ],
        },
    ]
    display(
        df.style.set_caption(titulo)
        .format(formatters, na_rep="—")
        .hide(axis="index")
        .set_table_styles(styles)
    )


def csv(df, path, index=False):
    df.to_csv(path, index=index, encoding="utf-8-sig", date_format="%Y-%m-%d")


def eixo(ax, titulo, xlabel, ylabel, zero=False):
    ax.set_title(titulo, loc="left", pad=12)
    ax.set_xlabel(xlabel, labelpad=8)
    ax.set_ylabel(ylabel, labelpad=8)
    ax.grid(axis="y", alpha=0.8)
    ax.set_axisbelow(True)
    if zero:
        ax.axhline(0, color=CINZA, linewidth=0.65, zorder=1)


def cabecalho_fig(fig, numero, titulo, subtitulo):
    fig.suptitle(
        f"{numero}  |  {titulo}",
        x=0.07,
        y=0.99,
        ha="left",
        fontsize=17,
        fontweight="bold",
        color=AZUL,
    )
    altura = fig.get_size_inches()[1]
    posicao_subtitulo = 0.99 - 0.40 / altura
    fig.text(
        0.07,
        posicao_subtitulo,
        subtitulo,
        ha="left",
        va="top",
        fontsize=10,
        color=CINZA,
    )


def salvar(fig, path, nota_texto):
    # Todas as figuras têm notas de leitura e fontes, e exportação vetorial.
    footer = "\n".join(textwrap.wrap(nota_texto, width=155))
    fig.text(
        0.07,
        0.016,
        footer
        + "\nFonte: conjunto fornecido · FAOSTAT, CRU-CY e WDI. Cálculos próprios.",
        fontsize=8,
        color=CINZA,
        va="bottom",
    )
    fig.savefig(path.with_suffix(".png"), dpi=170, bbox_inches="tight")
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    plt.show()
    plt.close(fig)


def mapa(
    ax,
    data,
    titulo,
    xlabel,
    ylabel,
    cbarlabel,
    limites=None,
    divergente=False,
    anotacoes=False,
    fmt=".2f",
):
    cmap = LinearSegmentedColormap.from_list("iscte", [GELO, "#8592E2", AZUL])
    if divergente:
        cmap = LinearSegmentedColormap.from_list("iscte_div", [VERMELHO, "white", AZUL])
    options = {} if limites is None else {"vmin": limites[0], "vmax": limites[1]}
    im = ax.imshow(data.to_numpy(float), aspect="auto", cmap=cmap, **options)
    ax.set_xticks(range(data.shape[1]), labels=data.columns)
    ax.set_yticks(range(data.shape[0]), labels=data.index)
    ax.set(title=titulo, xlabel=xlabel, ylabel=ylabel)
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.03, pad=0.025)
    cbar.set_label(cbarlabel)
    if anotacoes:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                value = float(data.iloc[i, j])
                if np.isfinite(value):
                    ax.text(
                        j,
                        i,
                        format(value, fmt).replace(".", ","),
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="white" if abs(im.norm(value) - 0.5) > 0.31 else PRETO,
                    )
    return im


def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def apresentar_plano(alteracoes):
    """Mostra um índice compacto e apresenta cada proposta num bloco legível."""
    tabela(
        alteracoes[["ID", "Prioridade", "Tema", "Estado"]],
        "Tabela 3.7 · Alterações propostas para a modelação",
    )
    for _, proposta in alteracoes.iterrows():
        display(
            Markdown(
                f"### {proposta['ID']} · {proposta['Tema']}\n\n"
                f"**Evidência:** {proposta['Evidência']}\n\n"
                f"**Alteração proposta:** {proposta['Alteração proposta']}\n\n"
                f"**Como verificar:** {proposta['Como verificar']}"
            )
        )
