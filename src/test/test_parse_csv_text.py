# -*- coding: utf-8 -*-
"""
Unit test for the public CSV text parser API.
"""
import os
import unittest
from collections import Counter
from csv import DictReader
from io import StringIO

from src.p2p_statement_parser import ParserInputError
from src.p2p_statement_parser import detect_provider_from_csv_text
from src.p2p_statement_parser import parse_csv_text


class TestParseCsvText(unittest.TestCase):
    """Test case implementation for parse_csv_text"""

    def test_parse_csv_text_returns_portfolio_performance_csv(self):
        testdata = os.path.join(os.path.dirname(__file__), "testdata", "mintos.csv")
        with open(testdata, "r", encoding="utf-8-sig") as csv_input:
            output = parse_csv_text(csv_input.read(), provider="mintos_en", aggregate="transaction")

        self.assertTrue(output.startswith("Datum,Wert,Buchungswährung,Typ,Notiz"))
        self.assertIn("2018-01-17,20,EUR,Einlage,236659674: Incoming client payment", output)

    def test_parse_csv_text_rejects_unknown_provider(self):
        with self.assertRaises(ValueError):
            parse_csv_text("", provider="unknown", aggregate="transaction")

    def test_parse_csv_text_auto_detects_provider(self):
        testdata = os.path.join(os.path.dirname(__file__), "testdata", "mintos.csv")
        with open(testdata, "r", encoding="utf-8-sig") as csv_input:
            output = parse_csv_text(csv_input.read(), provider="auto", aggregate="transaction")

        self.assertIn("236659674: Incoming client payment", output)

    def test_detect_provider_from_csv_text(self):
        testdata = os.path.join(os.path.dirname(__file__), "testdata", "mintos_de.csv")
        with open(testdata, "r", encoding="utf-8-sig") as csv_input:
            self.assertEqual("mintos_de", detect_provider_from_csv_text(csv_input.read()))

    def test_parse_csv_text_reports_wrong_provider_headers(self):
        testdata = os.path.join(os.path.dirname(__file__), "testdata", "mintos_de.csv")
        with open(testdata, "r", encoding="utf-8-sig") as csv_input:
            with self.assertRaises(ParserInputError) as context:
                parse_csv_text(csv_input.read(), provider="mintos_en", aggregate="transaction")

        self.assertIn("This CSV looks like Mintos DE", str(context.exception))
        self.assertIn("Mintos EN is selected", str(context.exception))

    def test_parse_estateguru_de_csv_text(self):
        testdata = os.path.join(os.path.dirname(__file__), "testdata", "estateguru_de.csv")
        with open(testdata, "r", encoding="utf-8-sig") as csv_input:
            output = parse_csv_text(csv_input.read(), provider="estateguru_de", aggregate="transaction")

        rows = list(DictReader(StringIO(output)))
        categories = Counter(row["Typ"] for row in rows)
        self.assertEqual(33, len(rows))
        self.assertEqual(7, categories["Einlage"])
        self.assertEqual(20, categories["Zinsen"])
        self.assertEqual(6, categories["Gebühren"])
        self.assertEqual("EGDE-000003: Synthetic Project 003", rows[0]["Notiz"])

    def test_parse_mintos_de_csv_text(self):
        testdata = os.path.join(os.path.dirname(__file__), "testdata", "mintos_de.csv")
        with open(testdata, "r", encoding="utf-8-sig") as csv_input:
            output = parse_csv_text(csv_input.read(), provider="mintos_de", aggregate="transaction")

        rows = list(DictReader(StringIO(output)))
        categories = Counter(row["Typ"] for row in rows)
        self.assertEqual(655, len(rows))
        self.assertEqual(381, categories["Zinsen"])
        self.assertEqual(274, categories["Gebühren"])
        self.assertEqual(
            "MDE-0000001: ISIN: SYN000000001 (Darlehen SYN-000001) Erhaltene Zinsen",
            rows[0]["Notiz"],
        )


if __name__ == "__main__":
    unittest.main()
