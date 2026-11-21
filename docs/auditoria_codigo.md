# Auditoria do código e da análise

Revisão de 12 de novembro de 2026. Âmbito: Parte 1, entradas preservadas, scripts, quatro notebooks e interpretações. A lista abaixo foi definida a partir das fontes técnicas indicadas e confrontada com o código e os dados; uma execução sem erros não foi tomada como prova de validade estatística.

## Lista de erros comuns e resultado da revisão

| Erro a evitar | Verificação neste projeto | Resultado |
|---|---|---|
| Tratar uma chave duplicada, omissa ou uma data irregular como painel válido | Introduzir duplicados, retirar um mês e acrescentar uma data a meio do mês | Corrigido: as datas fora da grelha também impedem a classificação como equilibrado |
| Deixar NaN ou infinito chegar ao estimador | Introduzir NaN, +inf e −inf no clima | Corrigido: o notebook 04 aplica a validação completa, mesmo quando executado isoladamente |
| Multiplicar linhas num merge ou ignorar correspondências incompletas | Verificar cardinalidade das junções e valores das fontes depois do merge | A cardinalidade já era verificada. Corrigida a aceitação de um omisso no peso agrícola da fonte anual |
| Tratar valores anuais repetidos como novas medições mensais | Verificar desfasamento e constância da variável em cada país–ano; testar estacionariedade à frequência anual | Corrigida a validação autónoma do ano económico no notebook 04. Mantêm-se 26 observações anuais por país nos testes |
| Calcular um lag através da fronteira entre países ou omitir meses | Ordenar por país e data, exigir grelha regular e usar shift dentro do país | Conferido; a variante perde um mês por país e usa amostra comparável |
| Estimar uma matriz singular sem aviso ou confundir escala com colinearidade | Posto completo, regressão FWL independente e condição dos regressores residualizados/padronizados | Conferido: erro máximo FWL ≈ 3,6×10⁻¹⁵ e condição ≈ 1,49. A fraca variação anual continua uma limitação substantiva |
| Comparar modelos em observações diferentes | Verificar índices país–data antes de calcular Hausman | Corrigido: o teste recusa amostras ou ordens diferentes |
| Forçar um valor-p quando a matriz do teste é inválida | Testar uma diferença de covariâncias indefinida | Conferido: sem inversa generalizada ou regularização para produzir significância; o relato aceita resultado indisponível |
| Confundir execução, validade numérica e validade inferencial | Hausman com variância comum separado das suas hipóteses; Mundlak agrupado complementar | Ambos continuam dependentes das hipóteses e de aproximações com poucos países |
| Presumir que t(14) resolve todos os problemas de 15 grupos | Contrastar agrupamento por país com inferência Driscoll–Kraay a 12 e 24 meses | Risco avaliado, não eliminado. Todos os erros padrão e intervalos são identificados pelo método |
| Presumir independência entre países após incluir datas | Examinar correlações residuais e recalcular covariância admitindo dependência transversal | Mantida a ressalva; os efeitos de data podem induzir correlações negativas e não garantem independência |
| Apagar extremos ou países para obter um resultado favorável | Resposta principal intacta; 15 exclusões individuais reportadas para cada calendário | Conferido: nenhum país é excluído do modelo principal. O centro da agricultura é fixo nas comparações |
| Ignorar os limites tabulados do KPSS | Distinguir p<0,01, p>0,10 e valores interpolados | Corrigida a exportação: coluna `p_kpss_limite`, além do valor numérico e dos avisos |
| Interpretar apenas p<0,05, causalidade ou “não significativo = sem efeito” | Rever magnitudes, IC, interações, desfasamento e variáveis omitidas | A conclusão contemporânea é incerta; a associação desfasada é exploratória. IC pontuais, sem alegação de controlo global de multiplicidade |
| Usar 2025 para selecionar uma previsão | Confirmar âmbito retrospetivo da Parte 1 e ausência de SARIMA | Conferido nesta revisão. A futura Parte 2 exige divisão temporal e novos diagnósticos apenas no treino |
| Deixar texto fixo acompanhar dados alterados ou um sucesso antigo sobreviver a uma falha | Trocar o ficheiro de entrada e simular uma execução interrompida por erro | Corrigido: exportação da síntese recusa outra versão dos dados; registo de execução indica `falhou`, com erro e resultados parciais |

## Correções verificadas por testes

Foram criados 12 testes em `tests/test_auditoria.py`, cobrindo as falhas de entrada, invariância à ordem das linhas, restrição de amostras do Hausman, matriz inválida, apresentação de um valor indisponível, proteção da versão dos dados e substituição de um registo antigo de sucesso por uma falha real.

Executar na raiz:

```powershell
.\.venv_validacao\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes não demonstram ausência de todos os erros. Cobrem casos concretos que foram reproduzidos, incluindo quatro falhas que passavam pela versão anterior. As estimativas principais não mudaram devido às correções de validação, porque as entradas atuais não continham esses defeitos.

## Resultados das verificações estatísticas

O FE final foi recalculado pelo teorema de Frisch–Waugh–Lovell, retirando da resposta e dos quatro regressores os controlos de país, data e sazonalidade nacional. Os coeficientes coincidem. Não foram detetados problemas numéricos de colinearidade entre esses regressores após controlar os efeitos fixos.

Para a temperatura contemporânea, o erro padrão agrupado é 0,0247; com Driscoll–Kraay e largura de 12 meses, passa a 0,0469. O IC correspondente é [−0,1368; 0,0479] e o p aproximado 0,3439. A associação desfasada mantém IC positivo nessa verificação: [0,0187; 0,2002], p aproximado 0,0183. A largura de 24 meses é apresentada igualmente. Estas escolhas não foram ajustadas para procurar o menor p.

Retirar um país de cada vez dá coeficientes térmicos entre −0,0565 e −0,0165 no contemporâneo e entre 0,0879 e 0,1280 no lag. A retirada do Níger afeta bastante a magnitude contemporânea. O sinal não depende exclusivamente de um país, mas a amostra continua intencional e pequena. Os CSV `11_inferencia_dk.csv` e `12_influencia_paises.csv` contêm todos os resultados; `13_auditoria_numerica.json` guarda as verificações.

Driscoll–Kraay explora a dimensão temporal longa (311/310 meses); não é uma correção exata nem garante validade perante qualquer quebra ou dinâmica. O teste DK com lag zero foi ainda confrontado com o caso limite de agrupamento por data, aplicando a mesma correção finita. Não foi implementado um wild cluster bootstrap ou CR2: permanecem extensões possíveis para estudar a inferência com 15 grupos. A conclusão não depende de fingir que esse risco está resolvido.

## Fontes da lista

- [statsmodels — Pitfalls](https://www.statsmodels.org/stable/pitfalls.html): modelos lineares podem usar inversa generalizada sem rejeitar automaticamente matrizes deficientes; foi verificado o posto e uma solução independente.
- [pandas — Merge, join, concatenate and compare](https://pandas.pydata.org/docs/user_guide/merging.html): cardinalidade e multiplicação de linhas nas junções; foram conferidas as relações e a completude numérica das fontes.
- [Stata — Robust inference](https://www.stata.com/stata-news/news39-2/robust-inference/): limitações de inferência agrupada com poucos grupos e alternativas de pequena amostra. Esta auditoria não equipara uma referência t a uma solução exata.
- [statsmodels — Driscoll–Kraay](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_nw_groupsum.html): implementação e pressuposto de dimensão temporal longa; foram usadas larguras explícitas e identificado o caráter aproximado.
- [statsmodels — KPSS](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.kpss.html): limites tabulados e avisos; os limites passaram a ser exportados separadamente.
- [ASA — Statement on statistical significance and p-values](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf): a decisão científica exige contexto e magnitude, além do valor-p. O conjunto de resultados e sensibilidades é apresentado.
- [scikit-learn — Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): fuga de informação entre treino e teste. Foi distinguida a análise explicativa retrospetiva da futura previsão.

As fontes orientaram a lista de verificação; a presença de um item na lista não significa que esse erro ocorria no conjunto de dados. “Corrigido” identifica uma falha concreta do código; “conferido” identifica uma verificação aprovada; riscos inferenciais e limitações dos dados são mantidos explicitamente.
