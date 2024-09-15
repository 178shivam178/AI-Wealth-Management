import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Database configuration using environment variables
db_config = {
    'host': os.getenv('DB_HOST'),         # Database host
    'user': os.getenv('DB_USER'),         # Database user
    'password': os.getenv('DB_PASSWORD'), # Database password
    'database': os.getenv('DB_NAME')      # Database name
}

def execute_query(query, params=None):
    connection = None
    result = None
    error_message = None
    
    try:
        # Establish a database connection using the configuration
        with mysql.connector.connect(**db_config) as connection:
            # Create a cursor object to interact with the database
            with connection.cursor() as cursor:
                # Execute the SQL query with optional parameters
                cursor.execute(query, params)
                # Fetch all results if the query returns rows
                if cursor.with_rows:
                    result = cursor.fetchall()
                # Commit the transaction
                connection.commit() 
    except Error as e:
        # Capture any database errors and store the error message
        error_message = str(e)
    finally:
        # Ensure the connection is closed if it is open
        if connection and connection.is_connected():
            connection.close()
    
    # Return the result of the query and any error message
    return result, error_message
