"""Modelos comparáveis e sensibilidades; inferência agrupada por país.

Os três modelos de base partilham exatamente X e amostra, sem efeitos de
tempo. Os FE com data e sazonalidade nacional são extensões identificadas
separadamente: não entram no Hausman do modelo de base.
"""
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import RandomEffects
from scipy.stats import chi2, f, t
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller, kpss
from threadpoolctl import threadpool_limits
from preparacao import conferir_campos

Y = "inflacao_alimentar_log_pct"
TERMOS = ["calor", "defice", "agricultura_c", "calor_agricultura"]


def preparar(dados):
    d = dados.sort_values(["pais_iso3", "data"]).reset_index(drop=True).copy()
    conferir_campos(d, [Y, "anomalia_temperatura_c", "defice_hidrico_3m_z",
                       "peso_agricola_pct_ano_anterior", "ln_pib_pc_ppc_ano_anterior"])
    centro = float(d.peso_agricola_pct_ano_anterior.mean())
    d["calor"] = d.anomalia_temperatura_c
    d["defice"] = d.defice_hidrico_3m_z
    d["agricultura_c"] = d.peso_agricola_pct_ano_anterior - centro
    d["calor_agricultura"] = d.calor * d.agricultura_c
    assert not d.duplicated(["pais_iso3", "data"]).any()
    assert d[TERMOS + [Y]].notna().all().all()
    meses = pd.date_range("2000-02-01", "2025-12-01", freq="MS")
    assert d.pais_iso3.nunique() == 15
    for _, grupo in d.groupby("pais_iso3"):
        assert pd.DatetimeIndex(grupo.data).equals(meses), "Cobertura mensal alterada."
    return d, centro


def desenho(d, pais=False, data=False, sazonal=False, tendencias=False):
    """Contrastes explícitos de posto completo, incluindo país × mês.

    Com efeitos de data, o mês comum já está absorvido. Bastam 14 × 11
    contrastes sazonais adicionais (o país de referência tem o perfil comum).
    """
    blocos = [sm.add_constant(d[TERMOS])]
    unidades = pd.get_dummies(d.pais_iso3, prefix="pais", drop_first=True, dtype=float)
    if pais:
        blocos.append(unidades)
    if data:
        blocos.append(pd.get_dummies(d.data, prefix="data", drop_first=True, dtype=float))
    if sazonal:
        assert pais and data
        meses = pd.get_dummies(d.data.dt.month, prefix="mes", drop_first=True, dtype=float)
        blocos.append(pd.DataFrame({f"{a}:{b}": unidades[a] * meses[b]
                                   for a in unidades for b in meses}))
    if tendencias:
        assert pais and data
        tempo = (d.data.dt.year - d.data.dt.year.min()) + (d.data.dt.month - 1) / 12
        blocos.append(unidades.mul(tempo, axis=0).add_prefix("tendencia_"))
    return pd.concat(blocos, axis=1)


def ajustar_ols(d, **efeitos):
    x = desenho(d, **efeitos)
    convencional = sm.OLS(d[Y], x).fit()
    assert convencional.model.rank == x.shape[1], "Desenho não identificado."
    robusto = convencional.get_robustcov_results(
        cov_type="cluster", groups=d.pais_iso3,
        use_correction=True, df_correction=True, use_t=True,
    )
    return {"beta": convencional.params, "cov": pd.DataFrame(robusto.cov_params(), index=x.columns, columns=x.columns),
            "cov_classica": convencional.cov_params(), "resid": convencional.resid,
            "r2": convencional.rsquared, "n": len(d), "k": x.shape[1],
            "sigma2": float(convencional.scale),
            "amostra": pd.MultiIndex.from_frame(d[["pais_iso3", "data"]])}


def ajustar_re(d):
    painel = d.set_index(["pais_iso3", "data"])
    modelo = RandomEffects(painel[Y], sm.add_constant(painel[TERMOS]))
    r = modelo.fit(cov_type="clustered", cluster_entity=True, group_debias=True)
    c = modelo.fit(cov_type="unadjusted")
    return {"beta": r.params, "cov": r.cov, "cov_classica": c.cov,
            "resid": pd.Series(r.resids.to_numpy(), index=d.index),
            "r2": r.rsquared, "n": len(d), "k": len(r.params),
            "sigma2": float(c.s2), "theta": float(r.theta.iloc[0, 0]),
            "variancias": r.variance_decomposition.to_dict(), "amostra": painel.index}


def tabela_coeficientes(modelos, grupos=15):
    linhas = []
    critico = t.ppf(.975, grupos - 1)
    for nome, r in modelos.items():
        for termo in TERMOS:
            beta = float(r["beta"][termo]); ep = float(np.sqrt(r["cov"].loc[termo, termo]))
            linhas.append(dict(modelo=nome, termo=termo, coeficiente=beta, ep_cluster=ep,
                               ic95_inf=beta-critico*ep, ic95_sup=beta+critico*ep,
                               p_cluster_t=2*t.sf(abs(beta/ep), grupos-1), gl_referencia=grupos-1,
                               n=r["n"], grupos=grupos,
                               r2=r["r2"], k=r["k"]))
    return pd.DataFrame(linhas)


def hausman(fe, re):
    """Hausman clássico com variância comum do RE (princípio de sigmamore).

    A normalização resolve a incompatibilidade de escalas em amostra finita;
    não torna o teste robusto a heteroscedasticidade ou autocorrelação.
    """
    if not fe["amostra"].equals(re["amostra"]):
        raise ValueError("Hausman exige os mesmos pares país–data, na mesma ordem.")
    b = (fe["beta"] - re["beta"]).loc[TERMOS].to_numpy()
    v_fe = fe["cov_classica"].loc[TERMOS, TERMOS].to_numpy()
    v_re = re["cov_classica"].loc[TERMOS, TERMOS].to_numpy()
    autovalores_originais = np.linalg.eigvalsh(v_fe - v_re)
    v = re["sigma2"] * (v_fe / fe["sigma2"] - v_re / re["sigma2"])
    v = (v + v.T) / 2
    autovalores = np.linalg.eigvalsh(v)
    try:
        np.linalg.cholesky(v)
        valido = True
    except np.linalg.LinAlgError:
        valido = False
    h = float(b @ np.linalg.solve(v, b)) if valido else None
    return dict(estatistica=h, gl=len(TERMOS), p_valor=float(chi2.sf(h, len(TERMOS))) if valido else None,
                matriz_positiva=valido, autovalores=autovalores.tolist(),
                metodo="Variância comum do RE, sem alterar coeficientes nem regularizar a matriz",
                sigma2_fe=fe["sigma2"], sigma2_re=re["sigma2"],
                autovalores_sem_normalizacao=autovalores_originais.tolist(),
                ressalva="Referência clássica: requer RE eficiente; não é robusta aos padrões residuais observados.")


def testar_mundlak(d):
    """Testa conjuntamente as médias por país dos quatro regressores.

    Inclui a média da interação, que difere do produto das médias. O teste
    usa covariância agrupada e uma referência F aproximada com G−1 gl.
    """
    painel = d.set_index(["pais_iso3", "data"])
    medias = painel[TERMOS].groupby(level=0).transform("mean").add_prefix("media_")
    x = pd.concat([sm.add_constant(painel[TERMOS]), medias], axis=1)
    modelo = RandomEffects(painel[Y], x).fit(
        cov_type="clustered", cluster_entity=True, group_debias=True
    )
    b = modelo.params[medias.columns]
    v = modelo.cov.loc[medias.columns, medias.columns]
    np.linalg.cholesky(v)
    wald = float(b @ np.linalg.solve(v, b))
    q = len(b)
    grupos = d.pais_iso3.nunique()
    ep = np.sqrt(np.diag(v))
    critico = t.ppf(.975, grupos - 1)
    tabela = pd.DataFrame({"termo": b.index, "coeficiente": b.to_numpy(),
                           "ep_cluster": ep, "ic95_inf": b.to_numpy() - critico * ep,
                           "ic95_sup": b.to_numpy() + critico * ep})
    teste = dict(estatistica_f=wald / q, gl_numerador=q, gl_denominador=grupos - 1,
                 p_valor=float(f.sf(wald / q, q, grupos - 1)), wald=wald,
                 n=len(d), grupos=grupos,
                 hipotese="Coeficientes das quatro médias nacionais conjuntamente iguais a zero",
                 ressalva="Teste complementar; F aproximado com 15 grupos, sem correção de dependência transversal.")
    return teste, tabela, modelo.params[TERMOS]


def diagnosticar_residuos(d, modelos):
    linhas, sintese = [], []
    for nome, r in modelos.items():
        a = d[["pais_iso3", "data"]].assign(residuo=np.asarray(r["resid"]))
        for iso, g in a.groupby("pais_iso3"):
            e = g.sort_values("data").residuo
            lb = acorr_ljungbox(e, lags=[12, 24], return_df=True)
            linhas.append(dict(modelo=nome, pais_iso3=iso, dp=e.std(), acf1=e.autocorr(1),
                               acf12=e.autocorr(12), p_lb12=lb.loc[12, "lb_pvalue"],
                               p_lb24=lb.loc[24, "lb_pvalue"]))
        corr = a.pivot(index="data", columns="pais_iso3", values="residuo").corr().to_numpy()
        pares = corr[np.triu_indices_from(corr, 1)]
        dp = a.groupby("pais_iso3").residuo.std()
        sintese.append(dict(modelo=nome, rmse_residual=np.sqrt(np.mean(a.residuo**2)),
                            dp_min=dp.min(), dp_max=dp.max(), razao_dp=dp.max()/dp.min(),
                            correlacao_mediana=np.median(pares), correlacao_abs_mediana=np.median(abs(pares))))
    return pd.DataFrame(linhas), pd.DataFrame(sintese)


def testes_estacionariedade(dados):
    """Covariáveis anuais testadas uma vez por ano, nunca como 311 réplicas."""
    linhas = []
    for iso, g in dados.groupby("pais_iso3"):
        anual = g.sort_values("data").drop_duplicates("ano_dados_economicos")
        for nome, serie, reg, freq in [
            (Y, g.sort_values("data")[Y], "c", "mensal"),
            ("peso_agricola_pct_ano_anterior", anual.peso_agricola_pct_ano_anterior, "ct", "anual"),
            ("ln_pib_pc_ppc_ano_anterior", anual.ln_pib_pc_ppc_ano_anterior, "ct", "anual"),
        ]:
            with warnings.catch_warnings(record=True) as avisos:
                warnings.simplefilter("always")
                adf = adfuller(serie, regression=reg, autolag="AIC", maxlag=3 if freq=="anual" else 12)
                kp = kpss(serie, regression=reg, nlags="auto")
            linhas.append(dict(pais_iso3=iso, variavel=nome, frequencia=freq, n=len(serie),
                               deterministica=reg, adf=adf[0], p_adf=adf[1], lags_adf=adf[2],
                               kpss=kp[0], p_kpss=kp[1], lags_kpss=kp[2],
                               p_kpss_limite=("<" if kp[0] > kp[3]["1%"] else
                                              ">" if kp[0] < kp[3]["10%"] else "="),
                               avisos=" | ".join(str(x.message) for x in avisos)))
    return pd.DataFrame(linhas)


def executar(dados, pasta):
    pasta = Path(pasta); pasta.mkdir(parents=True, exist_ok=True)
    d, centro = preparar(dados)
    with threadpool_limits(limits=1):
        modelos = {"Pooled": ajustar_ols(d), "FE pais": ajustar_ols(d, pais=True), "RE": ajustar_re(d)}
        h = hausman(modelos["FE pais"], modelos["RE"])
        mundlak, medias, beta_mundlak = testar_mundlak(d)
        np.testing.assert_allclose(beta_mundlak, modelos["FE pais"]["beta"][TERMOS], atol=1e-9)
        modelos["FE pais e data"] = ajustar_ols(d, pais=True, data=True)
        modelos["FE pais data sazonal"] = ajustar_ols(d, pais=True, data=True, sazonal=True)
        # Robustez pré-definida: substituir calor corrente pelo lag 1, sem
        # acrescentar um quinto termo. Reestimar o contemporâneo na mesma amostra.
        lag = d.groupby("pais_iso3").calor.shift(1)
        comum = d.loc[lag.notna()].copy().reset_index(drop=True)
        alt = comum.copy(); alt["calor"] = lag.dropna().to_numpy()
        alt["calor_agricultura"] = alt.calor * alt.agricultura_c
        sens = {"Corrente amostra lag": ajustar_ols(comum, pais=True, data=True, sazonal=True),
                "Lag 1 amostra lag": ajustar_ols(alt, pais=True, data=True, sazonal=True)}
        tendencias = ajustar_ols(d, pais=True, data=True, sazonal=True, tendencias=True)
        limitado = d.copy()
        limites = limitado.groupby("pais_iso3")[Y]
        limitado[Y] = limitado[Y].clip(limites.transform(lambda s: s.quantile(.01)),
                                       limites.transform(lambda s: s.quantile(.99)))
        extremos = ajustar_ols(limitado, pais=True, data=True, sazonal=True)
        # Confere que a centragem é apenas reparametrização (modelo de base).
        bruto = d.copy(); bruto["agricultura_c"] += centro
        bruto["calor_agricultura"] = bruto.calor * bruto.agricultura_c
        np.testing.assert_allclose(ajustar_ols(bruto)["resid"], modelos["Pooled"]["resid"], atol=1e-9)
        # Validação independente do FE por transformação within.
        z = d[TERMOS + [Y]] - d.groupby("pais_iso3")[TERMOS + [Y]].transform("mean")
        within = np.linalg.lstsq(z[TERMOS], z[Y], rcond=None)[0]
        np.testing.assert_allclose(within, modelos["FE pais"]["beta"][TERMOS], atol=1e-9)
    coefs = tabela_coeficientes(modelos)
    res, resumo = diagnosticar_residuos(d, modelos)
    for nome, tabela in {"01_coeficientes": coefs, "02_residuos_por_pais": res,
                         "03_resumo_residuos": resumo, "04_sensibilidade_lag": tabela_coeficientes(sens),
                         "05_estacionariedade": testes_estacionariedade(d),
                         "08_robustez": tabela_coeficientes({"FE com tendencias nacionais": tendencias,
                                                            "FE limites 1 e 99": extremos})}.items():
        tabela.to_csv(pasta / f"{nome}.csv", index=False, encoding="utf-8-sig")
    # Efeito marginal do calor em quantis observados, com a covariância conjunta.
    r = modelos["FE pais data sazonal"]; marginais = []
    for q in [.25, .5, .75]:
        a = float(d.peso_agricola_pct_ano_anterior.quantile(q)); v = np.array([1, a-centro])
        idx = ["calor", "calor_agricultura"]
        b = float(v @ r["beta"][idx]); ep = float(np.sqrt(v @ r["cov"].loc[idx, idx] @ v))
        marginais.append(dict(quantil=q, peso_agricola=a, efeito_calor=b,
                               ic95_inf=b-t.ppf(.975,14)*ep, ic95_sup=b+t.ppf(.975,14)*ep))
    pd.DataFrame(marginais).to_csv(pasta / "06_efeitos_marginais.csv", index=False)
    residuos = d[["pais_iso3", "pais", "data"]].copy()
    for nome, resultado in modelos.items():
        residuos[nome] = np.asarray(resultado["resid"])
    residuos.to_csv(pasta / "09_residuos.csv", index=False)
    medias.to_csv(pasta / "10_mundlak.csv", index=False, encoding="utf-8-sig")
    meta = dict(centro_agricultura=centro, n=len(d), grupos=15, meses=311,
                hausman=h, mundlak=mundlak, theta_re=modelos["RE"]["theta"], variancias_re=modelos["RE"]["variancias"],
                validacoes=["centragem preserva previsões", "FE coincide com within", "desenhos de posto completo",
                            "declives do RE aumentado de Mundlak coincidem com FE"],
                comparabilidade="Trio base sem tempo; extensões FE com data e sazonalidade na mesma amostra.")
    (pasta / "07_metadados.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return coefs, res, resumo, meta


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    d = pd.read_csv(raiz / "dados/originais/painel_indicadores.csv", parse_dates=["data"])
    c, _, r, m = executar(d, raiz / "resultados/tabelas/04_modelos")
    print(c.to_string(index=False)); print(r.to_string(index=False)); print(m)
