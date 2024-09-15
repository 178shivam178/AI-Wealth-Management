import openai
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_KEY')

def extract_entities(text):
    # Define the prompt for extracting key information from bank statements
    prompt = (
        "You are an advanced AI trained to extract key information from bank statements. "
        "Extract the following information into JSON format. Make sure there is no extra text, only the JSON object with key-value pairs. The keys are as follows: "
        "1. BankName\n"
        "2. PersonName\n"
        "3. PersonAddress\n"
        "4. CustomerID\n"
        "5. BranchName\n"
        "6. BranchAddress\n"
        "7. IFSC\n"
        "8. AccountNo\n\n"
        f"Here is the text from which to extract the information:\n{text}\n\n"
        "Provide the extracted information in this format:\n"
        "{\n"
        '  "BankName": "<value>",\n'
        '  "PersonName": "<value>",\n'
        '  "PersonAddress": "<value>",\n'
        '  "CustomerID": "<value>",\n'
        '  "BranchName": "<value>",\n'
        '  "BranchAddress": "<value>",\n'
        '  "IFSC": "<value>",\n'
        '  "AccountNo": "<value>"\n'
        "}\n"
        "ExtractedInfo:"
    )
    
    try:
        # Send a request to OpenAI's API to extract information based on the provided prompt
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model to use for extraction
            messages=[
                {"role": "system", "content": "You are an advanced AI trained to extract key information from bank statements."},  # System message with instructions
                {"role": "user", "content": prompt}  # User's prompt with the text to be processed
            ],
            temperature=0.0,  # Set the temperature to 0 for deterministic output
            max_tokens=256,  # Limit the response length
            top_p=1.0  # Use nucleus sampling with p=1.0 (deterministic output)
        )
        
        # Extract and clean the JSON response
        extracted_info_str = response.choices[0].message['content'].strip()
        extracted_info_json = json.loads(extracted_info_str)
    
    except openai.error.OpenAIError as e:
        # Handle errors from OpenAI API
        raise RuntimeError(f"OpenAI API error: {e}")
    except json.JSONDecodeError as e:
        # Handle JSON decoding errors
        raise RuntimeError(f"Error decoding JSON: {e}")
    except Exception as e:
        # Handle any other exceptions
        raise RuntimeError(f"Error during model generation: {e}")
    
    # Return the extracted information as a JSON object
    return extracted_info_json
