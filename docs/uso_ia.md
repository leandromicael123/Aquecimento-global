# Registo de apoio de IA

Nesta revisão, em 11–12 de novembro de 2026, foi utilizado o Codex da OpenAI para ler o feedback e o guião, rever a estrutura da Parte 1, recuperar os ficheiros de reprodução disponíveis localmente, implementar e executar modelos de painel, preparar figuras e redigir interpretações. A continuação de 12 de novembro usou o modelo GPT-6.1 Sol; a designação exata do modelo usado na etapa anterior não foi registada.

Foram consultadas, a pedido do utilizador, as orientações Data Storyteller, Data Scientist, Hallmark, BeHuman e Ponytail, identificadas em `decisoes_parte1.md`. São instruções de trabalho para a ferramenta, não fontes científicas para as conclusões económicas.

As verificações incluem comparação dos hashes das 51 fontes, reconstrução offline dos indicadores, comparação com as entradas preservadas, conferência do posto das matrizes e equivalência do FE com o cálculo within. A execução integral dos notebooks e as verificações realizadas ficam registadas em `resultados/verificacao_execucao.json`.

A auditoria posterior incluiu pesquisa de erros comuns, testes com entradas inválidas e falhas simuladas, verificação FWL do modelo final, inferência Driscoll–Kraay e influência da retirada de cada país. As correções e as limitações estão descritas em `auditoria_codigo.md`.

Este texto regista apenas a utilização conhecida nesta revisão. O grupo deve completar as ferramentas e finalidades de usos anteriores, incluindo eventuais orientações `no-slop-ui` e `no-ai-slop` referidas no README anterior. Não se presume que todos os membros já tenham validado ou compreendido os resultados.

## Formulação para adaptar na entrega

Utilizámos o Codex da OpenAI para apoiar a revisão do código, a estimação e verificação dos modelos de painel, a apresentação gráfica e a redação da Parte 1. O apoio incidiu também na organização dos dados e das instruções de reprodução. Conferimos os resultados através da execução do código, comparação com as fontes e verificações independentes de transformações e estimadores. A identificação de outras ferramentas utilizadas e a confirmação da revisão pelos membros do grupo devem ser completadas antes de assumir coletivamente a responsabilidade pelo trabalho entregue.
