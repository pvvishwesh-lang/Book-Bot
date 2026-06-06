import os
from dotenv import load_dotenv
from database import get_connection
load_dotenv()
def search_database(query_vector:list,top_k=10)->list:
    sql_query=f"""
    SELECT ol_id,title,author,subjects,description,embedding <=> %s::vector AS score
    FROM {os.environ.get('POSTGRES_SCHEMA')}.book
    ORDER BY embedding <=> %s::vector
    LIMIT %s;
    """
    conn=get_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql_query,(query_vector, query_vector, top_k))
        records=cursor.fetchall()
    conn.close()
    return records

