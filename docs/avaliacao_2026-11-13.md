# Modelos Longitudinais — atualização da avaliação (13/11/2026)

13/11/2026 · Atualização da avaliação de 7/11/2026. Os estados das tabelas são os desta data.

## Resumo

O commit de 12/11 completa a Parte 1, e todos os números novos conferidos batem certo. Faltam a Parte 2, o relatório LaTeX e confirmar o registo no Excel; a entrega é a 6/12/2026, daqui a 23 dias.

- **Guião:** 24 dos 34 requisitos estão cumpridos (eram 10 a 7/11), 3 em parte, 6 em falta e 1 por confirmar. Os 6 em falta são cinco pontos da Parte 2 e o relatório LaTeX.
- **Problemas de 7/11:** 6 dos 9 estão resolvidos. Estão em parte o registo no Excel e a apresentação (comentários no código, declaração de IA); o diagnóstico de Portugal só com o treino continua por fazer.
- **Resultado:** no modelo preferido, com efeitos de país, data e país × mês, +1 °C associa-se a −0,044 p.p. de inflação mensal ao peso agrícola médio, IC 95% [−0,097; 0,008]. Com a temperatura do mês anterior, a estimativa é +0,109 [0,030; 0,189]: a conclusão depende do momento da exposição.
- **A seguir:** a Parte 2 é a prioridade. A síntese da Parte 1 tem 3 434 palavras e tem de caber, com a Parte 2, em 4 páginas. Todos têm de saber defender os métodos novos na discussão de 11/12/2026.

## O que o commit de 12/11 acrescenta

O commit b5b6f57, de 12/11, acrescenta os modelos de painel, uma síntese escrita da Parte 1, o pacote de reprodução dos dados e uma auditoria com testes.

| Elemento | Ficheiros | Conteúdo |
| --- | --- | --- |
| Modelos de painel | `notebooks/04_modelos_painel.ipynb`, `scripts/modelos_painel.py` | Pooled, FE país e RE com os mesmos quatro termos; FE com data e com data + país × mês; Hausman, Mundlak, resíduos e sensibilidades |
| Tabelas de resultados | `resultados/tabelas/04_modelos/` | 13 ficheiros: coeficientes com EP e IC, resíduos por país, efeitos marginais, robustez, Mundlak, Driscoll–Kraay, influência de cada país |
| Síntese da Parte 1 | `relatorio/parte1.md` | 3 434 palavras, 3 tabelas e 5 figuras; cobre as secções 3.1 a 3.3 do guião |
| Figuras | `resultados/graficos/04_modelos/` | 5 figuras em PNG a 300 dpi, SVG e PDF, com 3,45 a 6,9 polegadas de largura e sem título dentro da imagem |
| Reprodução dos dados | `dados/reproducao/`, `scripts/verificar_reproducao.py` | Script de construção, 51 ficheiros de origem com SHA-256, clima de 1901–2025, normais de 1991–2020 e a série de Portugal com 299 meses de treino e 12 de teste |
| Auditoria | `scripts/auditoria.py`, `tests/test_auditoria.py`, `docs/auditoria_codigo.md` | 12 testes e uma lista de 16 erros comuns verificados |
| Decisões e cobertura | `docs/decisoes_parte1.md`, `docs/cobertura_parte1.md` | Resposta ponto a ponto ao feedback de 7/11 e mapa dos requisitos 3.1 a 3.3 |
| Declaração de IA | `docs/uso_ia.md` | Uso do Codex (OpenAI) a 11 e 12/11; o próprio texto pede ao grupo que complete os usos anteriores |
| README e dependências | `README.md`, `requirements.txt` | Sem as referências no-slop; diz que a Parte 2 e o relatório não estão feitos; acrescenta linearmodels 7.0 |

O painel de entrada (`dados/originais/painel_indicadores.csv`) tem o mesmo SHA-256 de 7/11, por isso as verificações descritivas da primeira avaliação continuam válidas.

## Verificação dos números novos

Todos os números novos de `relatorio/parte1.md` batem certo, incluindo os arredondamentos. Foram recalculados com código próprio sobre os CSV de dados, sem executar o código do repositório.

| Valor citado em `parte1.md` | Recalculado |
| --- | --- |
| Centro do peso agrícola: 15,436% do PIB | 15,436 |
| Tabela 1, temperatura: pooled −0,060 [−0,117; −0,003]; FE país −0,049 [−0,109; 0,011]; RE −0,051 [−0,110; 0,007] | Iguais |
| Tabela 1, défice, agricultura e interação nos três modelos | Iguais nos 9 coeficientes e respetivos IC |
| Tabela 1, R²: 0,0021; 0,0272; 0,0008 | Iguais |
| Tabela 2, FE país + data: temperatura −0,058 [−0,109; −0,007]; R² 0,1464 | Iguais, tal como os outros 3 termos |
| Tabela 2, FE país + data + sazonal: temperatura −0,044 [−0,097; 0,008]; défice −0,022 [−0,081; 0,037]; agricultura −0,031 [−0,066; 0,004]; interação 0,002 [−0,004; 0,008]; R² 0,3805 | Iguais |
| RE: θ = 0,664; variância do intercepto aleatório 0,078 | 0,664 e 0,078; variância residual 3,102 |
| Hausman com variância comum: χ²(4) = 10,466, p = 0,0333 | Igual; sem normalizar, a diferença das covariâncias não é definida positiva (autovalor mínimo −2,0 × 10⁻⁶) |
| Mundlak: F(4,14) = 5,730, p = 0,0060 | Igual |
| DP residual por país: 0,713 a 2,780 (FE data); 0,635 a 2,528, razão 3,98 (FE final) | Iguais |
| Ljung–Box: 14 países a 12 meses (FE data); 9 a 12 meses e 13 a 24 meses (FE final) | Iguais |
| Correlação residual entre países no FE final: mediana −0,095; mediana dos valores absolutos 0,212 | Iguais |
| Driscoll–Kraay a 12 meses: EP 0,047, IC [−0,137; 0,048], p 0,3439; desfasado IC [0,019; 0,200], p 0,0183 | EP 0,0469; IC [−0,1368; 0,0479]; p 0,3439; desfasado [0,0187; 0,2002], p 0,0183 |
| Retirar um país de cada vez: −0,056 a −0,016 | −0,0565 a −0,0165; desfasado 0,0879 a 0,1280 |
| Desfasamento de 1 mês, 4 650 observações: temperatura 0,109 [0,030; 0,189]; interação 0,007 [0,002; 0,013] | Iguais; o contemporâneo nos mesmos pares dá −0,041 [−0,095; 0,013] |
| Tendências nacionais e limites 1%/99%: o IC da temperatura inclui zero | −0,040 [−0,107; 0,028] e −0,043 [−0,095; 0,008] |
| ADF rejeita raiz unitária / KPSS rejeita estacionariedade: inflação mensal em 15 e 2 países; agricultura anual em 5 e 8; ln PIB em 3 e 9 | Iguais |
| 51 SHA-256 do manifesto; reconstrução com tolerância 10⁻¹⁰ | 51 de 51 conferem; o painel de `dados/reproducao/` difere do de entrada no máximo 8,9 × 10⁻¹⁴ |

Não foram verificadas a execução dos notebooks e dos 12 testes, relatada em `resultados/verificacao_execucao.json`, nem a reconstrução dos dados a partir dos ficheiros de origem.

## Estado dos 9 problemas de 7/11

Dos 9 problemas apontados a 7/11, 6 estão resolvidos, 2 em parte e 1 por fazer; o que está por fazer é da Parte 2.

| # | Problema (7/11) | Estado | O que foi feito | O que falta |
| --- | --- | --- | --- | --- |
| 1 | Há duas versões do trabalho | Em parte | O ramo seguiu a versão da inflação alimentar (`decisoes_parte1.md`) | Confirmar a decisão em grupo e o registo no Excel; o próprio repositório diz que não foram confirmados |
| 2 | Variáveis económicas quase constantes no país; ln PIB com tendência | Resolvido | ln PIB fora da especificação principal; peso agrícola centrado em 15,436, como moderador; ADF e KPSS anuais por país | Não interpretar o efeito próprio da agricultura (−0,031 no FE final) |
| 3 | Duas especificações não cabem em 4 páginas | Resolvido | Uma só: temperatura, défice, agricultura centrada e interação | Nada |
| 4 | Associação contemporânea quase nula | Resolvido | Sensibilidade com a temperatura do mês anterior: +0,109 [0,030; 0,189] | Saber explicar porque o contemporâneo continua a ser o principal (Novos riscos) |
| 5 | Sazonalidade diferente em cada país | Resolvido | FE com efeitos país × mês do calendário; o Ljung–Box a 12 meses passa de 14 para 9 países | Nada |
| 6 | Inferência frágil com 15 países | Resolvido | EP agrupados por país com correção e IC t(14); Hausman com ressalvas; Mundlak, Driscoll–Kraay e retirada de cada país | Os limites mantêm-se e têm de ser ditos: 15 grupos, DP residual com razão 3,98, autocorrelação em 9 países |
| 7 | Diagnósticos da Parte 2 com o período de teste | Por fazer | O repositório reconhece que os gráficos de Portugal com 2025 não servem para escolher o SARIMA | Refazer o diagnóstico de Portugal só com fevereiro de 2000 a dezembro de 2024 |
| 8 | Dados não reprodutíveis | Resolvido | `dados/reproducao/` com o script de construção e 51 ficheiros de origem; os 51 SHA-256 conferem | Correr `verificar_reproducao.py` num ambiente limpo antes da entrega |
| 9 | Apresentação e declaração de IA | Em parte | 5 figuras compactas, sem título nem rodapé na imagem; `docs/uso_ia.md` criado | Comentar o código (24 linhas de comentário em 2 135 linhas de scripts) e completar a declaração de IA |

## Cumprimento do guião, ponto a ponto

Dos 34 requisitos do guião, 24 estão cumpridos (eram 10 a 7/11), 3 em parte, 6 em falta e 1 por confirmar. A Parte 1 (3.1 a 3.3) está toda cumprida; falta a Parte 2, o relatório, comentar o código, completar a declaração de IA e confirmar o Excel.

| § | Requisito | 7/11 | 13/11 | Evidência a 13/11 |
| --- | --- | --- | --- | --- |
| 2 | Dados mensais ou trimestrais; série da Parte 2 tirada do painel | Feito | Feito | Sem alteração |
| 2 | Fontes identificadas e adequação justificada | Parcial | Feito | Manifesto com versões e SHA-256; `parte1.md` justifica o CRU-CY e diz que não é um instituto de estatística. A aceitação do CRU pela docente não está confirmada |
| 2 | Séries sem ajuste sazonal | Feito | Feito | Sem alteração |
| 2 | 10 a 20 países, pelo menos 10 anos, período comum | Feito | Feito | Sem alteração |
| 2 | Uma resposta quantitativa e 2 a 4 explicativas | Parcial | Feito | Uma especificação: 3 variáveis e a interação |
| 2 | Sem agregados regionais; sem interpolar dados anuais | Feito | Feito | Sem alteração |
| 2 | Registo no Excel coerente com o desenho | Por confirmar | Por confirmar | O repositório diz que não foi confirmado |
| 3.1.1 | Questões de investigação e justificação das variáveis | Feito | Feito | Q1 e Q2 em `parte1.md`, secção 1 |
| 3.1.2 | Formato longo, sem pares país–tempo duplicados | Feito | Feito | Sem alteração |
| 3.1.3 | Unidades, frequência, n.º de países e períodos, dimensão, equilíbrio | Feito | Feito | Sem alteração |
| 3.1.4 | Omissos, extremos e unidades, sem substituir faltas por zero | Feito | Feito | Sem alteração |
| 3.1.5 | Descritivas, trajetórias e variabilidade entre e dentro | Feito | Feito | Figuras 1 e 2 de `parte1.md` |
| 3.2.1 | Pooled OLS | Falta | Feito | Tabela 1 |
| 3.2.2 | Efeitos fixos por país, com efeitos de tempo justificados | Falta | Feito | Tabelas 1 e 2: FE país, FE país + data, FE país + data + país × mês |
| 3.2.3 | Efeitos aleatórios e hipótese de não correlação | Falta | Feito | Tabela 1; a hipótese de não correlação entre αᵢ e as explicativas é discutida na secção 3 |
| 3.2 | Mesmas covariáveis e amostra; papel de αᵢ e λₜ em cada modelo | Parcial | Feito | 4 665 observações e 4 termos em todos; quadro dos efeitos em cada modelo |
| 3.3 | Tabela com coeficientes, EP ou IC, n e ajustamento | Falta | Feito | Tabelas 1 e 2 com IC 95%; EP em `01_coeficientes.csv` |
| 3.3 | Interpretação de sinal, magnitude e unidades; o que o FE identifica | Falta | Feito | «Como ler as magnitudes»; efeito marginal β₁ + β₄Aᶜ com a covariância |
| 3.3 | Heteroscedasticidade e dependência dos resíduos; EP agrupados; poucos países; choques comuns | Parcial | Feito | Secção 5: DP por país, Ljung–Box, correlação entre países, Driscoll–Kraay |
| 3.3 | Escolha do modelo pelas hipóteses, não pelo R²; Hausman | Falta | Feito | FE final escolhido pelas hipóteses; Hausman e Mundlak com ressalvas |
| 3.3 | Tendências e não estacionariedade; níveis, logaritmos ou taxas | Parcial | Feito | ADF e KPSS mensais e anuais; tendências nacionais como sensibilidade |
| 3.3 | Associação não é causalidade; variáveis omitidas | Parcial | Feito | Secção 7: omitidas listadas e ligadas aos resultados |
| 4.1.1 | Série de um país, períodos regulares, justificação do país | Parcial | Parcial | Série de Portugal pronta; falta justificar a escolha de Portugal |
| 4.1.2 | Gráfico e análise de tendência, sazonalidade e extremos | Parcial | Falta | Os gráficos de Portugal incluem 2025 e o repositório diz que não servem para a Parte 2; falta a análise só com o treino |
| 4.1.3 | Últimos 12 meses para teste | Feito | Feito | `portugal_sarima.csv`: 299 meses de treino e 12 de teste |
| 4.1.4 | Transformação e diferenciação com ACF/PACF e testes, só no treino | Falta | Falta | Não feito |
| 4.2.1–2 | SARIMA candidatos com AIC/BIC; resíduos e Ljung–Box | Falta | Falta | Não feito |
| 4.2.3–4 | Comparação com o ingénuo sazonal e com ARIMA sem componente sazonal | Falta | Falta | Não feito |
| 4.3 | Previsões no teste, MAE e RMSE, gráfico com IC 95%, discussão dos erros | Falta | Falta | Não feito |
| 5 | Relatório PDF e LaTeX (ACL), 4 páginas, nomes e números no topo, sem capa nem anexos | Falta | Falta | Só existe `parte1.md`, com 3 434 palavras |
| 5 | Código comentado e executável sem erros | Parcial | Parcial | Execução sem erros relatada (39 células, 12 testes); 24 linhas de comentário em 2 135 linhas de scripts |
| 5 | Dados ou instruções de obtenção, códigos, data de extração, versões | Parcial | Feito | `dados/reproducao/` com script, manifesto e ficheiros de origem |
| 6 | Declaração de uso de IA verdadeira e adaptada | Falta | Parcial | `docs/uso_ia.md` cobre só o Codex a 11 e 12/11 |
| 7 | Legendas, unidades, sem saídas extensas do Python | Parcial | Feito | Figuras com legenda, fonte e unidades em `parte1.md`; manter no LaTeX |

## Novos riscos

Os riscos já não estão no conteúdo da Parte 1, mas no prazo, no espaço do relatório e na defesa oral.

1. **A Parte 2 ainda não começou.** Faltam o diagnóstico só com o treino, os SARIMA candidatos, o ARIMA, o ingénuo sazonal e as previsões de 2025: 5 dos 6 requisitos em falta. Com 23 dias até à entrega, é a prioridade.
2. **Há mais métodos fora dos materiais da UC.** Aos quatro do notebook 03 juntam-se o Hausman com variância comum, o teste de Mundlak, o Driscoll–Kraay, a verificação FWL, a retirada de cada país e o RE estimado com a biblioteca linearmodels, que não aparece nos materiais. Na discussão de 11/12/2026, qualquer elemento pode ter de os explicar; o próprio `decisoes_parte1.md` avisa que o Mundlak não deve ser apresentado sem compreender a hipótese testada. Proposta: no relatório, apoiar a escolha no que vem das aulas (pooled, FE, RE, erros agrupados, Hausman com as ressalvas do Caderno, Solução 64) e deixar o resto como robustez.
3. **O resultado depende do momento da exposição.** O contemporâneo é −0,044 [−0,097; 0,008] no FE final e −0,041 [−0,095; 0,013] nos 4 650 pares do desfasado; o desfasado é +0,109 [0,030; 0,189]. Um avaliador pode perguntar porque fica como principal a versão cujo IC inclui zero. A resposta está em `decisoes_parte1.md`: o desfasamento foi definido antes de estimar e o contemporâneo manteve-se; o relatório deve dizê-lo numa frase, sem somar os dois efeitos.
4. **A síntese da Parte 1 não cabe no relatório.** `parte1.md` tem 3 434 palavras, 3 tabelas e 5 figuras só para a Parte 1, e o relatório tem 4 páginas no modelo ACL para as duas partes. Estimativa desta revisão (fora dos materiais da UC): com 800 a 1 000 palavras por página ACL, só esse texto ocuparia 3,4 a 4,3 páginas. É preciso decidir já o espaço de cada parte e escrever o LaTeX a partir das Tabelas 1 e 2 e de poucas figuras.
5. **A declaração de IA está incompleta.** `docs/uso_ia.md` regista só o Codex a 11 e 12/11 e pede ao grupo que complete os usos anteriores. As decisões de 11 e 12/11 partiram do feedback de 7/11 (`decisoes_parte1.md`), preparado com o Claude, da Anthropic, tal como esta atualização. Cada elemento tem de listar as ferramentas que usou e para quê, incluindo estas avaliações.
6. **Há pormenores desatualizados.** `dados/reproducao/LEIA-ME.md` ainda descreve as duas especificações de outubro e diz que os modelos não foram estimados. As tabelas de `parte1.md` escrevem «FE pais», sem acento. Os scripts têm 24 linhas de comentário em 2 135.

## Próximos passos

O plano dá 11 dias à Parte 2, fecha o relatório a 29/11 e deixa a última semana para revisão; responsáveis e datas são para o grupo confirmar.

| Tarefa | Responsável | Prazo | Estado |
| --- | --- | --- | --- |
| Confirmar a versão em grupo e o registo no Excel | | 16/11/2026 | Por fazer |
| Parte 2: diagnóstico de Portugal só com o treino (gráfico, decomposição, ACF/PACF, ADF e KPSS) e justificação da escolha de Portugal | | 18/11/2026 | Por fazer |
| Parte 2: SARIMA candidatos com AIC/BIC, ARIMA sem componente sazonal e ingénuo sazonal; Ljung–Box nos resíduos | | 22/11/2026 | Por fazer |
| Parte 2: previsões de 2025, MAE e RMSE, gráfico com IC 95% e discussão dos erros | | 24/11/2026 | Por fazer |
| Relatório LaTeX: condensar a Parte 1; introdução, fundamentos e métodos | | 26/11/2026 | Por fazer |
| Relatório: resultados, discussão e conclusão; confirmar as 4 páginas | | 29/11/2026 | Por fazer |
| Declaração de IA com as ferramentas de cada elemento, incluindo estas avaliações | | 29/11/2026 | Por fazer |
| Comentar o código; atualizar o `LEIA-ME.md` de `dados/reproducao/`; corrigir «FE pais» | | 1/12/2026 | Por fazer |
| Conferir cada número do relatório com os outputs e reexecutar tudo num ambiente limpo | | 3/12/2026 | Por fazer |
| Entrega no Moodle até às 23:59: PDF, LaTeX, notebooks e dados | | 6/12/2026 | Por fazer |
| Ensaiar a discussão com as perguntas da secção seguinte | | 10/12/2026 | Por fazer |

## Preparação para a discussão

Estas perguntas juntam-se às 12 da avaliação de 7/11, que continuam válidas; incidem sobre o que o commit de 12/11 acrescentou.

| Pergunta provável | O que todos têm de saber responder | Base |
| --- | --- | --- |
| Porque é que o modelo preferido é o FE com país, data e país × mês, e não o de maior R²? | Admite correlação entre as características persistentes do país e as explicativas, retira os choques comuns e as sazonalidades nacionais, que diferem (amplitude de 0,64 em Espanha a 5,48 no Níger). O R² (0,3805) não é o critério. | Guião, 3.3; `parte1.md`, secção 4 |
| Que efeito estima o coeficiente da temperatura, com a agricultura centrada? | O de +1 °C quando o peso agrícola está na média (15,436% do PIB): −0,044 p.p. por mês no FE final. Noutro nível de agricultura, o efeito é β₁ + β₄Aᶜ, e o IC usa a covariância dos dois coeficientes. | `parte1.md`, «Como ler as magnitudes» |
| Porque não se interpreta o efeito próprio da agricultura (−0,031)? | 97,19% da variabilidade do peso agrícola é entre países; no FE sobra pouca variação, anual e repetida nos 12 meses (390 pares país–ano). Entra só para respeitar a hierarquia da interação. | Caderno, Solução 56; `parte1.md`, secções 1 e 2 |
| O que diz o Hausman, e porque se usou a variância comum? | H0: o efeito do país não está correlacionado com as explicativas, e o RE é consistente. Com variâncias estimadas em separado, a diferença das covariâncias não era definida positiva; com a variância comum, χ²(4) = 10,466, p = 0,0333, e rejeita-se H0 a 5%. A versão clássica pressupõe um RE eficiente, o que falha com heteroscedasticidade e autocorrelação. | Caderno, Solução 64; a variância comum está fora dos materiais da UC |
| E o teste de Mundlak? | Acrescenta ao RE as médias nacionais dos quatro regressores e testa se os seus coeficientes são todos zero. Com erros agrupados, F(4,14) = 5,730, p = 0,0060: aponta no mesmo sentido do Hausman, sem exigir um RE eficiente. | `parte1.md`, secção 4 (fora dos materiais da UC) |
| Porque é que os IC usam t com 14 graus de liberdade? | Os erros são agrupados por país e há 15 grupos: usa-se t(G − 1). Com tão poucos grupos, a inferência é aproximada, mesmo com 4 665 observações. | `parte1.md`, secção 3; Aula 5, slide 11; t(G − 1) está fora dos materiais da UC |
| O que significa θ = 0,664 no RE? | O RE subtrai a cada observação 66,4% da média do seu país; o FE subtrai 100% e o pooled 0%, por isso o RE fica entre os dois. A variância do efeito do país é 0,078, contra 3,102 do erro: cerca de 2,5% da variância residual total. | Caderno, Soluções 61 e 63 |
| O desfasado é significativo e o contemporâneo não; qual é o verdadeiro efeito? | Nenhum dos dois sozinho: são especificações diferentes, e trocar a temperatura corrente pela do mês anterior não estima um efeito acumulado. O contemporâneo foi definido como principal antes de estimar; o desfasado (+0,109 [0,030; 0,189]) mostra que a conclusão depende do momento da exposição. | `decisoes_parte1.md`; `parte1.md`, secção 6 |
| Para que serve o Driscoll–Kraay? | Os erros agrupados por país não admitem correlação entre países no mesmo mês; o Driscoll–Kraay admite-a. O IC da temperatura contemporânea continua a incluir zero ([−0,137; 0,048]) e o do desfasado continua a excluí-lo ([0,019; 0,200]). | `parte1.md`, secção 5 (fora dos materiais da UC) |
| O modelo final ainda tem resíduos dependentes? | Sim: o Ljung–Box sinaliza 9 países a 12 meses e 13 a 24 meses, e a razão entre o maior e o menor DP residual é 3,98. Por isso se usam erros agrupados, e os valores-p perto de 5% leem-se com cautela. | Caderno, Solução 53; `parte1.md`, secção 5 |
| Como se garante que os dados são os das fontes? | Os 51 ficheiros de origem estão no repositório com SHA-256, e `verificar_reproducao.py` reconstrói os indicadores sem acesso à Internet. | `dados/reproducao/`; guião, 5 |

Cada elemento deve conseguir responder a todas, não só às da parte que fez.

## Referências

- Guião do trabalho de grupo, Modelos Longitudinais, Licenciatura em Ciência de Dados, 2026/2027 (Moodle).
- Materiais da UC (D. A. Mendes, 2026): Aula 5, «Introdução a dados longitudinais»; Caderno de exercícios, Soluções 53, 56, 61, 63 e 64.
- Avaliação de 7/11/2026, «Modelos Longitudinais — avaliação do ramo Primeira-parte e plano até à entrega» (versão Word preparada para o grupo).
- Repositório [leandromicael123/Aquecimento-global, ramo Primeira-parte](https://github.com/leandromicael123/Aquecimento-global/tree/Primeira-parte), [commit b5b6f57](https://github.com/leandromicael123/Aquecimento-global/commit/b5b6f57ac344cd8e36910a35936ee5d5baa2efe1) de 12/11/2026. Ficheiros citados: [relatorio/parte1.md](https://github.com/leandromicael123/Aquecimento-global/blob/b5b6f57ac344cd8e36910a35936ee5d5baa2efe1/relatorio/parte1.md), [docs/decisoes_parte1.md](https://github.com/leandromicael123/Aquecimento-global/blob/b5b6f57ac344cd8e36910a35936ee5d5baa2efe1/docs/decisoes_parte1.md), [docs/uso_ia.md](https://github.com/leandromicael123/Aquecimento-global/blob/b5b6f57ac344cd8e36910a35936ee5d5baa2efe1/docs/uso_ia.md), [docs/auditoria_codigo.md](https://github.com/leandromicael123/Aquecimento-global/blob/b5b6f57ac344cd8e36910a35936ee5d5baa2efe1/docs/auditoria_codigo.md), [dados/reproducao/LEIA-ME.md](https://github.com/leandromicael123/Aquecimento-global/blob/b5b6f57ac344cd8e36910a35936ee5d5baa2efe1/dados/reproducao/LEIA-ME.md) e [resultados/tabelas/04_modelos/](https://github.com/leandromicael123/Aquecimento-global/tree/b5b6f57ac344cd8e36910a35936ee5d5baa2efe1/resultados/tabelas/04_modelos).
