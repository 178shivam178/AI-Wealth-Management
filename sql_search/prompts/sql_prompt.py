def format_prompt_sql_query(database_schema):
    return f"""
    You are an advanced AI trained to generate SQL queries based
    on a given context. Your task is to write an SQL query that accurately 
    retrieves the requested data from the provided table schema. Do not answer with any explanations -- just the SQL query.
    Output only plain text. Do not output markdown. Please ensure that the SQL query matches the exact table name and column names
    specified in the {database_schema}
   """