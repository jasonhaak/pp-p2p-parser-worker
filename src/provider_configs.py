# -*- coding: utf-8 -*-
"""
Bundled provider configuration for the P2P statement parser.
"""


PROVIDER_CONFIGS = {
    "bondora": {
        "type_regex": {
            "deposit": "(^TransferDeposit.*)|(^TransferGoGrowMainRepaiment.*)",
            "withdraw": "(^Withdraw.*)|(^TransferGoGrow$)",
            "interest": "(^TransferInterestRepaiment.*)|(^TransferExtraInterestRepaiment.*)",
            "fee": "(^FX commission.*)",
        },
        "csv_fieldnames": {
            "booking_date": "TransferDate",
            "booking_date_format": "%d.%m.%Y %H:%M",
            "booking_details": "Description",
            "booking_id": "LoanNumber",
            "booking_type": "Description",
            "booking_value": "Amount",
            "booking_currency": "Currency",
        },
    },
    "bondora_go_grow": {
        "type_regex": {
            "deposit": "(^TransferGoGrow$)",
            "withdraw": "(^TransferGoGrowMainRepaiment$)",
            "interest": "(^$)",
            "fee": "(^$)",
        },
        "csv_fieldnames": {
            "booking_date": "TransferDate",
            "booking_date_format": "%d.%m.%Y %H:%M",
            "booking_details": "Description",
            "booking_id": "LoanNumber",
            "booking_type": "Description",
            "booking_value": "Amount",
            "booking_currency": "Currency",
        },
    },
    "debitumnetwork": {
        "type_regex": {
            "deposit": "^DEPOSIT|^INVITED_REFERRAL_REWARD",
            "withdraw": "^WITHDRAW",
            "interest": "^REPAYMENT",
        },
        "csv_fieldnames": {
            "booking_date": "Date",
            "booking_date_format": "%Y-%m-%d",
            "booking_id": "Transaction ID",
            "booking_type": "Transaction Type",
            "booking_value": "Turnover",
            "booking_details": "Asset ID",
        },
    },
    "estateguru": {
        "type_regex": {
            "deposit": "^Einzahlung.*",
            "withdraw": "^Auszahlung.*",
            "interest": "(^Empfehlungsbonus.*)|(^Zins.*)|(^Sondervergütung.*)|(^Empfehlung.*)|(^Bonus.*)",
        },
        "csv_fieldnames": {
            "booking_date": "Zahlungsdatum",
            "booking_date_format": "%d/%m/%Y %H:%M",
            "booking_details": "Projektname",
            "booking_id": "UniqueId",
            "booking_type": "Cashflow-Typ",
            "booking_value": "Betrag",
            "booking_currency": "Währung",
        },
    },
    "estateguru_de": {
        "type_regex": {
            "deposit": "^Einzahlung.*",
            "withdraw": "^Auszahlung.*",
            "interest": "^Zins.*",
            "fee": "^Vermögensverwaltungsgebühr.*",
            "ignorable_entry": "(^Investition.*)|(^Hauptbetrag$)",
        },
        "csv_fieldnames": {
            "booking_date": "Zahlungsdatum",
            "booking_date_format": "%d.%m.%Y %H:%M",
            "booking_details": "Projektname",
            "booking_id": "ID",
            "booking_type": "Cashflow-Typ",
            "booking_value": "Betrag",
            "booking_currency": "Währung",
        },
    },
    "estateguru_en": {
        "type_regex": {
            "deposit": "^Deposit.*",
            "withdraw": "^Withdrawal.*",
            "interest": "(^Interest.*)|(^Indemnity.*)|(^Referral.*)|(^EG Bonus.*)|(^Secondary Market Profit.*)",
            "fee": "(^Secondary Market Loss.*)|(^Fee.*)",
        },
        "csv_fieldnames": {
            "booking_date": "Payment Date",
            "booking_date_format": "%d/%m/%Y %H:%M",
            "booking_details": "Loan Code",
            "booking_id": "ID",
            "booking_type": "Cash Flow Type",
            "booking_value": "Amount",
            "booking_currency": "Currency",
        },
    },
    "lande": {
        "type_regex": {
            "deposit": "^Bank transfer deposit$",
            "withdraw": "^Withdraw.*",
            "interest": "(.*Interest$)|(^Affiliate-Bonus$)|(^Empfehlungsbonus$)",
        },
        "csv_fieldnames": {
            "booking_date": "Date",
            "booking_date_format": "%d.%m.%Y",
            "booking_details": "Loan ID",
            "booking_id": "Transaction ID",
            "booking_type": "Type",
            "booking_value": "Amount",
        },
    },
    "mintos": {
        "type_regex": {
            "deposit": "(Deposits)|(^Incoming client.*)|(^Incoming currency exchange.*)|(^Affiliate partner bonus$)",
            "withdraw": "(^Withdraw application.*)|(Outgoing currency.*)|(Withdrawal)",
            "interest": (
                "(^Delayed interest.*)|(^Late payment.*)|(^Interest income.*)|(^Cashback.*)|"
                "(^.*[Ii]nterest received.*)|(^.*late fees received$)"
            ),
            "fee": "(^FX commission.*)|(.*secondary market fee$)",
            "ignorable_entry": ".*investment in loan.*|.*[Pp]rincipal received.*|.*secondary market transaction.*",
            "special_entry": "(.*discount/premium.*)",
        },
        "csv_fieldnames": {
            "booking_date": "Date",
            "booking_date_format": "%Y-%m-%d %H:%M:%S",
            "booking_details": "Details",
            "booking_id": "Transaction ID:",
            "booking_type": "Details",
            "booking_value": "Turnover",
            "booking_currency": "Currency",
        },
    },
    "mintos_de": {
        "type_regex": {
            "deposit": "(^Einzahlung.*)|(^Eingehende.*)",
            "withdraw": "(^Auszahlung.*)|(^Abhebung.*)",
            "interest": (
                "(.*Erhaltene Zinsen$)|(.*Zinseinnahmen.*)|(.*Zinserträge.*)|"
                "(.*Verzugszinseinnahmen.*)|(.*Zinseinnahmen aus ausstehenden Zahlungen.*)"
            ),
            "fee": "(.*Steuereinbehalt$)|(.*Einbehaltene Steuern.*)|(.*fee$)",
            "ignorable_entry": "(.*Erhaltene Tilgung.*)|(^Investition$)|(.* Investition$)",
        },
        "csv_fieldnames": {
            "booking_date": "Datum",
            "booking_date_format": "%Y-%m-%d %H:%M:%S",
            "booking_details": "Details",
            "booking_id": "Transaktions-Nr.:",
            "booking_type": "Details",
            "booking_value": "Umsatz",
            "booking_currency": "Währung",
        },
    },
    "robocash": {
        "type_regex": {
            "deposit": "^Adding funds.*",
            "withdraw": "^Withdraw application.*",
            "interest": "(^Paying interest.*)",
        },
        "csv_fieldnames": {
            "booking_date": "Date and time",
            "booking_date_format": "%Y-%m-%d %H:%M:%S",
            "booking_details": "Credit part ID",
            "booking_id": "Transaction ID",
            "booking_type": "Operation",
            "booking_value": "Amount",
        },
    },
    "swaper": {
        "type_regex": {
            "deposit": "^FUNDING.*",
            "withdraw": "^Withdraw application.*",
            "interest": "(^EXTENSION_INTEREST.*)|(^REPAYMENT_INTEREST.*)|(^BUYBACK_INTEREST.*)",
        },
        "csv_fieldnames": {
            "booking_date": "Booking date",
            "booking_date_format": "%d.%m.%Y",
            "booking_details": "Loan id",
            "booking_id": "Loan number",
            "booking_type": "Transaction type",
            "booking_value": "Amount",
        },
    },
    "viainvest": {
        "type_regex": {
            "deposit": "(Amount of funds deposited)",
            "withdraw": "",
            "interest": "(Amount of interest payment received)",
            "ignorable_entry": "(Amount invested in loan)|(Amount of principal repayment received)",
        },
        "csv_fieldnames": {
            "booking_date": "Value date",
            "booking_date_format": "%m/%d/%Y",
            "booking_details": "Loan ID",
            "booking_id": "Loan ID",
            "booking_type": "Transaction type",
            "booking_value": "Credit (€)",
        },
    },
}
