import pdfplumber
import pandas as pd

def PdfToTable(path):
    """
    Extracts tables from a PDF file and returns the combined data as a pandas DataFrame.
    
    :param path: Path to the PDF file.
    :return: A DataFrame containing the combined table data from all pages of the PDF.
    """
    # Open the PDF file
    pdf = pdfplumber.open(path)
    all_tables = []  # List to hold DataFrames of tables from each page
    
    # Iterate over each page in the PDF
    for page in pdf.pages:
        # Extract table from the current page
        table = page.extract_table()
        if table:
            # Convert the table data to a DataFrame
            df = pd.DataFrame(table[1:], columns=table[0])
            # Drop rows with missing values
            df = df.dropna()
            # Append the DataFrame to the list of tables
            all_tables.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    if all_tables:
        final_df = pd.concat(all_tables, ignore_index=True)
    else:
        # Return an empty DataFrame if no tables were found
        final_df = pd.DataFrame() 
    
    # Close the PDF file
    pdf.close()
    return final_df
