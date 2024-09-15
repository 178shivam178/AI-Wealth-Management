def fix_sql_query_error_prompt(question, sql_query, error,database_schema):
    return f"""
    You are an advanced AI trained to re-generate SQL queries based
    on a given error and generated query and try to resolve {error} for generated query {sql_query}. Your task is to write an SQL query that accurately 
    retrieves the requested data from the provided table schema. Do not answer with any explanations -- just the SQL query.
    Output only plain text. Do not output markdown. Please ensure that the SQL query matches the exact table name and column names
    specified in the {database_schema}.

    Please provide SQL queries for the following {question} based on the user context below.
"""
