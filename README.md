# AI-Wealth-Manager
This project is designed to process and manage PDFs by setting up a Python environment and running the necessary scripts. Follow the instructions below to set up and run the project.

## Prerequisites

- Python 3.8.13 for PDF extraction
- Python 3.8.19 for managing the server

## Setup Instructions

### 1. Set Up Python Environment for PDF Extraction

1. **Create a virtual environment:**

    ```bash
    python3.8 -m venv env_pdf_extraction
    ```

2. **Activate the virtual environment:**

    - On Windows:
    
      ```bash
      env_pdf_extraction\Scripts\activate
      ```
    
    - On macOS/Linux:
    
      ```bash
      source env_pdf_extraction/bin/activate
      ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements_api.txt
    ```

4. **Run the API script:**

    ```bash
    python api.py
    ```

### 2. Set Up Python Environment for Management Server

1. **Create a virtual environment:**

    ```bash
    python3.8 -m venv env_management
    ```

2. **Activate the virtual environment:**

    - On Windows:
    
      ```bash
      env_management\Scripts\activate
      ```
    
    - On macOS/Linux:
    
      ```bash
      source env_management/bin/activate
      ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements_manage.txt
    ```

4. **Run the management server:**

    ```bash
    python manage.py runserver
    ```

5. **Open the web application:**

    Navigate to [http://localhost:3002](http://localhost:3002) in your web browser to process PDFs.

[Download AI Wealth Management Video](https://github.com/178shivam178/AI-Wealth-Management/raw/main/AI-wealth-management.mp4)


## Notes

- Ensure that you activate the correct virtual environment before running any scripts or commands.
- If you encounter any issues, check that all dependencies are installed and that the correct version of Python is being used.

## Troubleshooting

- **Database Connection Error:** Verify that the database connection settings are correctly configured in your `.env` file.
- **Missing Packages:** Ensure all packages listed in `requirements_api.txt` and `requirements_manage.txt` are installed.
- **Server Issues:** Check the terminal for error messages and ensure that the server is running correctly.

## Contact

For any questions or support, please contact us.
