# Aquecimento global e inflação alimentar — dataset 2000–2025

## Ficheiro principal

`painel_indicadores.csv` contém 4 665 observações, 15 países e 311 meses por país, de fevereiro de 2000 a dezembro de 2025. Uma linha representa um país num mês. Chave única: `pais_iso3` + `data`.

Os dados de origem têm 312 meses, janeiro de 2000 a dezembro de 2025. Janeiro de 2000 é necessário para calcular a inflação de fevereiro. Esse mês inicial só aparece nos dados de origem, porque o arquivo FAOSTAT utilizado começa em janeiro de 2000 e não permite calcular a primeira variação sem uma fonte anterior.

CSV em UTF-8 com BOM, separador vírgula e ponto decimal. Datas no formato AAAA-MM-DD. Os valores numéricos mantêm a precisão dos cálculos. O Excel pode mostrar menos casas decimais, sem alterar os valores guardados. O ficheiro Excel é uma fotografia dos dados calculados em Python; o código incluído reproduz os CSV.

## Conteúdo

- `painel_indicadores.csv`: resposta, explicativas, interações e identificadores.
- `dados_brutos_mensais.csv`: 4 680 registos com IPC alimentar e clima publicado em 2000–2025.
- `dados_brutos_anuais.csv`: 390 registos, 15 países × 26 anos, com PIB real por habitante em PPC e peso agrícola de 1999–2024.
- `clima_historico_mensal.csv`: 22 500 registos de clima, de 1901 a 2025, para reproduzir os indicadores e a referência histórica.
- `normais_climaticas_1991_2020.csv`: 180 referências, uma por país e mês do calendário.
- `portugal_sarima.csv`: a mesma resposta do painel para Portugal, com 299 meses de treino e 12 meses de teste.
- `paises.csv`: nomes, códigos e grupos atuais de rendimento.
- `dicionario_variaveis.csv`: significado, unidade, papel, regra de cálculo e fonte de cada coluna.
- `fontes.csv` e `manifesto_fontes.json`: ligações exatas, versões, datas de recolha e SHA-256 dos arquivos originais.
- `fontes_originais/`: cópias dos arquivos descarregados, sem alterações.
- `construir_dataset.py`: reprodução dos dados e indicadores sem novas consultas à Internet.
- `verificacao_dataset.json`: dimensão, omissos, duplicados e conferências independentes dos cálculos.

## Dados brutos e indicadores

“Dados brutos” designa as séries publicadas antes das transformações deste trabalho. Incluem índices e médias já calculados pelas entidades produtoras. Os indicadores finais são derivados dessas séries ou usam o valor económico do ano anterior.

1. Inflação alimentar mensal = 100 × [ln(IPC_t) − ln(IPC_t−1)]. É uma taxa logarítmica mensal, aproximadamente percentual. Não é a taxa homóloga disponibilizada pela FAO nem exatamente 100 × (IPC_t/IPC_t−1 − 1). O código não aplica ajuste sazonal às séries recolhidas.
2. Anomalia térmica = temperatura média do mês − média 1991–2020 do mesmo país e mês do calendário. Um valor positivo significa um mês mais quente do que essa referência.
3. PET mensal = PET em mm/dia × número de dias do mês, incluindo anos bissextos.
4. Balanço hídrico mensal = precipitação − PET mensal. Balanço de três meses B3_t = balanço_t + balanço_t−1 + balanço_t−2. Usa-se uma janela retrospetiva, sem meses futuros.
5. Défice hídrico = [média histórica de B3 − B3_t] / desvio padrão amostral histórico de B3. A referência de 1991–2020 é calculada separadamente para cada país e mês do calendário, com 30 valores e ddof=1. Valores positivos indicam condições mais secas; valores negativos indicam condições mais húmidas. Este indicador não é SPEI, humidade observada do solo nem medida direta de perdas agrícolas.
6. PIB e peso agrícola: utiliza-se o ano t−1 em todos os meses do ano t. Estes valores continuam a ser anuais. Não houve interpolação nem criação de medições económicas mensais. O desfasamento não garante, por si só, que o dado já estivesse publicado em tempo real.
7. Interações = anomalia de temperatura × logaritmo do PIB do ano anterior, ou × peso agrícola do ano anterior. Os produtos são calculados sem centrar ou padronizar as variáveis económicas. O peso agrícola está em pontos percentuais: 5 representa 5% do PIB.

## Modelos previstos

Resposta comum: `inflacao_alimentar_log_pct`.

- Especificação desenvolvimento: `anomalia_temperatura_c`, `defice_hidrico_3m_z`, `ln_pib_pc_ppc_ano_anterior`, `calor_x_ln_pib`.
- Especificação agricultura: `anomalia_temperatura_c`, `defice_hidrico_3m_z`, `peso_agricola_pct_ano_anterior`, `calor_x_peso_agricola`.

Cada especificação tem quatro termos explicativos. Comparar pooled OLS, efeitos fixos e efeitos aleatórios com a mesma amostra e covariáveis dentro de cada especificação. A seleção e estimação dos modelos não foram realizadas neste pacote.

## Portugal e previsão

Extrair Portugal da coluna `pais_iso3` ou usar `portugal_sarima.csv`. Treino: fevereiro de 2000 a dezembro de 2024 (299 meses). Teste: janeiro a dezembro de 2025 (12 meses). Ajustar e escolher modelos apenas com o treino. Comparar SARIMA com ARIMA e previsão ingénua sazonal, a partir do final do treino, com o mesmo horizonte. A coluna `amostra_temporal` define essa separação em todos os países; o país escolhido para o exercício é Portugal.

Exemplo em Python:

```python
import pandas as pd

df = pd.read_csv('painel_indicadores.csv', parse_dates=['data'])
pt = df.loc[df['pais_iso3'].eq('PRT')].set_index('data').sort_index()
y_treino = pt.loc[:'2024-12-01', 'inflacao_alimentar_log_pct'].asfreq('MS')
y_teste = pt.loc['2025-01-01':, 'inflacao_alimentar_log_pct'].asfreq('MS')
```

## Qualidade e limites

O painel final não tem valores omissos nem pares país–mês duplicados. Nenhum valor foi substituído por zero, winsorizado, removido por ser extremo ou imputado por este código. Há conferências independentes para inflação, anomalia térmica e défice hídrico em quatro casos, incluindo fevereiro de anos bissextos.

Os sinalizadores da FAO nesta seleção mensal são A (Official value) e X (Value from external organization). Não existem I (imputado por uma agência recetora), E (estimado) ou L nesta seleção. A/X não certificam ausência de estimativas, imputações ou quebras nas fontes originais a montante. O arquivo FAOSTAT completo incluído contém também outros países e outros sinalizadores; o código seleciona apenas os 15 países e a série alimentar definida.

CRU-CY usa médias nacionais ponderadas pela área, derivadas de dados climáticos em grelha. O CRU prioriza cobertura completa e pode usar a climatologia de 1961–1990 em células sem observações. Ausência de omissos não significa igual cobertura de estações ou igual precisão. As médias nacionais também ocultam diferenças regionais. A PET depende das condições térmicas, pelo que a sua relação com a anomalia de temperatura deve ser considerada.

As séries de IPC podem ter mudanças de cabaz, cobertura e metodologia. O grupo de rendimento é o atual, ano fiscal 2027, e não uma classificação histórica para 2000–2025. A amostra não é representativa de todos os países e concentra países de baixo rendimento em África. O PIB real por habitante não mede diretamente pobreza, desigualdade nem rendimento disponível das famílias. Os dados são observacionais; a análise deverá discutir sazonalidade, tendências, quebras, choques comuns e fatores omitidos.

Os dados correspondem às versões recolhidas em outubro de 2026. A avaliação de 2025 é um exercício retrospetivo com dados revistos, não uma reprodução das versões disponíveis em tempo real.

## Reprodução

Na pasta do pacote, com pandas e numpy instalados:

```bash
python construir_dataset.py
```

O script usa somente as fontes guardadas e volta a criar os CSV e o relatório de verificação. As versões de Python, pandas e numpy utilizadas constam de `verificacao_dataset.json`. As fontes de origem mantêm as condições de utilização e atribuição das entidades produtoras. Para CRU, citar CRU-CY v4.10 e Harris et al. (2020), Scientific Data 7, 109, https://doi.org/10.1038/s41597-020-0453-3. Para FAOSTAT e Banco Mundial, identificar os conjuntos e indicadores indicados no dicionário e em fontes.csv.
