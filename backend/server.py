from fastapi import FastAPI,status,APIRouter,HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from embedding import embedding
from search import search_database
from llm import llm_call,extract_book_info,is_followup,follow_up_llm_call
from web_search import web_search_client
from save_book import save_book_to_database
from langchain_postgres import PostgresChatMessageHistory
import os
from dotenv import load_dotenv
import psycopg
from langchain_core.messages import AIMessage, HumanMessage
from typing import Optional
from database import get_connection
from auth import verify_password,create_token,hash_password,decode_token
from jose import JWTError

load_dotenv()

app=FastAPI()  
router=APIRouter() 

origins=[
    "http://localhost:5173",
]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=['*'],allow_headers=["*"])
class ChatRequestBody(BaseModel):
    message:str
    session_id:str
    reading_history: Optional[list] = []
class ChatResponseBody(BaseModel):
    message:str
    session_id:str


def get_sync_connection():
    global sync_connection
    if sync_connection.closed:
        sync_connection = psycopg.connect(conn_info)
    return sync_connection

conn_info = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('HOST')}:5432/{os.environ.get('POSTGRES_DATABASE')}?options=-csearch_path%3D{os.environ.get('POSTGRES_SCHEMA')}"
table_name = os.environ.get('POSTGRES_MEMORY_TABLE')
sync_connection = psycopg.connect(conn_info)
PostgresChatMessageHistory.create_tables(get_sync_connection(), table_name)

@app.get("/health",status_code=status.HTTP_200_OK,tags=['home'])
async def get_status():
    return {"message":"Success"}


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload=decode_token(token)
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")



@app.post("/chat",tags=['chat'])
async def chat_model(request:ChatRequestBody,current_user=Depends(get_current_user)):
    print(f"1. REQUEST RECEIVED: {request.message}")
    embed_user_message=embedding(request.message)
    print("2. Embedding done")
    search_db=search_database(embed_user_message)
    print("3. Search done")
    chat_history=PostgresChatMessageHistory(
    table_name,
    request.session_id,
    sync_connection=get_sync_connection()
    )
    print("4. Chat history created")
    history = [{"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content} 
           for m in chat_history.messages]
    history = [m for m in history if "I am sorry but I am programmed" not in m['content']]
    clean_history = [
    msg
    for i in range(0, len(history)-1, 2)
    if history[i]['role'] == 'user' and history[i+1]['role'] == 'assistant'
    for msg in [history[i], history[i+1]]
    ]
    clean_history = clean_history[-8:]
    truncated_history = [{"role": m['role'], "content": m['content'][:800]}for m in clean_history]
    print("5. History loaded")
    followup_keywords = ["first one", "second one", "third one", "fourth one", "fifth one"
                        "last one", "previous one", "next one","number one","number two", "#1", "#2", "#3","the one", "that one"
                        "tell me more", "more about", "more info","that book", "this book", "the book","the author", "who wrote",
                        "written by","other books", "other works", "same author","trilogy", "series", "sequel", "prequel","next book", 
                        "next in", "continuation","other books in", "rest of","what about", "what else", "which one","is there", "are there",
                        "does it","how long", "how many", "when was","why is", "what is", "who is","can you", "could you", "tell me","expand on", 
                        "elaborate", "explain","similar to that", "like that", "like it","without", "instead", "different","less", "more like",
                        "shorter", "longer","by the same", "by that author"
                        ]
    if any(k in request.message.lower() for k in followup_keywords) and len(truncated_history) > 0:
        followup = True
    else:
        followup = is_followup(request.message, truncated_history)
    print(f"Is followup: {followup}")
    print(f"History length: {len(truncated_history)}")
    print(f"History content: {truncated_history}")
    if followup:
        llm_results = follow_up_llm_call(request.message, truncated_history)
    else:
        if not search_db or search_db[0][5] > 0.5:
            result=web_search_client(request.message)['results']
            web_books=list()
            for book in result:
                book_info=extract_book_info(book['content'])
                if book_info.get('title') and book_info.get('description'):
                    save_book_to_database(book_info['title'],book_info['author'],book_info['description'],book_info['subjects'])
                    web_books.append(book_info)
            llm_results=llm_call(request.message,web_books,truncated_history,request.reading_history)
        else:
            llm_results=llm_call(request.message,search_db,truncated_history,request.reading_history)
        print("6. LLM done")
    try:
        if "I'm currently experiencing high demand. Please try again in a moment." not in llm_results:
            chat_history.add_messages(
            [
                HumanMessage(content=request.message),
                AIMessage(content=llm_results)
            ]
            )
            get_sync_connection().commit()
    except Exception as e:
        print(f"Error saving messages: {e}")
    print(f"Messages saved for session: {request.session_id}")
    return {"response":llm_results}

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    token: str
    user_id: int
    name: str
    email: str

@router.post('/auth/register',tags=['auth'])
def registration(request: RegisterRequest):
    connection=get_connection()
    with connection.cursor() as conn:
        try:
            query=f"""SELECT 1 FROM {os.environ.get('POSTGRES_SCHEMA')}.users WHERE email = %s and name=%s"""
            conn.execute(query,(request.email,request.name))
            result=conn.fetchone()
            if result is not None:
                raise HTTPException(status_code=400, detail="Email already registered")
            else:
                password_pashed=hash_password(request.password)
                insert_query=f"INSERT INTO {os.environ.get('POSTGRES_SCHEMA')}.users (name,email,password_hash) VALUES (%s,%s,%s)"
                conn.execute(insert_query,(request.name,request.email,password_pashed))
                connection.commit()
            conn.execute(f"SELECT id FROM {os.environ.get('POSTGRES_SCHEMA')}.users where email=%s and name=%s",(request.email,request.name))
            user_id=conn.fetchone()
            token=create_token(user_id[0], request.email)
            return AuthResponse(token=token, user_id=user_id[0], name=request.name, email=request.email) 
        finally:
            connection.close()

@router.post('/auth/login',tags=['auth'])
def login(request:LoginRequest):
    connection=get_connection()
    with connection.cursor() as conn:
        try:
            query=f"SELECT id, name, email, password_hash FROM {os.environ.get('POSTGRES_SCHEMA')}.users WHERE email = %s"
            conn.execute(query,(request.email,))
            result=conn.fetchone()
            if result is None:
                raise HTTPException(status_code=400, detail="User does not exist! Please register")
            else:
                if verify_password(request.password,result[3]):                    
                    token=create_token(result[0],request.email,)
                    return AuthResponse(token=token, user_id=result[0], name=result[1],email=request.email) 
                else:
                    raise HTTPException(status_code=401, detail="Invalid credentials")
        finally:
            connection.close()




app.include_router(router)




