import ast
import json
# Import necessary classes from LangChain for Tavily integration
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool

"""
Executes a web search using the TavilySearchResults tool.
Parameters:
    query (str): The search query entered by the user.
Returns:
    list: A list of search results containing answers, raw content, and images.
"""
class AgentWebTavily:
    def __init__(self, system_prompt: str = ""  ):
        self.name = "web_search"
        self.description = "Execute a web search using the TavilySearchResults tool."
        self.system_prompt = system_prompt

    def __call__(self, query: str):

        # Create an instance of TavilySearchResults with customized parameters
        search_tool = TavilySearchResults(
            max_results=5,  # Retrieves up to 5 search results
            include_answer=True,  # Includes direct answers when available
            include_raw_content=True,  # Includes full raw text content from search results
            include_images=True,  # Includes images from the search results
        )

        # Invoke the search with the given query and return the results
        return search_tool.invoke(query)
            