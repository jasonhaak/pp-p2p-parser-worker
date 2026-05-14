# -*- coding: utf-8 -*-
"""
Unit test for the portfolio performance writer module

Copyright 2018-04-29 ChrisRBe
"""
from unittest import TestCase

from src.portfolio_writer import PortfolioPerformanceWriter
from src.portfolio_writer import PP_FIELDNAMES


class TestPortfolioPerformanceWriter(TestCase):
    """Test case implementation for PortfolioPerformanceWriter"""

    def setUp(self):
        """test case setUp, run for each test case"""
        self.pp_writer = PortfolioPerformanceWriter()
        self.pp_writer.init_output()

    def test_init_output(self):
        """test init_output"""
        self.assertEqual(",".join(PP_FIELDNAMES), self.pp_writer.out_string_stream.getvalue().strip())

    def test_update_output(self):
        """test update_output"""
        test_entry = {
            PP_FIELDNAMES[0]: "date",
            PP_FIELDNAMES[1]: 123.456789,
            PP_FIELDNAMES[2]: "currency",
            PP_FIELDNAMES[3]: "category",
            PP_FIELDNAMES[4]: "note",
        }
        self.pp_writer.update_output(test_entry)
        self.assertEqual(
            'Datum,Wert,Buchungswährung,Typ,Notiz\r\ndate,"123,45679",currency,category,note',
            self.pp_writer.out_string_stream.getvalue().strip(),
        )

    def test_update_output_english(self):
        """test update_output with English Portfolio Performance labels"""
        pp_writer = PortfolioPerformanceWriter(output_language="en")
        pp_writer.init_output()
        test_entry = {
            PP_FIELDNAMES[0]: "date",
            PP_FIELDNAMES[1]: 123.456789,
            PP_FIELDNAMES[2]: "currency",
            PP_FIELDNAMES[3]: "Zinsen",
            PP_FIELDNAMES[4]: "note",
        }
        pp_writer.update_output(test_entry)
        self.assertEqual(
            'Date,Value,Transaction Currency,Type,Note\r\ndate,"123,45679",currency,Interest,note',
            pp_writer.out_string_stream.getvalue().strip(),
        )

    def test_update_output_english_translates_summary_notes(self):
        """test update_output translates generated aggregation notes"""
        pp_writer = PortfolioPerformanceWriter(output_language="en")
        pp_writer.init_output()
        test_entry = {
            PP_FIELDNAMES[0]: "date",
            PP_FIELDNAMES[1]: 12.34,
            PP_FIELDNAMES[2]: "currency",
            PP_FIELDNAMES[3]: "Zinsen",
            PP_FIELDNAMES[4]: "Monatszusammenfassung",
        }
        pp_writer.update_output(test_entry)
        self.assertEqual(
            'Date,Value,Transaction Currency,Type,Note\r\ndate,"12,34",currency,Interest,Monthly summary',
            pp_writer.out_string_stream.getvalue().strip(),
        )

    def test_rejects_unknown_output_language(self):
        """test unsupported output language validation"""
        with self.assertRaises(ValueError):
            PortfolioPerformanceWriter(output_language="fr")

    def test_update_output_umlaut(self):
        """test update_output with umlauts"""
        test_entry = {
            PP_FIELDNAMES[0]: "date",
            PP_FIELDNAMES[1]: 0.123456789,
            PP_FIELDNAMES[2]: "currency",
            PP_FIELDNAMES[3]: "category",
            PP_FIELDNAMES[4]: "Laiamäe Pärnaõie Užutekio",
        }
        self.pp_writer.update_output(test_entry)
        self.assertEqual(
            'Datum,Wert,Buchungswährung,Typ,Notiz\r\ndate,"0,12345679",currency,category,Laiamäe Pärnaõie Užutekio',
            self.pp_writer.out_string_stream.getvalue().strip(),
        )

    def test_update_output_is_locale_independent(self):
        """test update_output formats values deterministically"""
        test_entry = {
            PP_FIELDNAMES[0]: "date",
            PP_FIELDNAMES[1]: 0.123456789,
            PP_FIELDNAMES[2]: "currency",
            PP_FIELDNAMES[3]: "category",
            PP_FIELDNAMES[4]: "Laiamäe Pärnaõie Užutekio",
        }
        self.pp_writer.update_output(test_entry)
        self.assertEqual(
            'Datum,Wert,Buchungswährung,Typ,Notiz\r\ndate,"0,12345679",currency,category,Laiamäe Pärnaõie Užutekio',
            self.pp_writer.out_string_stream.getvalue().strip(),
        )

    def test_get_output(self):
        """test get_output"""
        self.assertEqual(",".join(PP_FIELDNAMES), self.pp_writer.get_output())
