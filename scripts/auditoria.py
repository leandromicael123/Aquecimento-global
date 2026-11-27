"""Verificações adicionais de identificação, influência e inferência do FE."""
from pathlib import Path
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t
from statsmodels.stats.sandwich_covariance import cov_nw_groupsum, cov_cluster
from threadpoolctl import threadpool_limits

from modelos_painel import preparar, desenho, ajustar_ols, TERMOS, Y


def executar(dados, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    d, centro = preparar(dados)
    lag = d.groupby("pais_iso3").calor.shift(1)
    anterior = d.loc[lag.notna()].copy().reset_index(drop=True)
    anterior["calor"] = lag.dropna().to_numpy()
    anterior["calor_agricultura"] = anterior.calor * anterior.agricultura_c
    inferencia, influencia = [], []
    verificacoes = {}

    with threadpool_limits(limits=1):
        for nome, amostra in [("Contemporaneo", d), ("Lag 1", anterior)]:
            x = desenho(amostra, pais=True, data=True, sazonal=True)
            modelo = sm.OLS(amostra[Y], x).fit()
            assert modelo.model.rank == x.shape[1]
            tempo = pd.factorize(amostra.data, sort=True)[0]
            n_datas = amostra.data.nunique()
            # Com lag zero, DK deve coincidir com a covariância agrupada por
            # data, usando a mesma correção N/(N−K).
            cov_zero = cov_nw_groupsum(modelo, 0, tempo, use_correction="hac")
            cov_data = cov_cluster(modelo, tempo, use_correction=False)
            np.testing.assert_allclose(cov_zero, cov_data * len(x) / modelo.df_resid,
                                       atol=1e-9, rtol=1e-8)
            for largura in [12, 24]:
                cov = cov_nw_groupsum(modelo, largura, tempo, use_correction="hac")
                for termo in TERMOS:
                    pos = x.columns.get_loc(termo)
                    b = float(modelo.params[termo])
                    ep = float(np.sqrt(cov[pos, pos]))
                    critico = t.ppf(.975, n_datas - 1)
                    inferencia.append(dict(modelo=nome, metodo="Driscoll-Kraay", largura=largura,
                                           termo=termo, coeficiente=b, ep=ep,
                                           ic95_inf=b - critico * ep, ic95_sup=b + critico * ep,
                                           p_aproximado=2 * t.sf(abs(b / ep), n_datas - 1),
                                           gl_referencia=n_datas - 1, n=len(x)))

            if nome == "Contemporaneo":
                # Verificação independente: retirar apenas os controlos e
                # estimar a regressão nas variáveis residualizadas (FWL).
                controles = x.drop(columns=TERMOS).to_numpy()
                variaveis = amostra[TERMOS + [Y]].to_numpy()
                residuos = variaveis - controles @ np.linalg.lstsq(controles, variaveis, rcond=None)[0]
                beta = np.linalg.lstsq(residuos[:, :-1], residuos[:, -1], rcond=None)[0]
                np.testing.assert_allclose(beta, modelo.params[TERMOS], atol=1e-9)
                padronizadas = residuos[:, :-1] / residuos[:, :-1].std(axis=0)
                verificacoes["condicao_regressores_apos_controlos"] = float(np.linalg.cond(padronizadas))
                verificacoes["erro_maximo_fwl"] = float(np.max(abs(beta - modelo.params[TERMOS])))

            for iso in amostra.pais_iso3.unique():
                sub = amostra.loc[amostra.pais_iso3.ne(iso)].reset_index(drop=True)
                r = ajustar_ols(sub, pais=True, data=True, sazonal=True)
                # Mantém-se o centro original para comparar o efeito no
                # mesmo peso agrícola, apesar de retirar um país.
                for termo in TERMOS:
                    b = float(r["beta"][termo])
                    ep = float(np.sqrt(r["cov"].loc[termo, termo]))
                    influencia.append(dict(modelo=nome, pais_retirado=iso, termo=termo,
                                            coeficiente=b, ep_cluster=ep, grupos=14,
                                            ic95_inf=b-t.ppf(.975,13)*ep,
                                            ic95_sup=b+t.ppf(.975,13)*ep))

    pd.DataFrame(inferencia).to_csv(pasta / "11_inferencia_dk.csv", index=False)
    pd.DataFrame(influencia).to_csv(pasta / "12_influencia_paises.csv", index=False)
    verificacoes.update(centro_agricultura=centro, janelas_dk=[12, 24],
                        fwl_confere=True, dk_lag_zero_confere=True,
                        ressalva="Sensibilidades; DK requer dimensão temporal longa. Nenhum método garante inferência exata.")
    (pasta / "13_auditoria_numerica.json").write_text(
        json.dumps(verificacoes, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return pd.DataFrame(inferencia), pd.DataFrame(influencia), verificacoes


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    d = pd.read_csv(raiz / "dados/originais/painel_indicadores.csv", parse_dates=["data"])
    a, b, v = executar(d, raiz / "resultados/tabelas/04_modelos")
    print(a[a.termo.eq("calor")].to_string(index=False))
    print(b[b.termo.eq("calor")].groupby("modelo").coeficiente.agg(["min", "max"]))
    print(v)
