"""Casos adversos encontrados na auditoria, sem alterar os dados de origem."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from preparacao import ler_painel, resumir_cobertura, conferir_transformacoes
from modelos_painel import preparar, hausman, TERMOS
from reexecutar import executar_todos
from sintese_parte1 import numero, gerar


class ValidacaoDados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = ler_painel(RAIZ / "dados/originais")

    def test_data_fora_grelha(self):
        extra = self.dados.iloc[[0]].copy()
        extra["data"] += pd.Timedelta(days=1)
        resumo, _ = resumir_cobertura(pd.concat([self.dados, extra], ignore_index=True))
        self.assertFalse(resumo["equilibrado"])
        self.assertEqual(resumo["pares_fora_grelha"], 1)

    def test_mes_ausente(self):
        resumo, _ = resumir_cobertura(self.dados.iloc[1:])
        self.assertFalse(resumo["equilibrado"])
        self.assertEqual(resumo["pares_ausentes"], 1)

    def test_nao_finitos(self):
        for valor in [np.nan, np.inf, -np.inf]:
            with self.subTest(valor=valor):
                d = self.dados.copy()
                d.loc[0, "anomalia_temperatura_c"] = valor
                with self.assertRaises(ValueError):
                    preparar(d)

    def test_ano_economico(self):
        d = self.dados.copy()
        d.loc[0, "ano_dados_economicos"] += 1
        with self.assertRaisesRegex(ValueError, "económico"):
            preparar(d)

    def test_covariavel_anual_nao_pode_variar_dentro_do_ano(self):
        d = self.dados.copy()
        d.loc[0, "peso_agricola_pct_ano_anterior"] += 1
        with self.assertRaisesRegex(ValueError, "anual"):
            preparar(d)

    def test_omisso_na_fonte_agricola(self):
        anual = pd.read_csv(RAIZ / "dados/originais/dados_brutos_anuais.csv")
        anual.loc[0, "peso_agricola_pct_pib"] = np.nan
        with tempfile.TemporaryDirectory() as pasta:
            anual.to_csv(Path(pasta)/"dados_brutos_anuais.csv", index=False)
            with self.assertRaisesRegex(ValueError, "Fonte anual"):
                conferir_transformacoes(self.dados, pasta)

    def test_ordem_da_entrada_nao_altera_preparacao(self):
        a, ca = preparar(self.dados)
        b, cb = preparar(self.dados.sample(frac=1, random_state=27))
        pd.testing.assert_frame_equal(a, b)
        self.assertEqual(ca, cb)


class InferenciaERelato(unittest.TestCase):
    def test_hausman_recusa_amostras_diferentes(self):
        with self.assertRaisesRegex(ValueError, "mesmos pares"):
            hausman({"amostra": pd.Index([1, 2])}, {"amostra": pd.Index([1, 3])})

    def test_hausman_nao_forca_matriz_indefinida(self):
        base = {"amostra": pd.Index([1, 2]), "beta": pd.Series(0., index=TERMOS), "sigma2": 1.}
        fe = dict(base, cov_classica=pd.DataFrame(np.eye(4), index=TERMOS, columns=TERMOS))
        re = dict(base, cov_classica=pd.DataFrame(2*np.eye(4), index=TERMOS, columns=TERMOS))
        h = hausman(fe, re)
        self.assertFalse(h["matriz_positiva"])
        self.assertIsNone(h["p_valor"])

    def test_valor_nao_disponivel(self):
        self.assertEqual(numero(None), "não disponível")

    def test_sintese_recusa_snapshot_alterado(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            p = raiz / "dados/originais"
            p.mkdir(parents=True)
            (p / "painel_indicadores.csv").write_text("dados alterados", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "entrada mudou"):
                gerar(raiz)

    def test_execucao_falhada_nao_deixa_sucesso_antigo(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            (raiz / "notebooks").mkdir()
            for nome in ["01.ipynb", "02.ipynb"]:
                (raiz / "notebooks" / nome).touch()
            (raiz / "resultados").mkdir()
            destino = raiz / "resultados/verificacao_execucao.json"
            destino.write_text('{"estado":"concluido"}', encoding="utf-8")
            with patch("reexecutar.executar_notebook", side_effect=[{"notebook": "01.ipynb"}, RuntimeError("falha simulada")]):
                with self.assertRaisesRegex(RuntimeError, "falha simulada"):
                    executar_todos(raiz)
            r = json.loads(destino.read_text(encoding="utf-8"))
            self.assertEqual(r["estado"], "falhou")
            self.assertEqual(len(r["notebooks"]), 1)


if __name__ == "__main__":
    unittest.main()
