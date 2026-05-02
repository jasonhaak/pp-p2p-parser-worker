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
logger = logging.getLogger(__name__)


class PortfolioPerformanceWriter(object):
    """
    Writing parsed Peer-to-Peer lending account statements to Portfolio Performance compatible format
    """

    def __init__(self, dialect="excel"):
        """
        constructor for class

        :param dialect: translates to the used CSV dialect, defaults to excel
        """
        self.dialect = dialect
        self.out_csv_fieldnames = PP_FIELDNAMES
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
            statement_dict[PP_FIELDNAMES[1]] = PortfolioPerformanceWriter.format_value(
                statement_dict[PP_FIELDNAMES[1]]
            )
            self.out_csv_writer.writerow(statement_dict)

    def get_output(self):
        """
        Return the complete Portfolio Performance CSV output as a string.
        """
        return self.out_string_stream.getvalue().strip()

    @staticmethod
    def format_value(value):
        """
        Format numeric values deterministically for Portfolio Performance CSV output.
        """
        formatted_value = "{:.8g}".format(Decimal(str(value)))
        if "." in formatted_value and "e" not in formatted_value.lower():
            formatted_value = formatted_value.rstrip("0").rstrip(".")
        return formatted_value.replace(".", ",")
