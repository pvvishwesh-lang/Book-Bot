from groq import Groq,RateLimitError,APIStatusError
import os
from dotenv import load_dotenv
import json
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions
import time
load_dotenv()

GROQ_CLIENT=Groq(api_key=os.environ.get("GROQ_API_KEY"))
GEMINI_CLIENT=genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

def convert_history_for_gemini(history: list) -> list:
    gemini_history=[]
    for message in history:
        gemini_history.append(types.Content(role="model" if message['role'] == "assistant" else message['role'],parts=[types.Part(text=message['content'])]))
    return gemini_history

def call_llm(prompt:str,messages: str,history:list=[],max_completion_tokens:int=2000) -> str:
    primary_llm=os.environ.get("PRIMARY_LLM",'groq')
    if primary_llm.lower()=='groq':
        try:
            response=GROQ_CLIENT.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                max_completion_tokens=max_completion_tokens,
                #extra_body={"thinking": {"type": "disabled"}},
                messages=[
                {"role":"system","content":prompt},
                *history,
                {"role":"user","content":messages}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:#(RateLimitError, APIStatusError):
            print(f'Error: {e}')
            try:
                time.sleep(3)
                response=GEMINI_CLIENT.models.generate_content(
                model="gemini-3.5-flash",
                config=types.GenerateContentConfig(
                system_instruction=prompt,
                max_output_tokens=max_completion_tokens
                ),
                contents=[
                *convert_history_for_gemini(history),
                types.Content(role='user',parts=[types.Part(text=messages)])
                ]
                )
                return response.text
            except Exception:
                return "I'm currently experiencing high demand. Please try again in a moment."
    else:
        try:
            response=GEMINI_CLIENT.models.generate_content(
                model="gemini-3.5-flash",
                max_completion_tokens=max_completion_tokens,
                config=types.GenerateContentConfig(
                system_instruction=prompt,
                max_output_tokens=max_completion_tokens
                ),
                contents=[
                *convert_history_for_gemini(history),
                types.Content(role='user',parts=[types.Part(text=messages)])
                ]
            )
            return response.text
        except google_exceptions.ResourceExhausted:
            try:
                time.sleep(3)
                response=GROQ_CLIENT.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                max_completion_tokens=max_completion_tokens,
                #extra_body={"thinking": {"type": "disabled"}},
                messages=[
                {"role":"system","content":prompt},
                *history,
                {"role":"user","content":messages}
                ]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f'Error: {e}')
                return 'I am experiencing high demand, please try again later.'


def llm_call(user_message:str,search_results:list,history: list = [],reading_history: list = []):
    reading_context = ""
    if reading_history:
        for book in reading_history:
            reading_context += f"- {book['title']} | Author: {book['author']} | Rating: {book['rating']} | Shelf: {book['shelf']}\n"
    prompt=f"""
    You are a book recommendation assistant. You have access to a database with 1.5 million book data loaded into it. Use this
    database to search for and get the books that are similar to what the user requires. The user may also upload a file which contains
    their reading history from GoodReads, Fable etc. In that case, use the {reading_context}, which contains the title, author,rating and shelf,
    and recommend books based on what types of books they have in their shelf and what their average rating is for titles they have read.
    For example:
    User Message: Give me Books similar to Dune
    You: Sure, let me search for books similar to Dune...
         Search the Database
         Return Similar books based on Genre, Author, description and other metrics
    Always return atleast 5 books, no less. Ensure that it is not the same book in a different languages. Sequels are allowed as long 
    as user does not specify that they do not want any of the books sequels.
    Never give any other recommendations nor perform any other tasks. If user asks for anything other than books respond with the following
    message:
    I am sorry but I am programmed to only help you find your next book.
    References like "the first one", "the second one", "the last one", 
    "that book", "tell me more", "what about it", "the previous one",
    "the one before", "number X" are ALL follow-ups regardless of context.
    Always format your response as a numbered list (1. 2. 3. etc.) with each book on its own line.
    Never use "Title:", "Author:" prefixes- just use the format:
    1. **Book Title** by Author Name - Description  
    """
    context=""
    for i, book in enumerate(search_results):
        if isinstance(book, dict):
            title = book.get('title')
            author = book.get('author', '')
            description = book.get('description')
        else:
            title = book[1]
            author = book[2]
            description = book[4] 
        context += f"{i+1}. Title: {title} | Author: {author} | Description: {description}\n"
    full_prompt = f"{context}\n\nUser asked: {user_message}"
    response=call_llm(prompt, full_prompt, history)
    return response


def extract_book_info(raw_content: str,history: list = []) -> dict:
    prompt=f"""
    Given this raw text about a book, extract the following information:
    - title
    - author
    - description (2-3 sentences)
    - subjects (list of genres/themes)
    Return ONLY a JSON object with these fields, nothing else.
    Raw text: {raw_content}"""
    response=call_llm(prompt, raw_content, history)
    try:
        return json.loads(response)
    except:
        return {"title": "", "author": "Unknown", "description": raw_content[:300], "subjects": []}

def is_followup(message:str,history:list)->bool:
    prompt="""
    You will get the current message from the user and the user ai conversation history, which will be empty if it is the start of 
    the conversation. Your job is to classify based on conversation history and message context, if the message is a follow up or new
    search. In case a message is a follow up, it will reference a previous chat. If it is a fresh book search, it will not reference 
    anything. Tag Follow-Ups as 'followup' and new search as 'new_search' and return nothing else.
    Examples of follow-ups:
    - "Tell me more about the x one" = followup
    - "What about the x book?" = followup  
    - "Who wrote that?" = followup
    - "Is there a sequel?" = followup
    Examples of new searches:
    - "Give me books similar to Dune" = new_search
    - "Books about space exploration" = new_search
    """
    response=call_llm(prompt, message, history)
    response_text=response.strip().lower()
    if response_text=='followup':
        return True
    return False

def follow_up_llm_call(message:str,history:list=[]):
    prompt="""
    You are a book recommendation assistant.The user is asking a follow-up question about books previously discussed in the conversation.
    Use the conversation history to answer their question in detail. Only answer questions related to books. Do NOT say "I am sorry but I am programmed..." for follow-up questions about books already discussed.
    """
    max_completion_tokens=3000
    response=call_llm(prompt, message, history,max_completion_tokens)
    return response
