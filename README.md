# Clima e inflação alimentar

Parte 1 do trabalho de Modelos Longitudinais: preparação, exploração e modelização de um painel mensal de 15 países, de fevereiro de 2000 a dezembro de 2025. Inclui pooled OLS, efeitos fixos, efeitos aleatórios e avaliação dos resíduos.

## Ler o trabalho

Começar pela [síntese da Parte 1](relatorio/parte1.md). Apresenta o problema, os dados, os modelos, os resultados e as limitações sem exigir leitura do código.

Os cálculos estão em quatro notebooks, que podem ser executados individualmente:

1. [Preparação e qualidade](notebooks/01_preparacao_e_qualidade.ipynb): questões, fontes, unidades, cobertura, omissos, extremos e reprodução dos indicadores.
2. [Exploração](notebooks/02_exploracao_visual.ipynb): trajetórias, distribuições, períodos e variação dentro e entre países.
3. [Diagnósticos exploratórios](notebooks/03_diagnosticos_e_alteracoes.ipynb): sazonalidade, dependência, choques comuns e decisões que fundamentam os modelos.
4. [Modelos e interpretação](notebooks/04_modelos_painel.ipynb): estimação, comparação, resíduos, estacionariedade, sensibilidades e respostas às questões.

O resultado principal é sensível ao calendário: a associação contemporânea da temperatura, ao peso agrícola médio, tem IC 95% que inclui zero após controlar a sazonalidade nacional. A versão com temperatura do mês anterior apresenta uma associação positiva. O notebook discute ambos os resultados, incluindo os limites da inferência com 15 países e da interpretação causal.

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

O primeiro script verifica os 51 hashes das fontes, reconstrói os indicadores offline e compara-os com as entradas originais. O segundo executa os quatro notebooks, atualiza tabelas/figuras/síntese e grava [o registo de execução](resultados/verificacao_execucao.json). Não é necessária ligação à Internet depois de instalar as dependências.

A [auditoria do código](docs/auditoria_codigo.md) documenta a lista de erros comuns, as correções e os testes. O notebook 04 inclui a sensibilidade de Driscoll–Kraay e a retirada de um país de cada vez. O registo distingue execução em curso, concluída ou falhada e identifica as versões dos scripts por hash.

## Organização

```text
dados/originais/       Entradas da análise, preservadas
dados/reproducao/      Script de construção, arquivos de origem e normais climáticas
dados/processados/    Painel ordenado
dados/modelacao/      Amostras preparadas
notebooks/            Quatro etapas da Parte 1
scripts/              Funções de preparação, análise, gráficos e execução
resultados/tabelas/   CSV sem arredondamentos de apresentação, por etapa
resultados/graficos/  Figuras exploratórias e versões compactas
relatorio/parte1.md   Síntese autónoma da Parte 1
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

As interpretações referem-se à versão dos dados aqui guardada. Se a entrada for substituída, os números são recalculados, mas o texto interpretativo dos notebooks deve ser revisto. As validações que fixam a dimensão esperada também devem ser reavaliadas.

## Âmbito e entrega

A [matriz de cobertura](docs/cobertura_parte1.md) liga cada requisito das secções 3.1–3.3 ao respetivo resultado. As [decisões](docs/decisoes_parte1.md) explicam como o feedback foi aplicado; o [registo de IA](docs/uso_ia.md) documenta o apoio conhecido nesta revisão.

A Parte 2 (SARIMA) e o relatório final conjunto de quatro páginas não foram produzidos nesta revisão da Parte 1. O grupo ainda precisa de confirmar o registo no Excel, a identificação dos membros e a declaração completa de IA. Não se deve utilizar a exploração de Portugal que inclui 2025 para selecionar modelos de previsão.
