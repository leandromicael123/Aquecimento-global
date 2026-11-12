"""Executa os notebooks da Parte 1 pela ordem de leitura, no Python ativo."""

import asyncio
import platform
import sys
import json
import hashlib
import importlib.metadata
from datetime import datetime, timezone
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager


class KernelDoAmbiente(KernelSpecManager):
    """Evita usar por engano um kernel global sem as bibliotecas do projeto."""
    def get_kernel_spec(self, kernel_name):
        spec = super().get_kernel_spec(kernel_name)
        spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
        return spec


def executar_notebook(ficheiro):
    notebook = nbformat.read(ficheiro, as_version=4)
    cliente = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(ficheiro.parent)}},
    )
    cliente.create_kernel_manager()
    cliente.km.kernel_spec_manager = KernelDoAmbiente()
    cliente.execute()
    nbformat.validate(notebook)
    ficheiro.write_text(nbformat.writes(notebook), encoding="utf-8", newline="\n")
    n_celulas = sum(celula.cell_type == "code" for celula in notebook.cells)
    print(f"{ficheiro.name}: {n_celulas} células executadas sem erros.", flush=True)
    return {"notebook": ficheiro.name, "celulas_codigo": n_celulas, "erros": 0,
            "sha256": hashlib.sha256(ficheiro.read_bytes()).hexdigest()}


def executar_todos(raiz):
    raiz = Path(raiz)
    destino = raiz / "resultados/verificacao_execucao.json"
    destino.parent.mkdir(exist_ok=True)
    bibliotecas = ["pandas", "numpy", "matplotlib", "scipy", "statsmodels", "linearmodels", "nbclient", "nbformat", "ipykernel", "threadpoolctl"]
    registo = {"estado": "em_execucao", "inicio_utc": datetime.now(timezone.utc).isoformat(),
               "python": platform.python_version(), "notebooks": [],
               "bibliotecas": {nome: importlib.metadata.version(nome) for nome in bibliotecas}}
    destino.write_text(json.dumps(registo, ensure_ascii=False, indent=2), encoding="utf-8")
    ficheiros = sorted((raiz / "notebooks").glob("*.ipynb"))
    try:
        if not ficheiros:
            raise ValueError("Não foram encontrados notebooks para executar.")
        for ficheiro in ficheiros:
            registo["notebooks"].append(executar_notebook(ficheiro))
        registo["estado"] = "concluido"
    except Exception as erro:
        registo["estado"] = "falhou"
        registo["erro"] = f"{type(erro).__name__}: {erro}"
        raise
    finally:
        registo["fim_utc"] = datetime.now(timezone.utc).isoformat()
        registo["scripts_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in sorted((raiz / "scripts").glob("*.py"))}
        destino.write_text(json.dumps(registo, ensure_ascii=False, indent=2), encoding="utf-8")
    return registo


def main():
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    executar_todos(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    main()
