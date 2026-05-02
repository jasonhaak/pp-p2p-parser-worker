# -*- coding: utf-8 -*-
"""
Unit test for the public CSV text parser API.
"""
import os
import unittest

from src.p2p_statement_parser import parse_csv_text


class TestParseCsvText(unittest.TestCase):
    """Test case implementation for parse_csv_text"""

    def test_parse_csv_text_returns_portfolio_performance_csv(self):
        testdata = os.path.join(os.path.dirname(__file__), "testdata", "mintos.csv")
        with open(testdata, "r", encoding="utf-8-sig") as csv_input:
            output = parse_csv_text(csv_input.read(), provider="mintos", aggregate="transaction")

        self.assertTrue(output.startswith("Datum,Wert,Buchungswährung,Typ,Notiz"))
        self.assertIn("2018-01-17,20,EUR,Einlage,236659674: Incoming client payment", output)

    def test_parse_csv_text_rejects_unknown_provider(self):
        with self.assertRaises(ValueError):
            parse_csv_text("", provider="unknown", aggregate="transaction")


if __name__ == "__main__":
    unittest.main()
