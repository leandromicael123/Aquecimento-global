"""Reconstrói os indicadores offline e compara com as entradas preservadas."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import pandas as pd


def verificar(raiz):
    pacote = raiz / "dados/reproducao"
    fontes = pd.read_csv(pacote / "fontes.csv")
    verificacoes = []
    for fonte in fontes.itertuples():
        p = pacote / fonte.ficheiro_original
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest == fonte.sha256, f"Fonte alterada: {p.name}"
        verificacoes.append({"ficheiro": fonte.ficheiro_original, "sha256": digest, "confere": True})
    subprocess.run([sys.executable, str(pacote / "construir_dataset.py")], check=True)
    for nome in ["painel_indicadores.csv", "dados_brutos_mensais.csv", "dados_brutos_anuais.csv"]:
        original = pd.read_csv(raiz / "dados/originais" / nome)
        reconstruido = pd.read_csv(pacote / nome)
        pd.testing.assert_frame_equal(original, reconstruido, rtol=1e-10, atol=1e-10)
    destino = raiz / "resultados/verificacao_fontes.json"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(json.dumps(verificacoes, indent=2), encoding="utf-8")
    print(f"{len(verificacoes)} fontes verificadas; três tabelas reconstruídas e iguais às entradas.")
    return verificacoes


if __name__ == "__main__":
    verificar(Path(__file__).resolve().parents[1])
