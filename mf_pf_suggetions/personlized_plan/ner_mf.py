import os
import openai
from dotenv import load_dotenv
import ast

# Load environment variables from a .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
api_key = os.getenv('OPENAI_KEY')

# Raise an error if the API key is not set
if api_key is None:
    raise ValueError("OpenAI API key is not set in the environment variables.")

# Set the API key for OpenAI
openai.api_key = api_key

def extract_entities(sentence):
    """
    Extract entities related to 'assets', 'time_period', and 'total_amount' from the given sentence using OpenAI API.

    Args:
        sentence (str): The sentence from which entities need to be extracted.

    Returns:
        dict or str: A dictionary containing extracted entities if successful, otherwise an error message.
    """
    try:
        # Define the prompt to instruct the model on what entities to extract
        prompt = (
            "Extract entities related to 'assets', 'time_period', and 'total_amount' from the following sentence.\n"
            "Only consider the following entities:\n"
            "Assets: [car, home, marriage, bike, flat, plots]\n"
            "Time_period: [1month, 3month, 6month, 9month, 1year, 2year, 3year, 4year, 5year, 7year, 10year, 15year, 20year]\n"
            "Total_amount: [amount in numeric format]\n"
            "Example: 'I want to buy a car costing 50000 and a house costing 200000 in 2 years.'\n"
            "Output: {'assets': ['car', 'house'], 'time_period': ['2year'], 'total_amount': [50000, 200000]}\n\n"
            f"Now extract from this sentence:\n\n\"{sentence}\"\n\n"
            "Return the result in this format: {'assets': [list of assets], 'time_period': [time period], 'total_amount': [list of amounts]}."
        )
        
        # Call the OpenAI API to generate the response based on the prompt
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that extracts specified entities from sentences."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  # Limit the response to 150 tokens
            n=1,  # Retrieve one response
            stop=None,
            temperature=0.2  # Set temperature for controlled randomness in the response
        )

        # Extract and clean up the response content
        extracted_entities = response['choices'][0]['message']['content'].strip()

        try:
            # Parse the response content into a dictionary
            result = ast.literal_eval(extracted_entities)
            # Validate that the result is a dictionary with the expected keys
            if isinstance(result, dict) and all(k in result for k in ['assets', 'time_period', 'total_amount']):
                return result
            else:
                return f"Unexpected format of the response: {extracted_entities}"
        except (ValueError, SyntaxError) as e:
            # Handle errors in parsing the response
            return f"Error parsing the response. Ensure the format is correct: {extracted_entities}"

    except openai.error.AuthenticationError:
        # Handle authentication errors related to OpenAI API key
        return "Authentication failed. Please check your OpenAI API key."
    except openai.error.OpenAIError as e:
        # Handle other errors from the OpenAI API
        return f"An error occurred while communicating with OpenAI API: {e}"
    except Exception as e:
        # Handle unexpected errors
        return f"An unexpected error occurred: {e}"
