# Cobertura da Parte 2

Referência: secção 4 do guião do trabalho de grupo (Modelos Longitudinais, 2026/2027).

| Requisito | Onde está resolvido |
|---|---|
| 4.1.1 País e resposta da Parte 1; série ordenada e regular; justificação do país | Notebook 05: série do Níger (311 meses, frequência mensal, sem duplicados nem omissos) e comparação dos 15 países no treino |
| 4.1.2 Gráfico da série; tendência, sazonalidade, extremos e alterações de comportamento | Notebook 05: figuras `01` a `03` de `resultados/graficos/05_sarima/` e respetiva leitura |
| 4.1.3 Últimos 12 meses para teste, fora da escolha dos modelos; validação dentro do treino | Notebooks 05 e 06: treino de fevereiro de 2000 a dezembro de 2024, teste de 2025; validação com origem móvel em 2015–2024 |
| 4.1.4 Transformação e diferenciação com gráficos, ACF/PACF e testes, só no treino | Notebook 05: ACF/PACF, ADF e KPSS antes e depois da diferença sazonal; d = 0, D = 1, s = 12 |
| 4.2.1 Conjunto pequeno de especificações justificadas; AIC/BIC e resíduos | Notebook 06, secção 4.2.1: M1 a M6; `01_candidatos.csv` e `02_coeficientes.csv` |
| 4.2.2 Resíduos do modelo selecionado: ACF e Ljung–Box com lags e graus de liberdade adequados; normalidade sem decidir sozinha | Notebook 06, secção 4.2.2: Ljung–Box nos lags 12, 24 e 36 com lag − 1 graus de liberdade, Jarque–Bera, teste H, desvio padrão anual e figura `02_diagnostico_residuos_M1` |
| 4.2.3 Referência ingénua sazonal | Notebook 06: validação de 2015–2024 e teste de 2025 |
| 4.2.4 ARIMA sem componente sazonal; sazonalidade sustentada pelos dados | Notebook 06: M6, ARIMA(1,0,0), grelha p, q ≤ 2 em `03_grelha_arima.csv` e Ljung–Box dos resíduos |
| 4.2 Especificação SARIMA sazonal discutida; teste não usado para escolher | Notebook 06: modelo final fixado no fim da secção 4.2, antes de usar 2025 |
| 4.3 Previsões a partir do fim do treino, com o mesmo horizonte para todos os métodos | Notebook 06: `08_previsoes_2025.csv` |
| 4.3 MAE e RMSE no teste; gráfico com observados, previsões e intervalo de 95% | `09_metricas_teste.csv`; figura `03_previsao_2025` |
| 4.3 Métricas na escala original; transformação inversa | Notebook 06, secção 4.3: a resposta não foi transformada e o SARIMAX devolve as previsões na escala da resposta |
| 4.3 SARIMA face à referência; períodos com maiores erros e relação com a informação disponível | Notebook 06: `10_erros_mensais_M1.csv` e leitura dos erros |
| Questões orientadoras e ligação entre as partes | Notebook 06, «Respostas às questões do guião»; `relatorio/parte2.md` |
| Notebook comentado e executável sem erros; dados e versões | Notebooks 05 e 06 leem `dados/processados/painel_longo.csv`, sem Internet; versões em `requirements.txt` |

O guião exige ainda o relatório final em LaTeX, com as duas partes nas mesmas secções e quatro páginas de conteúdo principal, o registo no Excel com o Níger como país da análise SARIMA e a declaração de uso de IA completa. Estes elementos não estão neste ramo.
