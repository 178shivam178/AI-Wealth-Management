import mysql.connector
from decimal import Decimal
import json
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Configuration for connecting to the MySQL database
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

def get_top_performing_funds(db_config, return_period, top_n=3):
    """
    Fetch the top-performing mutual funds based on the return period.

    Args:
        db_config (dict): Database configuration parameters.
        return_period (str): The return period (e.g., '1year', '3year').
        top_n (int): Number of top funds to retrieve (default is 3).

    Returns:
        list: A list of tuples with fund names and their return percentages.

    Raises:
        mysql.connector.Error: If there is a database connection or query error.
        ValueError: If no data is found for the specified return period.
    """
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Define the SQL query to retrieve top-performing funds based on the return period
        query = f"""
        SELECT fund_name, ret_{return_period} AS return_percentage
        FROM scheme_performance_table
        ORDER BY return_percentage DESC
        LIMIT %s
        """
        # Execute the query with the limit parameter
        cursor.execute(query, (top_n,))
        results = cursor.fetchall()
        
        # Close the cursor and connection
        cursor.close()
        connection.close()
        
        if results:
            # Return results with fund names and return percentages as Decimal objects
            return [(result['fund_name'], Decimal(result['return_percentage'])) for result in results]
        else:
            raise ValueError(f"No data found for {return_period}.")
    except mysql.connector.Error as err:
        # Print and raise database connection errors
        print(f"Database error: {err}")
        raise
    except ValueError as e:
        # Print and raise value errors if no data is found
        print(f"Value error: {e}")
        raise

def calculate_future_value(monthly_savings, annual_return_rate, periods_in_years):
    """
    Calculate the future value of a monthly savings plan with a given annual return rate over a certain period.

    Args:
        monthly_savings (float): The amount saved each month.
        annual_return_rate (float): The annual return rate as a percentage.
        periods_in_years (float): The number of years over which savings will be invested.

    Returns:
        Decimal: The future value of the investment.
    """
    monthly_savings = Decimal(monthly_savings)
    annual_return_rate = Decimal(annual_return_rate)
    
    # Calculate the monthly interest rate from the annual return rate
    monthly_rate = (1 + annual_return_rate / 100) ** (Decimal('1') / Decimal('12')) - Decimal('1')
    num_months = Decimal(periods_in_years) * Decimal('12')
    
    # Calculate the future value using the formula for compound interest
    future_value = monthly_savings * (((1 + monthly_rate) ** num_months - Decimal('1')) / monthly_rate)
    
    return future_value

def generate_investment_report(saving_amount, period):
    """
    Generate an investment report comparing different mutual funds for a specified period.

    Args:
        saving_amount (float): The amount saved each month.
        period (str): The investment period (e.g., '1year', '5year').

    Returns:
        str: JSON string containing the investment report.
    """
    top_n = 1  # Number of top funds to consider
    results = {}

    # Map periods to their respective years as decimals
    period_to_years = {
        '7_days': Decimal('7') / Decimal('365'),
        '14_days': Decimal('14') / Decimal('365'),
        '21_days': Decimal('21') / Decimal('365'),
        '28_days': Decimal('28') / Decimal('365'),
        '90_days': Decimal('90') / Decimal('365'),
        '365_days': Decimal('1'),
        '730_days': Decimal('2'),
        '1095_days': Decimal('3'),
        '1825_days': Decimal('5'),
        '3650_days': Decimal('10'),
        '1week': Decimal('7') / Decimal('365'),
        '1month': Decimal('1') / Decimal('12'),
        '3month': Decimal('3') / Decimal('12'),
        '6month': Decimal('0.5'),
        '9month': Decimal('9') / Decimal('12'),
        '1year': Decimal('1'),
        '2year': Decimal('2'),
        '3year': Decimal('3'),
        '4year': Decimal('4'),
        '5year': Decimal('5'),
        '7year': Decimal('7'),
        '10year': Decimal('10'),
        '15year': Decimal('15'),
        '20year': Decimal('20')
    }
    
    try:
        # Retrieve the number of years for the specified period
        periods_in_years = period_to_years[period]

        # Get top-performing funds for the given period
        top_funds = get_top_performing_funds(db_config, period, top_n)
        results[period] = []

        for fund_name, return_percentage in top_funds:
            annual_return = return_percentage  
            
            # Calculate total invested amount and future value
            total_invested_amount = Decimal(saving_amount) * Decimal('12') * periods_in_years
            future_value = calculate_future_value(saving_amount, annual_return, periods_in_years)
            
            results[period].append({
                'fund_name': fund_name,
                'return_percentage': float(return_percentage),  # Convert Decimal to float for JSON serialization
                'total_invested_amount': float(total_invested_amount),
                'future_value': float(future_value)
            })
    except KeyError:
        # Handle invalid period input
        print(f"Invalid period specified: {period}")
    except Exception as e:
        # Handle other exceptions
        print(f"Failed to retrieve data for {period}: {e}")
    
    # Convert the results dictionary to a JSON string
    json_output = json.dumps(results, indent=4, default=str)
    return json_output
