# -*- coding: utf-8 -*-
"""
Module for a generic peer to peer loan account statement parser.

Copyright 2018-04-29 ChrisRBe
"""
import calendar
import codecs
import csv
import io
import logging
import os

try:
    from src.p2p_config import Config
    from src.portfolio_writer import PP_FIELDNAMES
    from src.portfolio_writer import PP_OUTPUT_LANGUAGES
    from src.portfolio_writer import PortfolioPerformanceWriter
    from src.provider_configs import PROVIDER_CONFIGS
    from src.statement import Statement
except ModuleNotFoundError as exc:
    if exc.name != "src":
        raise
    from p2p_config import Config
    from portfolio_writer import PP_FIELDNAMES
    from portfolio_writer import PP_OUTPUT_LANGUAGES
    from portfolio_writer import PortfolioPerformanceWriter
    from provider_configs import PROVIDER_CONFIGS
    from statement import Statement


logger = logging.getLogger(__name__)
SUPPORTED_AGGREGATES = ["transaction", "daily", "monthly"]
PROVIDER_LABELS = {
    "bondora": "Bondora",
    "bondora_go_grow": "Bondora Go & Grow",
    "debitumnetwork": "Debitum Network",
    "estateguru_de": "Estateguru DE",
    "estateguru_de_legacy": "Estateguru DE Legacy",
    "estateguru_en": "Estateguru EN",
    "lande": "Lande",
    "mintos_de": "Mintos DE",
    "mintos_en": "Mintos EN",
    "robocash": "Robocash",
    "swaper": "Swaper",
    "viainvest": "Viainvest",
}


class ParserInputError(ValueError):
    """Raised when uploaded CSV content does not match the selected provider."""


def format_provider_label(provider):
    """
    Return a user-facing provider label.
    """
    return PROVIDER_LABELS.get(provider, provider)


def get_csv_headers(csv_text):
    """
    Return the header row from uploaded CSV text.
    """
    if not csv_text or not csv_text.strip():
        raise ParserInputError("The uploaded CSV file is empty.")

    with io.StringIO(csv_text.lstrip("\ufeff")) as infile:
        sample = infile.read(4096)
        infile.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error as exc:
            raise ParserInputError("The uploaded file is not a readable CSV file.") from exc

        reader = csv.reader(infile, dialect=dialect)
        try:
            headers = next(reader)
        except StopIteration as exc:
            raise ParserInputError("The uploaded CSV file has no header row.") from exc

    headers = [header.strip() for header in headers if header and header.strip()]
    if not headers:
        raise ParserInputError("The uploaded CSV file has no header row.")
    return headers


def get_required_headers(provider):
    """
    Return CSV headers required by a provider configuration.
    """
    csv_fieldnames = PROVIDER_CONFIGS[provider]["csv_fieldnames"]
    required_keys = ["booking_date", "booking_details", "booking_id", "booking_type", "booking_value"]
    if csv_fieldnames.get("booking_currency"):
        required_keys.append("booking_currency")
    return [csv_fieldnames[key] for key in required_keys]


def detect_provider_from_csv_text(csv_text):
    """
    Detect a supported provider by matching the uploaded CSV header row.
    """
    headers = set(get_csv_headers(csv_text))
    matches = []

    for provider in PROVIDER_CONFIGS:
        required_headers = set(get_required_headers(provider))
        if required_headers.issubset(headers):
            matches.append(provider)

    if not matches:
        return None
    return matches[0]


def validate_provider_headers(csv_text, provider):
    """
    Ensure uploaded CSV headers match the selected provider.
    """
    headers = set(get_csv_headers(csv_text))
    required_headers = set(get_required_headers(provider))
    missing_headers = sorted(required_headers - headers)

    if missing_headers:
        detected_provider = detect_provider_from_csv_text(csv_text)
        if detected_provider:
            detected_label = format_provider_label(detected_provider)
            selected_label = format_provider_label(provider)
            message = (
                "This CSV looks like {}, but {} is selected. "
                "Switch to provider {} or choose Auto-Detect and try again."
            ).format(detected_label, selected_label, detected_label)
        else:
            message = (
                "This CSV does not match {}. Choose Auto-Detect or select the correct provider and try again. "
                "Missing required column(s): {}."
            ).format(format_provider_label(provider), ", ".join(missing_headers))
        raise ParserInputError(message)


def parse_csv_text(csv_text, provider="mintos_en", aggregate="transaction", output_language="de"):
    """
    Parse uploaded account statement CSV content and return Portfolio Performance CSV content.

    :param csv_text: account statement CSV data as text
    :param provider: supported P2P lending provider name
    :param aggregate: transaction, daily, or monthly
    :param output_language: Portfolio Performance output language, de or en
    :return: Portfolio Performance CSV data as text, or False if no matching statements were found
    """
    if output_language not in PP_OUTPUT_LANGUAGES:
        raise ValueError("Unsupported Portfolio Performance output language: {}".format(output_language))

    if provider == "auto":
        provider = detect_provider_from_csv_text(csv_text)
        if not provider:
            raise ParserInputError("The uploaded CSV does not match any supported provider format.")

    if provider not in PROVIDER_CONFIGS:
        raise ValueError("The provided platform {} is currently not supported".format(provider))

    validate_provider_headers(csv_text, provider)

    platform_parser = PeerToPeerPlatformParser(config=PROVIDER_CONFIGS[provider])
    statement_list = platform_parser.parse_account_statement_text(csv_text=csv_text, aggregate=aggregate)

    if not statement_list:
        return False

    writer = PortfolioPerformanceWriter(output_language=output_language)
    writer.init_output()
    for entry in statement_list:
        writer.update_output(entry)
    return writer.get_output()


class PeerToPeerPlatformParser(object):
    """
    Implementation of a generic p2p investment platform account statement parser.
    Actual configuration for the individual services is done via a yml config file.
    """

    def __init__(self, config, infile=None):
        """
        Constructor for PeerToPeerPlatformParser
        """
        self._account_statement_file = infile
        self._config_file = config

        self.config = None
        self.output_list = []
        self.aggregation_data = {}

    @property
    def account_statement_file(self):
        """account statement file property"""
        return self._account_statement_file

    @account_statement_file.setter
    def account_statement_file(self, value):
        """account statement file property setter"""
        self._account_statement_file = value

    @property
    def config_file(self):
        """config file property"""
        return self._config_file

    @config_file.setter
    def config_file(self, value):
        """config file property setter"""
        self._config_file = value

    def __aggregate_statements(self, formatted_account_entry, comment, monthly=True):
        entry_date = formatted_account_entry[PP_FIELDNAMES[0]]
        if monthly:
            last_day = calendar.monthrange(entry_date.year, entry_date.month)[1]
            entry_date = entry_date.replace(day=last_day)

        entry_type = formatted_account_entry[PP_FIELDNAMES[3]]
        entry_value = formatted_account_entry[PP_FIELDNAMES[1]]
        entry_currency = formatted_account_entry[PP_FIELDNAMES[2]]

        logger.debug("entry type is %s. new entry date is %s. value of entry: %s", entry_type, entry_date, entry_value)
        if entry_date not in self.aggregation_data:
            self.aggregation_data[entry_date] = {}
        if entry_type in self.aggregation_data[entry_date]:
            logger.debug("add to existing entry")
            self.aggregation_data[entry_date][entry_type][PP_FIELDNAMES[1]] += entry_value
        else:
            self.aggregation_data[entry_date][entry_type] = {
                PP_FIELDNAMES[0]: entry_date,
                PP_FIELDNAMES[1]: entry_value,
                PP_FIELDNAMES[2]: entry_currency,
                PP_FIELDNAMES[3]: entry_type,
                PP_FIELDNAMES[4]: comment,
            }

    def __aggregate_statements_daily(self, formatted_account_entry):
        self.__aggregate_statements(formatted_account_entry, "Tageszusammenfassung", False)

    def __aggregate_statements_monthly(self, formatted_account_entry):
        self.__aggregate_statements(formatted_account_entry, "Monatszusammenfassung", True)

    def __format_statement(self, statement):
        """
        Formats a given statement into a dictionary containing the relevant data for Portfolio Performance.

        :param statement: contains a line from the given CSV file

        :return: dictionary containing the formatted account entry
        """
        statement = Statement(self.config, statement)
        category = statement.get_category()

        if not category or category == "Ignored":
            return

        formatted_account_entry = {
            PP_FIELDNAMES[0]: statement.get_date(),
            PP_FIELDNAMES[1]: round(statement.get_value(), 9),
            PP_FIELDNAMES[2]: statement.get_currency(),
            PP_FIELDNAMES[3]: category,
            PP_FIELDNAMES[4]: statement.get_note(),
        }
        return formatted_account_entry

    def __migrate_data_to_output(self):
        """
        Iterates over the data collected for the aggregation of account statement data and adds it to the output list.
        :return:
        """
        for _, booking_type in self.aggregation_data.items():
            for _, entry in booking_type.items():
                entry[PP_FIELDNAMES[1]] = round(entry[PP_FIELDNAMES[1]], 9)
                self.output_list.append(entry)

    def __parse_service_config(self):
        """
        Load the bundled configuration for the individual p2p loan platform.
        """
        if isinstance(self.config_file, dict):
            self.config = Config(self.config_file)
        else:
            provider = os.path.splitext(os.path.basename(self.config_file))[0]
            if provider in PROVIDER_CONFIGS:
                self.config = Config(PROVIDER_CONFIGS[provider])
                return
            raise ValueError("The provided platform {} is currently not supported".format(provider))

    def __reset_output(self):
        self.output_list = []
        self.aggregation_data = {}

    def __validate_aggregate(self, aggregate):
        if aggregate in SUPPORTED_AGGREGATES:
            logger.info("Aggregating data on a {} basis".format(aggregate))
            return True

        logger.error("Aggregating data on a {} basis not supported.".format(aggregate))
        return False

    def __parse_account_statement_stream(self, infile, aggregate="transaction"):
        dialect = csv.Sniffer().sniff(infile.readline())
        infile.seek(0)
        account_statement = csv.DictReader(infile, dialect=dialect)

        for statement in account_statement:
            self.__process_statement(aggregate=aggregate, statement=statement)

        if aggregate == "daily" or aggregate == "monthly":
            self.__migrate_data_to_output()
        return self.output_list

    def parse_account_statement_text(self, csv_text, aggregate="transaction"):
        """
        Parse account statement CSV text with the parser's configured platform settings.

        :param csv_text: account statement CSV data as text
        :param aggregate: specifies the aggregation period. defaults to transaction.
        :return: list of account statement entries ready for use in Portfolio Performance
        """
        self.__reset_output()
        if not self.__validate_aggregate(aggregate):
            return

        self.__parse_service_config()

        logger.info("Loading account statement")
        with io.StringIO(csv_text.lstrip("\ufeff")) as infile:
            return self.__parse_account_statement_stream(infile, aggregate=aggregate)

    def __process_statement(self, statement, aggregate="transaction"):
        """
        Processes each statement read from the account statement file. First, format in into the dictionary.
        Then check what aggregation should be applied.

            - transaction: add directly to the output list.
            - daily: add it to intermediate aggregation collection.
            - monthly: add it to intermediate aggregation collection.

        :param statement: Contains one line from the account statement file
        :param aggregate: specify the aggregation format; e.g. daily or monthly. Defaults to transaction.

        :return:
        """
        formatted_account_entry = self.__format_statement(statement)
        if formatted_account_entry:
            if aggregate == "transaction":
                self.output_list.append(formatted_account_entry)
            elif aggregate == "daily":
                self.__aggregate_statements_daily(formatted_account_entry)
            elif aggregate == "monthly":
                self.__aggregate_statements_monthly(formatted_account_entry)

    def parse_account_statement(self, aggregate="transaction"):
        """
        read a platform account statement csv file and filter the content according to the given configuration file.
        If aggregation is selected the output data will be post processed in the following way:

        - aggregate="transaction": return the list of processed statements as is.
        - aggregate="daily": return a list of post-processed statements aggregating on daily basis for each
          booking type.
        - aggregate="monthly": return a list of post-processed statements aggregating on monthly basis for each
          booking type.

        :param aggregate: specifies the aggregation period. defaults to daily.
        :return: list of account statement entries ready for use in Portfolio Performance
        """
        self.__reset_output()
        if not self.__validate_aggregate(aggregate):
            return

        if not self._account_statement_file or not os.path.exists(self._account_statement_file):
            logger.error("provided file %s does not exist", self._account_statement_file)
            return False

        self.__parse_service_config()
        logger.info("Loading account statement")
        with codecs.open(self._account_statement_file, "r", encoding="utf-8-sig") as infile:
            return self.__parse_account_statement_stream(infile, aggregate=aggregate)
