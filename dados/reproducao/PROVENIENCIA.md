# Origem deste pacote

Recuperado de `Dataset_Aquecimento_Global_2000_2025 (2).zip`, disponível localmente nos Downloads, em 11 de novembro de 2026. SHA-256 do ZIP:

`4ae92bd6ab4c19a75d1d9bace5cd43b11f00a61cc7c1b4167a5ecdae08329159`

O `painel_indicadores.csv` no arquivo coincide byte a byte com o painel de `dados/originais/`. Foram copiados o código, as fontes e os CSV; o ficheiro Excel redundante foi omitido. O script original foi lido antes da execução e preservado. As condições e versões de cada fonte constam do manifesto original.

Para reconstruir e verificar a partir da raiz do projeto:

```bash
python scripts/verificar_reproducao.py
```

O comando confere os 51 SHA-256, executa `construir_dataset.py` nesta pasta e compara o resultado com as três tabelas preservadas em `dados/originais/`. O histórico de clima e as normais são recalculados, permitindo reproduzir a anomalia e o défice hídrico. Não são necessários novos descarregamentos.

O documento `dados/originais/metodologia_original.txt` descreve a estrutura do pacote de origem e mantém o seu valor documental. O seu comando `python construir_dataset.py` deve ser executado nesta pasta. O estado atual dos modelos é descrito no README da raiz e no notebook 04, não no texto histórico do pacote.
