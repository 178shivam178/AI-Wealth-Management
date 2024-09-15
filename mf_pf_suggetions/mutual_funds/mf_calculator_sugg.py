import mysql.connector
from decimal import Decimal
import json
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Database configuration loaded from environment variables
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

def get_top_performing_funds(db_config, return_period, top_n=3):
    """
    Fetch the top-performing mutual funds based on the specified return period.
    
    Args:
        db_config (dict): Database configuration dictionary.
        return_period (str): The return period to filter (e.g., '1year').
        top_n (int): Number of top-performing funds to retrieve (default is 3).
    
    Returns:
        list: List of tuples containing fund names and return percentages.
    
    Raises:
        ValueError: If no data is found for the specified return period.
    """
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Define the query to get the top-performing funds
        query = f"""
        SELECT fund_name, ret_{return_period} AS return_percentage
        FROM scheme_performance_table
        ORDER BY return_percentage DESC
        LIMIT %s
        """
        cursor.execute(query, (top_n,))
        results = cursor.fetchall()
        
        # Close the cursor and connection
        cursor.close()
        connection.close()
        
        if results:
            # Convert results to a list of tuples with Decimal return percentages
            return [(result['fund_name'], Decimal(result['return_percentage'])) for result in results]
        else:
            raise ValueError(f"No data found for {return_period}.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        raise
    except ValueError as e:
        print(f"Value error: {e}")
        raise

def calculate_future_value(monthly_savings, annual_return_rate, periods_in_years):
    """
    Calculate the future value of monthly savings based on the annual return rate.
    
    Args:
        monthly_savings (float): Amount of money saved monthly.
        annual_return_rate (float): Annual return rate as a percentage.
        periods_in_years (float): Number of years for the investment.
    
    Returns:
        Decimal: Future value of the investment.
    """
    monthly_savings = Decimal(monthly_savings)
    annual_return_rate = Decimal(annual_return_rate)
    
    # Convert annual return rate to monthly rate
    monthly_rate = (1 + annual_return_rate / 100) ** (Decimal('1') / Decimal('12')) - Decimal('1')
    num_months = Decimal(periods_in_years) * Decimal('12')
    
    # Calculate the future value using the formula
    future_value = monthly_savings * (((1 + monthly_rate) ** num_months - Decimal('1')) / monthly_rate)
    
    return future_value

def generate_investment_report(saving_amount):
    """
    Generate an investment report showing the future value of savings in top-performing funds for various periods.
    
    Args:
        saving_amount (float): Amount of money saved monthly.
    
    Returns:
        str: JSON string containing the investment report.
    """
    periods = ['6month', '1year', '2year', '3year', '4year', '5year', '10year']
    top_n = 3
    results = {}

    for period in periods:
        try:
            # Get the top-performing funds for the current period
            top_funds = get_top_performing_funds(db_config, period, top_n)
            results[period] = []
            
            for fund_name, return_percentage in top_funds:
                annual_return = return_percentage  # Using the return percentage directly as annual return
                periods_in_years = {
                    '6month': Decimal('0.5'),
                    '1year': Decimal('1'),
                    '2year': Decimal('2'),
                    '3year': Decimal('3'),
                    '4year': Decimal('4'),
                    '5year': Decimal('5'),
                    '10year': Decimal('10')
                }[period]
                total_invested_amount = Decimal(saving_amount) * Decimal('12') * periods_in_years
                future_value = calculate_future_value(saving_amount, annual_return, periods_in_years)
                results[period].append({
                    'fund_name': fund_name,
                    'return_percentage': float(return_percentage),  # Convert Decimal to float for JSON serialization
                    'total_invested_amount': float(total_invested_amount),
                    'future_value': float(future_value)
                })
        except Exception as e:
            print(f"Failed to retrieve data for {period}: {e}")
    
    # Convert the results dictionary to a JSON string
    json_output = json.dumps(results, indent=4, default=str)
    return json_output
