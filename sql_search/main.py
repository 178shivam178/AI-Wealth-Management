from prompts.sql_prompt import format_prompt_sql_query
import db_schema as db_schema
from steps.generate_query import generate_sql_query
from steps.execute_query import process_single_query

def execute_user_query(user_query):
    # Retrieve the database schema
    database_schema = db_schema.database_schema
    
    # Format the system prompt based on the database schema
    system_prompt = format_prompt_sql_query(database_schema)
    
    try:
        # Generate an SQL query using the user question and the system prompt
        generated_query = generate_sql_query(user_query, system_prompt)
        
        # Check if a valid query was generated
        if not generated_query:
            return "No generated query received from the LLM model."
        
        # Execute the generated query and retrieve the result
        result = process_single_query(user_query, generated_query)
        
        return result
        
    except ConnectionError:
        # Handle errors related to database connection issues
        return "Database connection error. Please check your connection settings."
    except SyntaxError:
        # Handle errors related to syntax issues in the SQL query
        return "Error in the generated SQL query syntax."
    except Exception as e:
        # Handle any other unexpected errors
        return f"An unexpected error occurred: {str(e)}"
