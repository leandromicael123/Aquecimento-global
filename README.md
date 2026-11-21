# Clima e inflação alimentar

Trabalho de grupo de Modelos Longitudinais. A Parte 1 prepara, explora e modeliza um painel mensal de 15 países, de fevereiro de 2000 a dezembro de 2025, com pooled OLS, efeitos fixos, efeitos aleatórios e avaliação dos resíduos. A Parte 2 modeliza com SARIMA a inflação alimentar mensal do Níger e avalia as previsões para 2025.

## Ler o trabalho

Começar pelas sínteses da [Parte 1](relatorio/parte1.md) e da [Parte 2](relatorio/parte2.md). Apresentam o problema, os dados, os modelos, os resultados e as limitações sem exigir leitura do código.

Os cálculos estão em seis notebooks, que podem ser executados individualmente:

1. [Preparação e qualidade](notebooks/01_preparacao_e_qualidade.ipynb): questões, fontes, unidades, cobertura, omissos, extremos e reprodução dos indicadores.
2. [Exploração](notebooks/02_exploracao_visual.ipynb): trajetórias, distribuições, períodos e variação dentro e entre países.
3. [Diagnósticos exploratórios](notebooks/03_diagnosticos_e_alteracoes.ipynb): sazonalidade, dependência, choques comuns e decisões que fundamentam os modelos.
4. [Modelos e interpretação](notebooks/04_modelos_painel.ipynb): estimação, comparação, resíduos, estacionariedade, sensibilidades e respostas às questões.
5. [Seleção e diagnóstico da série](notebooks/05_sarima_diagnostico.ipynb): escolha do Níger, divisão treino/teste, sazonalidade, ACF/PACF, ADF e KPSS (secção 4.1 do guião).
6. [Estimação, comparação e previsão](notebooks/06_sarima_estimacao_previsao.ipynb): candidatos SARIMA, validação com origem móvel, resíduos e previsões de 2025 (secções 4.2 e 4.3).

O resultado principal é sensível ao calendário: a associação contemporânea da temperatura, ao peso agrícola médio, tem IC 95% que inclui zero após controlar a sazonalidade nacional. A versão com temperatura do mês anterior apresenta uma associação positiva. O notebook 04 discute ambos os resultados, incluindo os limites da inferência com 15 países e da interpretação causal.

Na Parte 2, o modelo final é o SARIMA(0,0,0)(0,1,1)₁₂, escolhido só com o treino. Na validação de 2015–2024 erra menos do que o ARIMA sem componente sazonal e do que as referências simples. Em 2025, um ano que fugiu ao padrão sazonal, só supera a referência ingénua sazonal: RMSE de 3,632, contra 4,609 do ingénuo sazonal e 3,229 do ARIMA.

## Executar

Python 3.12. No PowerShell, a partir desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\verificar_reproducao.py
.\.venv\Scripts\python.exe scripts\reexecutar.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Em Linux/macOS, usar `.venv/bin/python` em vez do caminho Windows. O executor utiliza o Python ativo para os kernels, evitando executar os notebooks num ambiente global diferente.

O primeiro script verifica os 51 hashes das fontes, reconstrói os indicadores offline e compara-os com as entradas originais. O segundo executa todos os notebooks da pasta `notebooks/`, atualiza tabelas/figuras/síntese e grava [o registo de execução](resultados/verificacao_execucao.json). Não é necessária ligação à Internet depois de instalar as dependências: os notebooks 05 e 06 também leem o painel guardado em `dados/processados/`.

O registo de execução atual é de 12/11/2026 e cobre os notebooks 01 a 04. Os notebooks 05 e 06 foram executados de raiz a 20 e 21/11/2026, com as versões de bibliotecas do `requirements.txt` (em Python 3.13). Antes da entrega, correr de novo o executor para o registo incluir os seis notebooks.

A [auditoria do código](docs/auditoria_codigo.md) documenta a lista de erros comuns, as correções e os testes. O notebook 04 inclui a sensibilidade de Driscoll–Kraay e a retirada de um país de cada vez. O registo distingue execução em curso, concluída ou falhada e identifica as versões dos scripts por hash.

## Organização

```text
dados/originais/       Entradas da análise, preservadas
dados/reproducao/      Script de construção, arquivos de origem e normais climáticas
dados/processados/    Painel ordenado
dados/modelacao/      Amostras preparadas
notebooks/            01–04: Parte 1; 05–06: Parte 2
scripts/              Funções de preparação, análise, gráficos e execução
resultados/tabelas/   CSV sem arredondamentos de apresentação, por etapa
resultados/graficos/  Figuras exploratórias e versões compactas
relatorio/            Sínteses autónomas das Partes 1 e 2
docs/                 Decisões, cobertura do guião e registo do apoio de IA
```

A pasta [de reprodução](dados/reproducao/PROVENIENCIA.md) contém o pacote recuperado cujo painel coincide com a entrada. `metodologia_original.txt` descreve esse pacote histórico; o estado atual do trabalho é o documentado aqui.

## Convenções de análise

- A inflação é `100 × Δln(IPC)`, aproximadamente percentual por mês; não é a taxa homóloga.
- A especificação principal tem temperatura, défice hídrico, agricultura centrada e interação. O log PIB permanece na exploração.
- As variáveis económicas são anuais, do ano anterior e repetidas nos meses, sem interpolação. Os testes dessas variáveis usam uma observação por ano.
- O trio pooled/FE país/RE partilha covariáveis, amostra e ausência de efeitos de tempo. As extensões FE acrescentam data e sazonalidade nacional na mesma amostra.
- Os IC usam erros agrupados por país e t(14). O R² RE refere-se à regressão GLS transformada, ao contrário do R² OLS; não são diretamente comparáveis.
- Os resíduos RE guardados pela biblioteca pertencem à transformação GLS. O seu RMSE não é usado como uma medida diretamente comparável ao RMSE OLS.
- O Hausman usa variância comum do RE: χ²(4)=10,466 e p=0,0333. A dificuldade da subtração sem normalização está documentada. Um teste complementar de Mundlak com EP agrupados dá F(4,14)=5,730 e p=0,0060; a inferência com 15 grupos continua aproximada.
- Nenhum extremo é retirado da análise principal. A limitação nos quantis é apenas sensibilidade numa cópia dos dados.
- As figuras compactas em `resultados/graficos/04_modelos/` têm versões PNG a 300 dpi, SVG e PDF. Títulos, fontes e notas ficam no texto, permitindo inserção no relatório.
- Parte 2: série do Níger (`NER`), com treino de fevereiro de 2000 a dezembro de 2024 e teste de janeiro a dezembro de 2025 (coluna `amostra_temporal`). As escolhas usam só o treino; 2025 só entra depois de fixado o modelo.
- Os AIC e BIC só se comparam entre modelos com a mesma diferenciação. D = 0 e D = 1 comparam-se pela validação com origem móvel dentro do treino.
- Erro de previsão = observado − previsto. MAE e RMSE estão em pontos percentuais por mês, na escala da resposta; não há transformação inversa.
- As figuras `01_validacao_rmse_por_janela` e `03_previsao_2025` de `resultados/graficos/06_sarima/` têm versões PNG a 300 ppp e PDF, sem título dentro da imagem, para o relatório.

As interpretações referem-se à versão dos dados aqui guardada. Se a entrada for substituída, os números são recalculados, mas o texto interpretativo dos notebooks deve ser revisto. As validações que fixam a dimensão esperada também devem ser reavaliadas.

## Âmbito e entrega

As matrizes de cobertura da [Parte 1](docs/cobertura_parte1.md) e da [Parte 2](docs/cobertura_parte2.md) ligam cada requisito do guião ao respetivo resultado. As [decisões](docs/decisoes_parte1.md) explicam como o feedback da Parte 1 foi aplicado; o [registo de IA](docs/uso_ia.md) documenta o apoio de IA conhecido.

O relatório final conjunto de quatro páginas, em LaTeX, ainda não foi produzido. O grupo ainda precisa de confirmar o registo no Excel (incluindo o Níger como país da Parte 2), a identificação dos membros e a declaração completa de IA. A Parte 2 usa o Níger: `portugal_sarima.csv` e a exploração de Portugal com 2025 vêm do plano inicial e não servem para escolher modelos de previsão.
