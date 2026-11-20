# Decisões da Parte 1

Versão revista em 11–12 de novembro de 2026, com base no feedback de 7 de novembro e no guião `Trabalho_Grupo_Modelos_Longitudinais (9).pdf`.

| Ponto do feedback | Decisão aplicada | Evidência |
|---|---|---|
| Versão do trabalho | Continuar o painel de inflação alimentar existente nesta pasta | Notebooks 01–04 |
| Uma especificação principal | Temperatura, défice hídrico, agricultura centrada e interação | Notebook 04 |
| Variável anual | Agricultura do ano anterior; efeito próprio mantido por hierarquia, com interpretação prudente | Testes anuais e tendências nacionais |
| Modelos comparáveis | Pooled, FE país e RE com os mesmos quatro termos e 4 665 observações, sem tempo no trio de base | Tabela 4.1 |
| Efeitos de tempo | Extensões FE com data e com data + país × mês, na mesma amostra | Tabela 4.2 |
| Modelo preferido | FE país + data + sazonalidade nacional para a associação contemporânea | Hipóteses e diagnósticos; não seleção por R² |
| Dinâmica | Uma sensibilidade com temperatura do mês anterior, substituindo a corrente e mantendo quatro termos | Contemporâneo reestimado nos mesmos 4 650 pares |
| Tendência e extremos | Sensibilidades com tendências nacionais e resposta limitada aos quantis nacionais 1%/99% | Tabela de robustez; entrada principal preservada |
| Inferência | EP agrupados por país, correção finita e IC t(14); limites de poucos grupos e dependência transversal explícitos | Notebook 04 e CSV |
| Hausman | Usar variância comum do RE; preservar diagnóstico da diferença não normalizada. Acrescentar Mundlak agrupado como verificação complementar | χ²(4)=10,466, p=0,0333; F(4,14)=5,730, p=0,0060; autovalores e hipóteses no notebook 04 |
| Reprodução | Recuperar script, histórico climático, normais e 51 arquivos de origem | `scripts/verificar_reproducao.py` |
| Apresentação | Cinco figuras compactas, sem título ou rodapé dentro da imagem | PNG a 300 dpi, SVG e PDF |

As escolhas de agricultura e do desfasamento de um mês foram definidas antes da execução dos novos modelos. A especificação contemporânea foi mantida mesmo depois de a variante desfasada produzir uma associação positiva. A verificação com tendências nacionais e limites nos quantis foi acrescentada para avaliar os riscos identificados no feedback. Estas decisões não equivalem a um pré-registo externo.

A revisão de 12 de novembro do aviso de Hausman distinguiu duas questões: a diferença não normalizada de covariâncias é indefinida; a variante com variância comum resolve esse problema numérico, mas continua sujeita às hipóteses clássicas. O teste de Mundlak com agrupamento foi acrescentado como diagnóstico complementar das restrições do RE, sem mudar a amostra, as estimativas dos modelos principais ou a especificação preferida. É um método adicional ao material de base da UC e está explicado no notebook; não deve ser apresentado sem compreender a hipótese testada.

As extensões não alteram retroativamente os diagnósticos exploratórios dos notebooks 01–03. Os testes HAC, BH e Kruskal já existentes são resultados complementares; a síntese principal apoia-se em perfis, ACF e resíduos dos modelos. A Parte 2 não foi estimada nesta revisão. A utilização de 2025 na Parte 1 é retrospetiva; os gráficos exploratórios de Portugal não devem ser reutilizados para selecionar o SARIMA.

## Verificações que dependem do grupo

Os quatro notebooks foram executados de início a fim em 12 de novembro de 2026 num ambiente virtual novo, sem acesso aos pacotes do Python global. Após a auditoria, as 39 células de código terminaram sem erros e os 12 testes de regressão passaram. As versões e os hashes dos notebooks e scripts constam de `resultados/verificacao_execucao.json`. A verificação das fontes e reconstrução dos indicadores decorreu no notebook 01. A lista de 16 pontos e as limitações remanescentes estão em `auditoria_codigo.md`.

O registo no Excel da UC, a composição do grupo, a eventual aprovação do uso de CRU como fonte institucional e os usos de IA anteriores a esta revisão não foram confirmados. Não foram efetuadas alterações no Excel, no GitHub ou no Moodle. O documento de feedback foi usado como informação para a revisão, não como autorização para executar as tarefas administrativas nele listadas.

## Orientações de escrita e apresentação

- [Data Storyteller](https://github.com/dkyazzentwatwa/chatgpt-skills/blob/main/data-storyteller/SKILL.md): começar pelos resultados e ligar afirmações às tabelas, com limites explícitos. O auxiliar genérico foi consultado; preservou-se o cálculo específico do painel, evitando tratar a coluna empilhada como uma única série.
- [Data Scientist](https://github.com/borghei/Claude-Skills/blob/main/data-analytics/data-scientist/SKILL.md): comparar com uma referência, reportar incerteza e registar especificações. A seleção de variáveis é substantiva e não uma seleção automática orientada pelo valor-p.
- [Hallmark, data-viz](https://github.com/nutlope/hallmark/blob/main/skills/hallmark/references/data-viz.md): um destaque cromático, texto neutro, grelhas leves, eixos honestos e ausência de decoração. As figuras científicas usam Matplotlib para exportação vetorial; não foi construído um website.
- [BeHuman](https://github.com/alirezarezvani/claude-skills/blob/main/engineering/behuman/skills/behuman/SKILL.md): escrita direta, sem frases de enchimento. A aplicação limita-se à redação; não altera os cálculos nem a apresentação da incerteza.
- [Ponytail](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md): aproveitar a estrutura existente, evitar abstrações desnecessárias e manter verificações dos cálculos.
