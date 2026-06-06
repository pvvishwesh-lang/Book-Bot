import os
from dotenv import load_dotenv
import uuid
from embedding import embedding
from database import get_connection
load_dotenv()
def save_book_to_database(title,author,description,subjects):
    ol_id=f"web_{uuid.uuid4()}"
    subjects_str = ", ".join(subjects)
    embedding_str=f"title: {title} |subjects: {subjects_str} |description: {description[:300]}"
    embedded_data=embedding(embedding_str)
    query=f"""INSERT INTO {os.environ.get('POSTGRES_SCHEMA')}.book (ol_id,title,author,subjects,description,embedding) VALUES (%s, %s, %s, %s, %s, %s)"""
    conn=get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query,(ol_id, title, author, subjects, description, embedded_data))
        conn.commit()
    conn.close()
    return {"status": "success", "ol_id": ol_id} 