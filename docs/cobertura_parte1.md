# Cobertura da Parte 1

Referência: secções 3.1–3.3 de `Trabalho_Grupo_Modelos_Longitudinais (9).pdf`.

| Requisito | Onde está resolvido |
|---|---|
| 3.1.1 Questões e justificação das variáveis | Notebook 01, secção 1; síntese, secção 1 |
| 3.1.2 Formato longo e ausência de duplicados | Notebook 01, cobertura e verificações da chave |
| 3.1.3 Unidades, frequência, dimensão e equilíbrio | Notebook 01, Tabelas 1.1–1.2 |
| 3.1.4 Omissos, extremos e transformações | Notebook 01; notebook 03, extremos; dados originais preservados |
| 3.1.5 Descritivas, trajetórias, entre/dentro | Notebook 02; Figuras 1–2 da síntese |
| 3.2.1 Pooled OLS | Notebook 04, Tabela 4.1 |
| 3.2.2 FE país e consideração dos efeitos de tempo | Notebook 04, Tabelas 4.1–4.2; data e sazonalidade nacional |
| 3.2.3 RE e hipótese de não correlação | Notebook 04, secções 1–2 |
| 3.2 Mesmas covariáveis/amostra e papel dos efeitos | Notebook 04, secção 1; modelos de base e extensões identificados separadamente |
| 3.3 Coeficientes, IC/EP, n e ajustamento | Tabelas 4.1–4.2; `01_coeficientes.csv` contém EP e IC |
| 3.3 Sinal, magnitude, unidades, interpretação within | Notebook 04, secções 1 e 4; efeitos marginais com covariância conjunta |
| 3.3 Heteroscedasticidade e dependência temporal residual | Notebook 04, secção 6; DP nacional, ACF e Ljung–Box 12/24 |
| 3.3 EP robustos, poucos grupos e dependência transversal | Notebook 04, secção 6; limitações explícitas |
| 3.3 Escolha por hipóteses; Hausman se aplicável | Notebook 04, secções 3 e 5; Hausman com variância comum e Mundlak complementar agrupado, com ressalvas |
| 3.3 Tendências, não estacionariedade, transformação | Notebook 04, secções 7–8; ADF/KPSS à frequência correta e tendências nacionais |
| 3.3 Associação vs causalidade e omitidas | Notebook 04, secção 9; síntese, secção 7 |
| Dados e instruções de reprodução | `dados/reproducao/`; `scripts/verificar_reproducao.py` |
| Código executável e resultados guardados | `scripts/reexecutar.py`; `resultados/verificacao_execucao.json` |
| Auditoria de erros comuns e verificações adicionais | `docs/auditoria_codigo.md`; 12 testes; notebook 04, secção 8.1 |

O guião exige também a Parte 2 e um relatório final que integre as duas partes. A conclusão da Parte 1 não equivale à conclusão dessa entrega conjunta. Os elementos administrativos por confirmar estão indicados em `decisoes_parte1.md`.
