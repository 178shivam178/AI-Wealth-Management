database_schema = """{
    Database Name = AI_Wealth
    TABLE_NAME = transaction_info
    "transaction_info": "This table contains information about financial transactions from various bank accounts. Each record represents a unique transaction and includes details about the transaction date, value date, description, debit and credit amounts, balance, and label.",
    "COLUMNS": {
        "ID": {
            "description": "Unique identifier for each transaction",
            "values_sample": ["6"]
        },
        "BankName": {
            "description": "Name of the bank where the transaction occurred",
            "values_sample": ["YES Bank"]
        },
        "PersonName": {
            "description": "Name of the person associated with the transaction",
            "values_sample": ["MRS.K GEETHANJALI"]
        },
        "AccountNo": {
            "description": "Bank account number associated with the transaction",
            "values_sample": ["063991900002710"]
        },
        "TransactionDate": {
            "description": "Date when the transaction occurred",
            "values_sample": ["2017-12-02"]
        },
        "ValueDate": {
            "description": "Date when the value of the transaction is considered for accounting purposes",
            "values_sample": ["2017-12-02"]
        },
        "Description": {
            "description": "Description or details of the transaction",
            "values_sample": [
                "PCA:5000944243:PAYTMWAL1210203:PTM(PAYTM\nPAYTMWAL1210203-120240141263",
                "PCA:5000944243:037044001941265:FAMILIES\nSUPERMARKET 037044001941265-733608213111"
            ]
        },
        "Debit": {
            "description": "Amount debited from the account",
            "values_sample": ["899.00", "469.00"]
        },
        "Credit": {
            "description": "Amount credited to the account",
            "values_sample": ["0.00"]
        },
        "Balance": {
            "description": "Balance in the account after the transaction",
            "values_sample": ["50000.46", "49531.46"]
        },
        "label": {
            "description": "Category or label associated with the transaction",
            "values_sample": ["Others", "Super Market"]
        }
    }
}
"""