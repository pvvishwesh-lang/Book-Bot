from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

def web_search_client(search_query:str):
    tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    response=tavily_client.search(f"book {search_query} author description",max_results=5)
    return response
