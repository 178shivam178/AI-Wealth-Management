import time
from db.execute import execute_query
from prompts.fix_sql_query_prompt import fix_sql_query_error_prompt
import db_schema
from steps.generate_query import generate_sql_query

# Custom exception for handling errors in query execution
class QueryExecutionError(Exception):
    """Custom exception for errors in query execution."""
    pass

# Custom exception for handling errors in generating query suggestions
class QuerySuggestionError(Exception):
    """Custom exception for errors in generating query suggestions."""
    pass

def process_single_query(question, generated_query):
    max_attempts = 3  # Maximum number of retry attempts for query execution
    attempt = 0  # Initialize attempt counter

    while attempt < max_attempts:
        try:
            # Execute the SQL query and get the result and error message
            result, error_message = execute_query(generated_query)
            
            if error_message:
                # If there is an error, prepare a system prompt for fixing the query
                system_prompt = fix_sql_query_error_prompt(
                    question, 
                    result, 
                    error_message, 
                    db_schema.database_schema
                )
    
                print(f"Attempt {attempt + 1} failed: {error_message}")

                try:
                    # Generate a new SQL query based on the system prompt
                    suggested_query = generate_sql_query(question, system_prompt)
                    if suggested_query:
                        print(f"Received a suggested query from the error resolution API: {suggested_query}")
                        generated_query = suggested_query  # Update the query with the suggestion
                    else:
                        raise QuerySuggestionError("No suggestions received from the error resolution API.")
                except Exception as e:
                    # Handle errors in generating query suggestions
                    raise QuerySuggestionError(f"Error generating query suggestion: {str(e)}")
                
                attempt += 1  # Increment attempt counter
                time.sleep(1)  # Wait before retrying
            
            else:
                # If no error, return the successful result
                print(f"Query executed successfully: {result}")
                return result  

        except Exception as e:
            # Handle general exceptions during query execution
            raise QueryExecutionError(f"An error occurred during query execution: {str(e)}")

    # If all attempts fail, return a failure message
    print("All attempts failed. No answer could be obtained for this question.")
    return "No answer could be obtained for this question." 
