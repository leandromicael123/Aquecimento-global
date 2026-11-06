# Aquecimento global e inflação alimentar

Trabalho de Modelos Longitudinais — preparação, exploração e diagnóstico de um painel mensal de 15 países, de fevereiro de 2000 a dezembro de 2025.

## Ordem de leitura

1. `notebooks/01_preparacao_e_qualidade.ipynb`: perguntas de investigação, variáveis, unidades, cobertura, omissos, sinalização de extremos e conferência das transformações.
2. `notebooks/02_exploracao_visual.ipynb`: estatísticas, trajetórias, distribuições, evolução agregada e variabilidade entre e dentro dos países.
3. `notebooks/03_diagnosticos_e_alteracoes.ipynb`: sazonalidade, autocorrelação, movimentos comuns, extremos, amostras comparáveis e alterações propostas para a modelação.

Cada notebook contém resultados executados, gráficos e interpretações. Pode ser executado autonomamente. Os modelos de painel finais ainda não foram estimados.

## Organização dos ficheiros

```text
Trabalho/
├── dados/
│   ├── originais/          # Entradas fornecidas, preservadas sem alterações
│   ├── processados/        # Painel longo verificado e ordenado
│   └── modelacao/          # Amostras por especificação e amostra comum
├── notebooks/              # Três documentos de análise, pela ordem acima
├── scripts/
│   ├── preparacao.py       # Leitura, qualidade e conferência dos dados
│   ├── exploracao.py       # Estatísticas e medidas de dispersão
│   ├── diagnosticos.py     # Testes, extremos e propostas de alteração
│   ├── graficos.py         # Uma função por figura
│   ├── estilo_iscte.py     # Cores, rótulos e apresentação das tabelas
│   └── reexecutar.py       # Executa os notebooks pela ordem de leitura
├── resultados/
│   ├── tabelas/            # CSV e registo de qualidade JSON, por etapa
│   │   ├── 01_preparacao/
│   │   ├── 02_exploracao/
│   │   └── 03_diagnosticos/
│   └── graficos/           # Cada figura em PNG e SVG, por etapa
│       ├── 02_exploracao/
│       └── 03_diagnosticos/
├── requirements.txt
└── README.md
```

Os nomes e números das figuras correspondem aos ficheiros exportados. Os ficheiros Python contêm funções com nomes descritivos; os notebooks apresentam as chamadas, resultados e interpretação.

## Executar

Ambiente usado: Python 3.12. Na pasta `Trabalho`, instalar as dependências e executar:

```bash
python -m pip install -r requirements.txt
python scripts/reexecutar.py
```

Para trabalho interativo, abrir os `.ipynb` no VS Code com a extensão Jupyter ou no JupyterLab. Escolher um kernel Python com as dependências instaladas. Os notebooks localizam os dados quer sejam abertos a partir da raiz, quer a partir de `notebooks/`.

## Convenções de leitura

- Os dados originais não são sobrescritos por nenhum notebook.
- A inflação é uma taxa logarítmica mensal, aproximadamente percentual; não é a taxa homóloga.
- As covariáveis económicas são anuais, desfasadas um ano e repetidas nos meses. Não foram interpoladas.
- Os extremos são sinalizados e verificados, sem exclusão automática. A sensibilidade com limites de quantis é apenas um cenário separado.
- As figuras apresentam títulos, eixos, unidades, legenda quando necessária e fonte. São guardadas em PNG e SVG.
- As tabelas de resultados mantêm os nomes técnicos nos CSV para facilitar reprodução; o notebook oferece rótulos explicativos.

## Estilo e referências

O azul institucional Iscte é `#0D28C2` (RGB 13, 40, 194), conforme o [Manual de Marca, secção Cor](https://cies.iscte.pt/np4/?fileName=manual_de_marca_versao_digital_marco_202.pdf&newsId=3485). Branco e cinzentos compõem a base. Cores de contraste distinguem séries e sinais nas figuras, sem pretensão de certificar uma aplicação oficial da marca. A tipografia usa Montserrat quando instalada, com alternativa legível local.

As fontes, versões e limitações dos dados constam de `dados/originais/fontes.csv`, `dicionario_variaveis.csv` e `metodologia_original.txt`. A documentação técnica dos testes está citada no notebook 03.
