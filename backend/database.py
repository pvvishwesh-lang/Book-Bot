from dotenv import load_dotenv
import os
import psycopg2
from pgvector.psycopg2 import register_vector

def get_connection():
    load_dotenv()
    conn=psycopg2.connect(
    database=os.environ.get("POSTGRES_DATABASE"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("HOST"),
    port=os.environ.get("PORT")
    )
    register_vector(conn)
    return conn
