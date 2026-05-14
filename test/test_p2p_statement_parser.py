# -*- coding: utf-8 -*-
"""
Unit test for the p2p account statement parser module

Copyright 2018-05-01 ChrisRBe
"""
import datetime
import os
import unittest

from src.p2p_statement_parser import PeerToPeerPlatformParser


class TestBaseParser(unittest.TestCase):
    """Test case implementation for PeerToPeerPlatformParser"""

    def setUp(self):
        """test case setUp, run for each test case"""
        self.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "mintos.csv")
        self.config_file = os.path.join(os.path.dirname(__file__), os.pardir, "config", "mintos_en.yml")
        self.base_parser = PeerToPeerPlatformParser(infile=self.account_statement_file, config=self.config_file)
        self.maxDiff = None

    def test_account_statement_file(self):
        """test account statement file property"""
        self.assertEqual(
            os.path.join(os.path.dirname(__file__), "testdata", "mintos.csv"),
            self.base_parser.account_statement_file,
        )

    def test_config_file(self):
        """test config file property"""
        self.assertEqual(
            os.path.join(os.path.dirname(__file__), os.pardir, "config", "mintos_en.yml"),
            self.base_parser.config_file,
        )

    def test_bondora_parsing(self):
        """test parse_account_statement for bondora"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "bondora.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "bondora.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2019, 1, 1),
                "Note": ": TransferDeposit|DE1111000000111111",
                "Type": "Deposit",
                "Value": 100.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2019, 1, 2),
                "Note": ": TransferGoGrow",
                "Type": "Withdrawal",
                "Value": -100.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2019, 1, 3),
                "Note": ": TransferDeposit|Wirecard",
                "Type": "Deposit",
                "Value": 100.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2019, 1, 4),
                "Note": "1111111-111111112: TransferInterestRepaiment",
                "Type": "Interest",
                "Value": 0.006792079,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2019, 1, 5),
                "Note": "1111111-111111113: TransferExtraInterestRepaiment",
                "Type": "Interest",
                "Value": 7.0588e-05,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement())

    def test_bondora_go_grow_parsing(self):
        """test parse_account_statement for bondora"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "bondora.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            "config",
            "bondora_go_grow.yml",
        )
        expected_statement = [
            {
                "Date": datetime.date(2019, 1, 2),
                "Note": ": TransferGoGrow",
                "Type": "Deposit",
                "Value": -100.0,
                "Currency": "EUR",
            }
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement())

    def test_estateguru_parsing(self):
        """test parse_account_statement for estateguru"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "estateguru.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "estateguru_de_legacy.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 18),
                "Note": "18012018204714DEP: ",
                "Type": "Deposit",
                "Value": 1000.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 23),
                "Note": "23012018092020DEP: ",
                "Type": "Deposit",
                "Value": 1000.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 24),
                "Note": "24012018000000REFEE5975: Kaerepere business loan 2. stage",
                "Type": "Interest",
                "Value": 0.25,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 24),
                "Note": "24012018000346WIT: ",
                "Type": "Withdrawal",
                "Value": -1000.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 30),
                "Note": "30012018000000REFEE4182: Laiamäe bridge loan",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 24),
                "Note": "24022018000000INTEE5975: Kaerepere business loan 2. stage",
                "Type": "Interest",
                "Value": 0.46,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 27),
                "Note": "27022018225240DEP: ",
                "Type": "Deposit",
                "Value": 1000.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 3, 1),
                "Note": "01032018000000BONLT2293: Grevitas construction loan",
                "Type": "Interest",
                "Value": 0.47,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 3, 15),
                "Note": "15032018000000INTLT0689: Užutekio bridge loan",
                "Type": "Interest",
                "Value": 0.59,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 4, 8),
                "Note": "08042018000000INTEE3186: Pärnaõie st bridge loan",
                "Type": "Interest",
                "Value": 0.46,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement())

    def test_mintos_parsing(self):
        """test parse_account_statement for mintos"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "mintos.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "mintos_en.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 17),
                "Note": "236659674: Incoming client payment",
                "Type": "Deposit",
                "Value": 20.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 18),
                "Note": "237974500: Interest income Loan ID: 2049443-01",
                "Type": "Interest",
                "Value": 0.005555556,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 19),
                "Note": "238112163: Interest income on rebuy Rebuy purpose: "
                "agreement_amendment Loan ID: 2198495-01",
                "Type": "Interest",
                "Value": 0.003777778,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 19),
                "Note": "238112984: Interest income on rebuy Rebuy purpose: early_repayment " "Loan ID: 2202538-01",
                "Type": "Interest",
                "Value": 0.003083333,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 25),
                "Note": "241699935: Late payment fee income Loan ID: 1529173-01",
                "Type": "Interest",
                "Value": 0.001214211,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 29),
                "Note": "243559685: Delayed interest income on rebuy Rebuy purpose: "
                "agreement_amendment Loan ID: 2198503-01",
                "Type": "Interest",
                "Value": 0.000342077,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 27),
                "Note": "260918485: Cashback bonus",
                "Type": "Interest",
                "Value": 0.3,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2016, 9, 28),
                "Note": "115013710: Withdraw application",
                "Type": "Withdrawal",
                "Value": -20.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 4, 10),
                "Note": "178363724: Loan 28375000-01 - discount/premium for secondary market transaction 178363274.",
                "Type": "Fees",
                "Value": -0.145454545,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 4, 10),
                "Note": "178363725: Loan 28375000-01 - discount/premium for secondary market transaction 178363275.",
                "Type": "Interest",
                "Value": 0.505454545,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(1970, 1, 1),
                "Note": "127373922: Loan 35287609-01 - interest received (no date for testing)",
                "Type": "Interest",
                "Value": 0.5,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement())

    def test_mintos_parsing_daily_aggregation(self):
        """test parse_account_statement for mintos"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "mintos.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "mintos_en.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 17),
                "Note": "Daily summary",
                "Type": "Deposit",
                "Value": 20.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 18),
                "Note": "Daily summary",
                "Type": "Interest",
                "Value": 0.005555556,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 19),
                "Note": "Daily summary",
                "Type": "Interest",
                "Value": 0.006861111,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 25),
                "Note": "Daily summary",
                "Type": "Interest",
                "Value": 0.001214211,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 29),
                "Note": "Daily summary",
                "Type": "Interest",
                "Value": 0.000342077,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 27),
                "Note": "Daily summary",
                "Type": "Interest",
                "Value": 0.3,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2016, 9, 28),
                "Note": "Daily summary",
                "Type": "Withdrawal",
                "Value": -20.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 4, 10),
                "Note": "Daily summary",
                "Type": "Fees",
                "Value": -0.145454545,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 4, 10),
                "Note": "Daily summary",
                "Type": "Interest",
                "Value": 0.505454545,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(1970, 1, 1),
                "Note": "Daily summary",
                "Type": "Interest",
                "Value": 0.5,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement(aggregate="daily"))

    def test_mintos_parsing_transaction_aggregation(self):
        """test parse_account_statement for mintos"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "mintos.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "mintos_en.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 17),
                "Note": "236659674: Incoming client payment",
                "Type": "Deposit",
                "Value": 20.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 18),
                "Note": "237974500: Interest income Loan ID: 2049443-01",
                "Type": "Interest",
                "Value": 0.005555556,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 19),
                "Note": "238112163: Interest income on rebuy Rebuy purpose: "
                "agreement_amendment Loan ID: 2198495-01",
                "Type": "Interest",
                "Value": 0.003777778,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 19),
                "Note": "238112984: Interest income on rebuy Rebuy purpose: early_repayment " "Loan ID: 2202538-01",
                "Type": "Interest",
                "Value": 0.003083333,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 25),
                "Note": "241699935: Late payment fee income Loan ID: 1529173-01",
                "Type": "Interest",
                "Value": 0.001214211,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 29),
                "Note": "243559685: Delayed interest income on rebuy Rebuy purpose: "
                "agreement_amendment Loan ID: 2198503-01",
                "Type": "Interest",
                "Value": 0.000342077,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 27),
                "Note": "260918485: Cashback bonus",
                "Type": "Interest",
                "Value": 0.3,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2016, 9, 28),
                "Note": "115013710: Withdraw application",
                "Type": "Withdrawal",
                "Value": -20.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 4, 10),
                "Note": "178363724: Loan 28375000-01 - discount/premium for secondary market transaction 178363274.",
                "Type": "Fees",
                "Value": -0.145454545,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 4, 10),
                "Note": "178363725: Loan 28375000-01 - discount/premium for secondary market transaction 178363275.",
                "Type": "Interest",
                "Value": 0.505454545,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(1970, 1, 1),
                "Note": "127373922: Loan 35287609-01 - interest received (no date for testing)",
                "Type": "Interest",
                "Value": 0.5,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement(aggregate="transaction"))

    def test_mintos_parsing_monthly_aggregation(self):
        """test parse_account_statement for mintos"""
        self.base_parser.account_statement_file = os.path.join(
            os.path.dirname(__file__), "testdata", "mintos_several_months.csv"
        )
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "mintos_en.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 28),
                "Note": "Monthly summary",
                "Type": "Deposit",
                "Value": 20.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 28),
                "Note": "Monthly summary",
                "Type": "Interest",
                "Value": 0.3,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 31),
                "Note": "Monthly summary",
                "Type": "Deposit",
                "Value": 20.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 31),
                "Note": "Monthly summary",
                "Type": "Interest",
                "Value": 0.013972955,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2016, 9, 30),
                "Note": "Monthly summary",
                "Type": "Withdrawal",
                "Value": -20.0,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement(aggregate="monthly"))

    def test_viainvest_parsing_transaction_aggregation(self):
        """test parse_account_statement for viainvest"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "viainvest.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "viainvest.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 12, 13),
                "Note": ": ",
                "Type": "Deposit",
                "Value": 1000.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 12, 14),
                "Note": "04-1246342: 04-1246342",
                "Type": "Interest",
                "Value": 0.10,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 12, 14),
                "Note": "05-3233341: 05-3233341",
                "Type": "Interest",
                "Value": 0.09,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement(aggregate="transaction"))

    @unittest.skip("Currently not checking if infile exists.")
    def test_no_statement_file(self):
        """test parse_account_statement with non existent file"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "not_existing.csv")
        self.assertFalse(self.base_parser.parse_account_statement())

    def test_robocash_parsing(self):
        """test parse_account_statement for robocash"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "robocash.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "robocash.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 15),
                "Note": "2438244: ",
                "Type": "Deposit",
                "Value": 2000.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 2, 16),
                "Note": "2458795: 856836",
                "Type": "Interest",
                "Value": 0.003835616,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement())

    def test_swaper_parsing(self):
        """test parse_account_statement for swaper"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "swaper.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "config", "swaper.yml"
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 5, 1),
                "Note": "PL-84587: 119113",
                "Type": "Interest",
                "Value": 0.1,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 4, 30),
                "Note": "PL-82794: 116800",
                "Type": "Interest",
                "Value": 0.12,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 4, 26),
                "Note": "GL-22989301: 117251",
                "Type": "Interest",
                "Value": 0.11,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2018, 1, 24),
                "Note": ": ",
                "Type": "Deposit",
                "Value": 2000.0,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement())

    def test_debitumnetwork_parsing(self):
        """test parse_account_statement for debitum network"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "debitum.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            "config",
            "debitumnetwork.yml",
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 8, 25),
                "Note": "405eea2a-7745-4588-8f08-5c1512987324: NA",
                "Type": "Deposit",
                "Value": 121.91,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 9, 7),
                "Note": "b9da7662-de61-43d1-a179-c300d5695587: " "6c4a6d93-faea-4d96-856c-7cdd3fb3023b",
                "Type": "Interest",
                "Value": 10.03,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2020, 9, 7),
                "Note": "7260c567-fdb4-44d4-84ce-4256c7d7fb80: NA",
                "Type": "Deposit",
                "Value": 10.0,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement())

    def test_lande_parsing(self):
        """test parse_account_statement for lande.finance"""
        self.base_parser.account_statement_file = os.path.join(os.path.dirname(__file__), "testdata", "lande.csv")
        self.base_parser.config_file = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            "config",
            "lande.yml",
        )
        expected_statement = [
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 8),
                "Note": "97b1a146-1c3f-47e5-8ac3-10ade56765ec: ",
                "Type": "Deposit",
                "Value": 500.0,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 8),
                "Note": "97b20fa6-c6cd-4c08-8f4a-b25f120ec583: 221108-366978",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 11),
                "Note": "97b7d986-c414-427f-90a2-c05e98641900: 221109-297724",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 11),
                "Note": "97b8289e-fd86-4312-84de-f50631fb571f: 221108-142849",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 11),
                "Note": "97b833cf-9d9f-4ff2-a800-a2b1ebaea865: 221101-847953",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 14),
                "Note": "97be0c4f-a4d1-4e7d-aeff-f07e7c446d7e: 220929-309009",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 14),
                "Note": "97be0ca1-0c64-498f-9a47-bc2c7f1ca1ed: 220926-944705",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 14),
                "Note": "97be0cfb-3ceb-4bdc-9411-b25acae80a6e: 221011-882308",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 14),
                "Note": "97be0d40-9237-4683-a6d9-be836ba90580: 221012-476486",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 14),
                "Note": "97be0d93-81a0-428b-9ea3-23be8ff7cfca: 221101-842051",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 11, 14),
                "Note": "97be48c7-c79d-4a35-a440-4048b74b17c8: 221114-968949",
                "Type": "Interest",
                "Value": 0.5,
            },
            {
                "Currency": "EUR",
                "Date": datetime.date(2022, 12, 1),
                "Note": "97e065db-dcad-4a29-8738-5adbfc74fc49: 221011-882308",
                "Type": "Interest",
                "Value": 0.5,
            },
        ]
        self.assertEqual(expected_statement, self.base_parser.parse_account_statement())

    def test_aggregation_not_supported(self):
        """test if unsopported aggregation is correctly handled"""
        self.assertFalse(self.base_parser.parse_account_statement(aggregate="yearly"))
