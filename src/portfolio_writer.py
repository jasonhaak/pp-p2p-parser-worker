# -*- coding: utf-8 -*-
"""
Module for the portfolio performance writer

Copyright 2018-04-29 ChrisRBe
"""
import csv
import io
import logging
from decimal import Decimal


PP_FIELDNAMES = ["Datum", "Wert", "Buchungswährung", "Typ", "Notiz"]
PP_OUTPUT_LANGUAGES = ("de", "en")
PP_OUTPUT_FIELDNAMES = {
    "de": PP_FIELDNAMES,
    "en": ["Date", "Value", "Transaction Currency", "Type", "Note"],
}
PP_TYPE_TRANSLATIONS = {
    "en": {
        "Einlage": "Deposit",
        "Entnahme": "Withdrawal",
        "Zinsen": "Interest",
        "Gebühren": "Fees",
    },
}
PP_NOTE_TRANSLATIONS = {
    "en": {
        "Tageszusammenfassung": "Daily summary",
        "Monatszusammenfassung": "Monthly summary",
    },
}
logger = logging.getLogger(__name__)


class PortfolioPerformanceWriter(object):
    """
    Writing parsed Peer-to-Peer lending account statements to Portfolio Performance compatible format
    """

    def __init__(self, dialect="excel", output_language="de"):
        """
        constructor for class

        :param dialect: translates to the used CSV dialect, defaults to excel
        :param output_language: Portfolio Performance language for headers and transaction types
        """
        if output_language not in PP_OUTPUT_LANGUAGES:
            raise ValueError("Unsupported Portfolio Performance output language: {}".format(output_language))

        self.dialect = dialect
        self.output_language = output_language
        self.out_csv_fieldnames = PP_OUTPUT_FIELDNAMES[output_language]
        self.out_string_stream = io.StringIO()
        self.out_csv_writer = None

    def init_output(self):
        """
        Initialize output csv file
        """
        if not self.out_csv_writer:
            self.out_csv_writer = csv.DictWriter(
                f=self.out_string_stream,
                fieldnames=self.out_csv_fieldnames,
                dialect=self.dialect,
            )
            self.out_csv_writer.writeheader()

    def update_output(self, statement_dict):
        """
        Add a new line to the portfolio performance output file; format is a dictionary

        :param statement_dict: dictionary containing the fieldnames of the output file and the respective content as
        key value pair
        :return:
        """
        if statement_dict:
            self.out_csv_writer.writerow(self.__format_output_statement(statement_dict))

    def get_output(self):
        """
        Return the complete Portfolio Performance CSV output as a string.
        """
        return self.out_string_stream.getvalue().strip()

    def __format_output_statement(self, statement_dict):
        output_statement = {}
        for source_fieldname, output_fieldname in zip(PP_FIELDNAMES, self.out_csv_fieldnames):
            output_statement[output_fieldname] = statement_dict[source_fieldname]

        value_fieldname = PP_OUTPUT_FIELDNAMES[self.output_language][1]
        type_fieldname = PP_OUTPUT_FIELDNAMES[self.output_language][3]
        note_fieldname = PP_OUTPUT_FIELDNAMES[self.output_language][4]
        output_statement[value_fieldname] = PortfolioPerformanceWriter.format_value(output_statement[value_fieldname])
        output_statement[type_fieldname] = PP_TYPE_TRANSLATIONS.get(self.output_language, {}).get(
            output_statement[type_fieldname],
            output_statement[type_fieldname],
        )
        output_statement[note_fieldname] = PP_NOTE_TRANSLATIONS.get(self.output_language, {}).get(
            output_statement[note_fieldname],
            output_statement[note_fieldname],
        )
        return output_statement

    @staticmethod
    def format_value(value):
        """
        Format numeric values deterministically for Portfolio Performance CSV output.
        """
        formatted_value = "{:.8g}".format(Decimal(str(value)))
        if "." in formatted_value and "e" not in formatted_value.lower():
            formatted_value = formatted_value.rstrip("0").rstrip(".")
        return formatted_value.replace(".", ",")
