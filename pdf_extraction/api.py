from flask import Flask, request, jsonify, render_template
import fitz
import os
import werkzeug.utils
import logging
from src.info import extract_entities
from src.transaction import PdfToTable
from src.insert_db import insert_data_to_db
import json
import mysql.connector

# Initialize Flask app
app = Flask(__name__)

# Configuration for file upload settings
UPLOAD_FOLDER = 'uploads'  # Directory to save uploaded files
ALLOWED_EXTENSIONS = {'pdf'}  # Allowed file extensions
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max file size limit (16 MB)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create the upload folder if it does not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    """
    Check if the file has an allowed extension.
    
    :param filename: The name of the file.
    :return: True if file extension is allowed, otherwise False.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    """
    Securely format the file name to prevent path traversal attacks.
    
    :param filename: The original file name.
    :return: A secure file name.
    """
    return werkzeug.utils.secure_filename(filename)

def process_pdf(file_path):
    """
    Process the uploaded PDF file: extract key entities and table data, and insert into the database.
    
    :param file_path: The path to the uploaded PDF file.
    :return: A response dictionary and HTTP status code.
    """
    try:
        # Open the PDF file
        with fitz.open(file_path) as pdf_document:
            # Check if the PDF is empty
            if len(pdf_document) == 0:
                return {'error': 'Empty PDF document'}, 400
            
            # Extract text from the first page
            first_page = pdf_document.load_page(0)
            text = first_page.get_text()
            text_to_process = text[:500]  # Limit text to process for entity extraction

            # Extract key entities from the text
            key_entities = extract_entities(text_to_process)
            key_entities = json.dumps(key_entities, indent=2)
            if 'error' in key_entities:
                logging.error(f'Error in extract_entities_external: {key_entities["error"]}')
                return {'error': 'Error extracting entities from the text'}, 500
            
            # Extract tables from the PDF and convert to DataFrame
            df = PdfToTable(file_path)
            if df.empty:
                logging.error('Error in PdfToTable: No tables found in the PDF document')
                return {'error': 'Error extracting tables from the PDF document'}, 500
            
            # Convert DataFrame to a list of dictionaries
            transaction_data = df.to_dict(orient='records')
            # Insert extracted data into the database
            insert_data_to_db(key_entities, transaction_data)

        return {
            'message': 'PDF processed and data inserted successfully'
        }, 200

    except mysql.connector.Error as err:
        logging.error(f'MySQL error: {err}')
        if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
            return {'error': 'Duplicate entry found in the database'}, 409
        return {'error': 'Database error occurred'}, 500
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return {'error': str(e)}, 500
    finally:
        # Clean up: remove the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f'File removed after processing: {file_path}')

@app.route('/')
def index():
    """
    Render the index page.
    :return: Rendered HTML template.
    """
    return render_template('index.html')

@app.route('/upload-and-process', methods=['POST'])
def upload_and_process_file():
    """
    Handle file upload, process the PDF, and return the result.
    :return: JSON response with the result of PDF processing.
    """
    # Check if the file part is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if the file has an allowed extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    # Secure the filename and save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(file_path)
        logging.info(f'File uploaded: {file_path}')

        # Process the PDF and get the result
        result, status_code = process_pdf(file_path)
        return jsonify(result), status_code

    except Exception as e:
        logging.error(f'Error processing file: {e}')
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3002, debug=True)
