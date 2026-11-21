# Registo de apoio de IA

## Codex (OpenAI), Parte 1

Nesta revisão, em 11–12 de novembro de 2026, foi utilizado o Codex da OpenAI para ler o feedback e o guião, rever a estrutura da Parte 1, recuperar os ficheiros de reprodução disponíveis localmente, implementar e executar modelos de painel, preparar figuras e redigir interpretações. A continuação de 12 de novembro usou o modelo GPT-6.1 Sol; a designação exata do modelo usado na etapa anterior não foi registada.

Foram consultadas, a pedido do utilizador, as orientações Data Storyteller, Data Scientist, Hallmark, BeHuman e Ponytail, identificadas em `decisoes_parte1.md`. São instruções de trabalho para a ferramenta, não fontes científicas para as conclusões económicas.

As verificações incluem comparação dos hashes das 51 fontes, reconstrução offline dos indicadores, comparação com as entradas preservadas, conferência do posto das matrizes e equivalência do FE com o cálculo within. A execução integral dos notebooks e as verificações realizadas ficam registadas em `resultados/verificacao_execucao.json`.

A auditoria posterior incluiu pesquisa de erros comuns, testes com entradas inválidas e falhas simuladas, verificação FWL do modelo final, inferência Driscoll–Kraay e influência da retirada de cada país. As correções e as limitações estão descritas em `auditoria_codigo.md`.

Este texto regista apenas a utilização conhecida nesta revisão. O grupo deve completar as ferramentas e finalidades de usos anteriores, incluindo eventuais orientações `no-slop-ui` e `no-ai-slop` referidas no README anterior. Não se presume que todos os membros já tenham validado ou compreendido os resultados.

## Claude (Anthropic)

- Avaliações da Parte 1 de 7/11/2026 e de 13/11/2026 (a segunda está em `docs/avaliacao_2026-11-13.md`): preparadas com o Claude, da Anthropic, como essa avaliação indica. O commit de 13/11 regista o modelo Claude Fable 5.2; o modelo usado a 7/11 não foi registado.
- 20/11/2026, a pedido de Paula Relvas: ponto de situação do ramo `Segunda-parte` face ao guião (modelos Claude Fable 5.2 e Claude Opus 5.5).
- 20 e 21/11/2026, a pedido de Paula Relvas, com o modelo Claude Opus 5.5: revisão do notebook 05 (leitura dos dados locais, cálculo da comparação entre países que justifica o Níger, correções de texto); escrita e execução do notebook 06 (secções 4.2 e 4.3: candidatos, validação com origem móvel, diagnóstico dos resíduos, previsões de 2025 e avaliação); redação de `relatorio/parte2.md` e de `docs/cobertura_parte2.md`; atualização do README e do `LEIA-ME.md` dos dados.

Verificações desta etapa: os notebooks 05 e 06 foram executados de raiz num kernel limpo, com as versões de bibliotecas do `requirements.txt`; os números do notebook 05 foram recalculados com código independente; as afirmações do texto do notebook 06 estão protegidas por verificações (`assert`) que interrompem a execução se os resultados mudarem; as métricas de validação e de teste foram recalculadas a partir dos ficheiros de previsões gravados. Todos os elementos do grupo devem rever estas escolhas e conseguir explicá-las na discussão.

## Formulação para adaptar na entrega

Utilizámos o Codex, da OpenAI, e o Claude, da Anthropic, para apoiar a revisão do código, a estimação e verificação dos modelos de painel e dos modelos SARIMA, a apresentação gráfica e a redação das sínteses das duas partes. O apoio incidiu também na organização dos dados e das instruções de reprodução. Conferimos os resultados através da execução do código, comparação com as fontes e verificações independentes de transformações, estimadores e métricas de previsão. A identificação de outras ferramentas utilizadas e a confirmação da revisão pelos membros do grupo devem ser completadas antes de assumir coletivamente a responsabilidade pelo trabalho entregue.
