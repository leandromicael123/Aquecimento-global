"""Figuras compactas em PNG, SVG e PDF, com legendas externas."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

AZUL = "#0D28C2"
TEXTO = "#252525"
CINZA = "#767676"
CLARO = "#C9CDD5"
GRELHA = "#E2E2E2"
BRANCO = "#FFFFFF"
FONTE = "DejaVu Sans"
Y = "inflacao_alimentar_log_pct"


def estilo():
    plt.rcParams.update({"font.family": FONTE, "font.size": 8, "axes.labelsize": 8,
                         "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
                         "text.color": TEXTO, "axes.labelcolor": TEXTO,
                         "xtick.color": TEXTO, "ytick.color": TEXTO,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": CLARO, "grid.color": GRELHA,
                         "grid.linewidth": .5, "legend.frameon": False,
                         "figure.facecolor": BRANCO, "axes.facecolor": BRANCO,
                         "svg.fonttype": "none", "pdf.fonttype": 42})


def guardar(fig, pasta, nome):
    pasta = Path(pasta); pasta.mkdir(parents=True, exist_ok=True)
    for ext in ["png", "svg", "pdf"]:
        fig.savefig(pasta / f"{nome}.{ext}", dpi=300, facecolor=BRANCO)
    plt.close(fig)


def evolucao(dados, pasta):
    s = dados.groupby("data")[Y].mean()
    fig, ax = plt.subplots(figsize=(6.9, 2.55), layout="constrained")
    ax.plot(s.index, s, color=CLARO, linewidth=.7, label="Média mensal dos 15 países")
    ax.plot(s.index, s.rolling(12).mean(), color=AZUL, linewidth=1.4,
            label="Média móvel dos últimos 12 meses")
    ax.axhline(0, color=CINZA, linewidth=.5)
    ax.set(xlabel="Ano", ylabel="Inflação (100 × Δ ln IPC)")
    ax.yaxis.set_major_locator(MaxNLocator(5)); ax.grid(axis="y")
    ax.set_axisbelow(True); ax.legend(loc="upper left")
    guardar(fig, pasta, "01_evolucao")


def variabilidade(dados, pasta):
    cols = [Y, "peso_agricola_pct_ano_anterior", "ln_pib_pc_ppc_ano_anterior"]
    dentro = []
    for c in cols:
        ss = ((dados[c] - dados[c].mean())**2).sum()
        dentro.append(100 * ((dados[c] - dados.groupby("pais_iso3")[c].transform("mean"))**2).sum()/ss)
    dentro = np.array(dentro)
    fig, ax = plt.subplots(figsize=(6.9, 1.85), layout="constrained")
    y = np.arange(3)
    ax.barh(y, dentro, color=AZUL, height=.45, label="Dentro do país")
    ax.barh(y, 100-dentro, left=dentro, color=CLARO, height=.45, label="Entre países")
    for pos, v in enumerate(dentro):
        ax.text(102, pos, f"{v:.2f}% dentro".replace(".", ","), va="center", fontsize=8)
    ax.set_yticks(y, ["Inflação", "Peso agrícola", "Log PIB"])
    ax.set(xlim=(0,130), xlabel="Percentagem da soma de quadrados total")
    ax.set_xticks([0,25,50,75,100]); ax.invert_yaxis()
    ax.legend(loc="lower left", bbox_to_anchor=(0,1.01), ncol=2)
    guardar(fig, pasta, "02_variabilidade")


def coeficientes(coefs, pasta):
    nomes = ["Pooled", "FE pais", "RE", "FE pais e data", "FE pais data sazonal"]
    labels = ["Pooled", "FE país", "RE", "FE país + data", "FE + sazonalidade\nnacional"]
    d = coefs.loc[coefs.termo.eq("calor")].set_index("modelo").loc[nomes]
    fig, ax = plt.subplots(figsize=(3.45, 2.6), layout="constrained")
    for i, r in enumerate(d.itertuples()):
        cor = AZUL if i==4 else CINZA
        ax.errorbar(r.coeficiente, i, xerr=[[r.coeficiente-r.ic95_inf],[r.ic95_sup-r.coeficiente]],
                    fmt="o", color=cor, markersize=3, capsize=2, linewidth=1)
    ax.axvline(0, color=TEXTO, linewidth=.6)
    ax.set_yticks(range(5), labels); ax.invert_yaxis()
    ax.set_xlabel("Inflação por +1 °C\n(p.p. aprox./mês)")
    ax.xaxis.set_major_locator(MaxNLocator(4)); ax.grid(axis="x"); ax.set_axisbelow(True)
    guardar(fig, pasta, "03_calor_modelos")


def residuos(residuos, pasta):
    dados = residuos.sort_values(["pais_iso3", "data"])
    modelos = ["FE pais e data", "FE pais data sazonal"]
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.65), layout="constrained")
    for nome, cor, ls in zip(modelos, [CINZA, AZUL], ["--", "-"]):
        acf = [[g[nome].autocorr(lag) for _,g in dados.groupby("pais_iso3")] for lag in range(1,25)]
        med = np.median(np.abs(acf), axis=1)
        axes[0].plot(range(1,25), med, color=cor, linestyle=ls,
                     label="Com sazonalidade nacional" if nome==modelos[1] else "País + data", linewidth=1.2)
        dp = dados.groupby("pais_iso3")[nome].std().sort_values().to_numpy()
        axes[1].plot(range(1,16), dp, color=cor, linestyle=ls, linewidth=1.2)
    axes[0].set(xlabel="Desfasamento (meses)", ylabel="Mediana de |ACF residual|", xticks=[1,6,12,18,24])
    axes[1].set(xlabel="Países ordenados pelo DP (em cada modelo)", ylabel="DP residual (p.p. aprox.)", xticks=[1,5,10,15], ylim=(0,None))
    for ax in axes:
        ax.grid(axis="y"); ax.yaxis.set_major_locator(MaxNLocator(4)); ax.set_axisbelow(True)
    axes[0].legend(loc="upper left", bbox_to_anchor=(0,1.2), ncol=2)
    guardar(fig, pasta, "04_residuos")


def sensibilidade(lag, robustez, coefs, pasta):
    frames = [coefs[coefs.modelo.eq("FE pais data sazonal")], lag, robustez]
    d = pd.concat(frames).query("termo == 'calor'")
    labels = ["Contemporâneo (n=4665)", "Contemporâneo (n=4650)", "Desfasado 1 mês (n=4650)",
              "Tendências por país", "Limites nos quantis 1%/99%"]
    fig, ax = plt.subplots(figsize=(6.9, 2.55), layout="constrained")
    for i, r in enumerate(d.itertuples()):
        ax.errorbar(r.coeficiente, i, xerr=[[r.coeficiente-r.ic95_inf],[r.ic95_sup-r.coeficiente]],
                    fmt="o", color=AZUL if i==2 else CINZA, markersize=4, capsize=2)
    ax.set_yticks(range(len(d)), labels); ax.invert_yaxis()
    ax.axvline(0, color=TEXTO, linewidth=.6); ax.grid(axis="x"); ax.set_axisbelow(True)
    ax.set_xlabel("Associação com +1 °C ao peso agrícola médio (p.p. aproximados de inflação mensal)")
    guardar(fig, pasta, "05_sensibilidade")


def executar(dados, tabelas, pasta):
    estilo(); tabelas = Path(tabelas)
    c = pd.read_csv(tabelas/"01_coeficientes.csv")
    evolucao(dados, pasta); variabilidade(dados, pasta); coeficientes(c, pasta)
    residuos(pd.read_csv(tabelas/"09_residuos.csv"), pasta)
    sensibilidade(pd.read_csv(tabelas/"04_sensibilidade_lag.csv"),
                  pd.read_csv(tabelas/"08_robustez.csv"), c, pasta)
