import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import json
from decimal import Decimal

# Load environment variables from a .env file
load_dotenv()

# Database configuration loaded from environment variables
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

def decimal_to_float(o):
    """
    Convert Decimal to float for JSON serialization.
    
    Args:
        o (object): The object to convert.
    
    Returns:
        float: The converted float value if o is a Decimal.
    
    Raises:
        TypeError: If o is not a Decimal.
    """
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError(f'Object of type {o.__class__.__name__} '
                    f'is not JSON serializable')

def get_average_balances():
    """
    Fetch and calculate the average balances for each account per month.
    
    Returns:
        str: JSON string containing the average balances for each account.
    
    Raises:
        Error: If there is a database connection error.
    """
    results = []
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Define the SQL query to calculate monthly average balances
            query = """
            WITH AdjustedBalances AS (
                SELECT
                    BankName,
                    PersonName,
                    AccountNo,
                    DATE_FORMAT(TransactionDate, '%Y-%m-01') AS MonthStart,
                    Balance
                FROM transaction_info
                WHERE DATE(TransactionDate) BETWEEN
                    DATE_SUB(DATE_FORMAT(TransactionDate, '%Y-%m-01'), INTERVAL 1 DAY) AND
                    DATE_ADD(DATE_FORMAT(TransactionDate, '%Y-%m-01'), INTERVAL 1 DAY)
            ),
            MonthlyAverages AS (
                SELECT
                    BankName,
                    PersonName,
                    AccountNo,
                    YEAR(MonthStart) AS Year,
                    MONTH(MonthStart) AS Month,
                    AVG(Balance) AS AverageBalance
                FROM AdjustedBalances
                GROUP BY BankName, PersonName, AccountNo, Year, Month
            )
            SELECT
                BankName,
                PersonName,
                AccountNo,
                Year,
                Month,
                ROUND(AverageBalance, 2) AS AverageBalance
            FROM MonthlyAverages
            ORDER BY BankName, PersonName, AccountNo, Year, Month;
            """
            # Execute the SQL query
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Convert query results to a list of dictionaries
            result_list = []
            for row in results:
                result_list.append({
                    "BankName": row[0],
                    "PersonName": row[1],
                    "AccountNo": row[2],
                    "Year": row[3],
                    "Month": row[4],
                    "AverageBalance": decimal_to_float(row[5])
                })

            # Convert the result list to a JSON string
            json_result = json.dumps(result_list, indent=4)
            return json_result

    except Error as e:
        # Handle database connection errors
        print(f"Error: {e}")
        return json.dumps({"error": str(e)})

    finally:
        # Ensure resources are released and connection is closed
        if connection.is_connected():
            cursor.close()
            connection.close()
