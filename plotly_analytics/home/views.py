import logging
from django.shortcuts import render
from django.http import JsonResponse
import requests
import sys
import os
import ast
import re
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Database configuration using environment variables
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

# Add paths to the system path for importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../sql_search')))
from main import execute_user_query

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../mf_pf_suggetions')))
from mutual_funds.mf_main import get_average_balances
from mutual_funds.mf_calculator_sugg import generate_investment_report
from personlized_plan.steps import process_financial_analysis

# Set up logging for the module
logger = logging.getLogger(__name__)

def calculate_average_balance(personal_data):
    """
    Calculate the average balance from the provided personal data.
    
    :param personal_data: List of dictionaries containing 'AverageBalance' information.
    :return: The average balance, rounded to the nearest integer. Returns 0 if no balances are provided.
    """
    balances = [record['AverageBalance'] for record in personal_data]

    if balances:
        average_balance = sum(balances) / len(balances)
        return int(round(average_balance)) 
    else:
        return 0 

def home(request):
    """
    Render the home page with average balance and mutual fund suggestions.
    
    :param request: The HTTP request object.
    :return: Rendered HTML template with context data.
    """
    # Fetch average balances and process personal data
    personal_data = get_average_balances()
    personal_data = ast.literal_eval(personal_data)

    person_name = personal_data[0]['PersonName']
    account_no = personal_data[0]['AccountNo']

    # Calculate average balance
    average_balance = calculate_average_balance(personal_data)
    # Generate mutual fund suggestions based on the average balance
    mf_suggestions = generate_investment_report(average_balance)
    
    # Prepare context for rendering the template
    context = {
        'person_name': person_name,
        'account_no': account_no,
        'data': personal_data,
        'average_balance': average_balance,
        'mutual_funds': ast.literal_eval(mf_suggestions)
    }
    
    return render(request, 'home/base.html', context)

def is_financial_goal_query(query):
    """
    Determine if the query is related to a financial goal such as buying a car, home, or bike.
    
    :param query: The user query string.
    :return: True if the query relates to a financial goal, otherwise False.
    """
    query_lower = query.lower()
    financial_goal_keywords = [
        "buy a car", "buy a home", "buy a bike",
        "purchase a car", "purchase a home", "purchase a bike",
        "plan to buy a car", "plan to buy a home", "plan to buy a bike",
        "intend to buy a car", "intend to buy a home", "intend to buy a bike",
        "saving for a car", "saving for a home", "saving for a bike",
        "goal to buy a car", "goal to buy a home", "goal to buy a bike",
        "want to buy a car", "want to buy a home", "want to buy a bike"
    ]

    # Compile a regex pattern to match financial goal phrases
    pattern = re.compile(r'\b(?:buy|purchase|plan to buy|intend to buy|saving for|goal to buy|want to buy)\s+a\s+(car|home|bike)\b', re.IGNORECASE)
    return any(keyword in query_lower for keyword in financial_goal_keywords) or bool(pattern.search(query_lower))

def search_view(request):
    """
    Handle POST requests for searching based on user query. Process financial goals or execute user queries.
    
    :param request: The HTTP request object.
    :return: JSON response with search results or error messages.
    """
    # Fetch average balances and process personal data
    personal_data = get_average_balances()
    personal_data = ast.literal_eval(personal_data)

    # Calculate average balance
    average_balance = calculate_average_balance(personal_data)
    
    if request.method == 'POST':
        search_query = request.POST.get('query')
        
        # Check if the query parameter is provided
        if not search_query:
            return JsonResponse({'error': 'Query parameter is required'}, status=400)
        
        try:
            saving_amount = average_balance
            if is_financial_goal_query(search_query):
                # Process financial goals
                results = process_financial_analysis(search_query, saving_amount)
      
                if isinstance(results, dict):
                    return JsonResponse({"results": results})
                else:
                    return JsonResponse({'error': 'Unexpected results format from financial analysis'}, status=500)
                
            else:
                # Execute user query and format results
                results = execute_user_query(search_query)
                formatted_results = [list(result) for result in results]
                return JsonResponse({'results': formatted_results})
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'API request error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
