import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import ast
import pandas as pd
from src.classification import classify_description
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration for connecting to the MySQL database
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Custom exception for handling database errors
class DatabaseError(Exception):
    pass

def convert_date_format(date_str, current_format='%d/%m/%Y', target_format='%Y-%m-%d'):
    """
    Convert date from one format to another.
    
    :param date_str: Date string to convert.
    :param current_format: Current date format.
    :param target_format: Target date format.
    :return: Date string in target format or None if conversion fails.
    """
    if isinstance(date_str, str) and date_str.strip():
        try:
            return datetime.strptime(date_str, current_format).strftime(target_format)
        except ValueError:
            raise ValueError(f"Date conversion error for date_str: {date_str}")
    return None

def convert_decimal_value(value_str):
    """
    Convert a string representation of a decimal value to a float.
    
    :param value_str: String to convert.
    :return: Float value or 0.0 if conversion fails.
    """
    if isinstance(value_str, str) and value_str.strip():
        try:
            value = value_str.replace(',', '')  # Remove commas for conversion
            return float(value) if value else 0.0
        except ValueError:
            raise ValueError(f"Decimal conversion error for value_str: {value_str}")
    return 0.0

def is_valid_value(value):
    """
    Check if a value is valid (not NaN, None, empty string, or 'nan').
    
    :param value: Value to check.
    :return: True if value is valid, False otherwise.
    """
    return not (pd.isna(value) or value in [None, '', 'nan'])

def filter_valid_transactions(transaction_data):
    """
    Filter out invalid transactions based on required fields.
    
    :param transaction_data: List of transaction dictionaries.
    :return: List of valid transactions.
    """
    filtered_data = []
    for transaction in transaction_data:
        # Check if all required fields are valid
        if all(is_valid_value(transaction.get(key)) for key in ['Transaction\nDate', 'ValueDate', 'Debit', 'Credit', 'Balance']):
            filtered_data.append(transaction)
    return filtered_data

def insert_data_to_db(personal_info, transaction_data):
    """
    Insert personal information and transaction data into the database.
    
    :param personal_info: Personal information as a string to be converted to a dictionary.
    :param transaction_data: List of transaction dictionaries.
    """
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            **db_config
        )
        with conn.cursor() as cursor:
            # Convert personal_info string to a dictionary
            personal_info = ast.literal_eval(personal_info)

            # Insert or update personal information
            personal_insert_query = """
                INSERT INTO Personal_Info 
                (BankName, PersonName, BranchName, PersonAddress, BankAddress, AccountNo, IFSC, CustomerID) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                BankName = VALUES(BankName), PersonName = VALUES(PersonName), BranchName = VALUES(BranchName),
                PersonAddress = VALUES(PersonAddress), BankAddress = VALUES(BankAddress),
                IFSC = VALUES(IFSC)
            """
            personal_data = (
                personal_info.get('BankName', ''),
                personal_info.get('PersonName', ''),
                personal_info.get('BranchName', ''),
                personal_info.get('PersonAddress', ''),
                personal_info.get('BranchAddress', ''), 
                personal_info.get('AccountNo', ''),
                personal_info.get('IFSC', ''),
                personal_info.get('CustomerID', '')
            )
            cursor.execute(personal_insert_query, personal_data)

            # Retrieve the ID of the inserted or updated personal record
            personal_id_query = "SELECT ID FROM Personal_Info WHERE CustomerID = %s"
            cursor.execute(personal_id_query, (personal_info.get('CustomerID', ''),))
            result = cursor.fetchone()
            if result:
                personal_id = result[0]
            else:
                raise DatabaseError("Error: Personal record was not found after insertion.")

            # Filter valid transactions
            transaction_data = filter_valid_transactions(transaction_data)

            # Insert transaction data
            transaction_insert_query = """
                INSERT INTO Transaction_Info 
                (ID, BankName, PersonName, AccountNo, TransactionDate, ValueDate, Description, Debit, Credit, Balance,label) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            """
            for transaction in transaction_data:
                # Convert date and value fields
                transaction_date = convert_date_format(transaction.get('Transaction\nDate', ''))
                value_date = convert_date_format(transaction.get('ValueDate', ''))
                debit = convert_decimal_value(transaction.get('Debit', '0'))
                credit = convert_decimal_value(transaction.get('Credit', '0'))
                balance = convert_decimal_value(transaction.get('Balance', '0'))

                # Classify the transaction description
                label = classify_description(transaction.get('Description', ''))
                
                # Prepare transaction data for insertion
                transaction_data_tuple = (
                    personal_id,
                    personal_info.get('BankName', ''),
                    personal_info.get('PersonName', ''),
                    personal_info.get('AccountNo', ''),
                    transaction_date,
                    value_date,
                    transaction.get('Description', ''),
                    debit,
                    credit,
                    balance,
                    label
                )
                cursor.execute(transaction_insert_query, transaction_data_tuple)

            # Commit all changes to the database
            conn.commit()

    except mysql.connector.Error as err:
        # Handle MySQL errors
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise DatabaseError(f"Duplicate entry error: {err}")
        else:
            raise DatabaseError(f"Database error: {err}")
    except Exception as e:
        # Handle unexpected errors
        raise DatabaseError(f"Unexpected error: {str(e)}")
    finally:
        # Ensure database connection is closed
        if conn.is_connected():
            conn.close()
