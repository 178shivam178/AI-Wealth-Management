import openai
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Set the OpenAI API key from the environment variables
openai.api_key = os.getenv('OPENAI_KEY')

# Custom exception for errors in SQL query generation
class SQLQueryGenerationError(Exception):
    pass

def generate_sql_query(user_question, system_prompt):
    try:
        # Prepare the messages for the OpenAI API request
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
        
        # Make a request to OpenAI's ChatCompletion API to generate SQL query
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Model to use for query generation
            messages=messages,      # Messages containing the system prompt and user question
            max_tokens=150,         # Maximum number of tokens in the response
            temperature=0.7,        # Sampling temperature for creativity
            top_p=0.9               # Nucleus sampling parameter
        )

        # Extract and return the generated SQL query from the API response
        sql_query = response.choices[0].message['content'].strip()
        return sql_query

    except openai.error.OpenAIError as e:
        # Handle errors specific to the OpenAI API
        raise SQLQueryGenerationError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        # Handle unexpected errors
        raise SQLQueryGenerationError(f"An unexpected error occurred: {str(e)}")
