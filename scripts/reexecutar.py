"""Executa os três notebooks pela ordem de leitura."""

import asyncio
import platform
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def executar_notebook(ficheiro):
    notebook = nbformat.read(ficheiro, as_version=4)
    cliente = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(ficheiro.parent)}},
    )
    cliente.execute()
    nbformat.validate(notebook)
    nbformat.write(notebook, ficheiro)
    n_celulas = sum(celula.cell_type == "code" for celula in notebook.cells)
    print(f"{ficheiro.name}: {n_celulas} células executadas sem erros.", flush=True)


def main():
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    raiz = Path(__file__).resolve().parents[1]
    for ficheiro in sorted((raiz / "notebooks").glob("*.ipynb")):
        executar_notebook(ficheiro)


if __name__ == "__main__":
    main()
