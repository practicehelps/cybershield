import ast
import json
import os
from openai import OpenAI
# Import necessary classes from LangChain for Tavily integration
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
import streamlit as st

"""
Executes a web search using the TavilySearchResults tool.
Parameters:
    query (str): The search query entered by the user.
Returns:
    list: A list of search results containing answers, raw content, and images.
"""
class AgentWebTavily:
    def __init__(self, system: str = ""  ):
        self.openai_client = OpenAI(
          # This is the default and can be omitted
          api_key=os.environ.get("OPENAI_API_KEY"),
        )

        self.name = "web_search"
        self.description = "Execute a web search using the TavilySearchResults tool."
        self.system = system

        # Initialize an empty message list to track conversation history.
        self.messages = []

        # If a system message is provided, add it to the message history with the "system" role.
        if self.system:
            self.messages.append({"role": "system", "content": self.system})


    def __call__(self, query: str):

        self.messages.append({"role": "user", "content": query})
        #st.write("Web agent tavily called. Here is the message history so far:", self.messages)

        # Call OpenAI's chat completion API using the stored conversation history.
        response = self.execute()
        #st.write("openai response from web search via tavily= %s" % response)
 
        self.messages.append({"role": "assistant", "content": response})
        return response

    
    def execute(self):
        """Send messages to OpenAI's API and retrieve the response."""
        try:
            # Call OpenAI's chat completion API using the stored conversation history.
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo", messages=self.messages
            )   
            # st.write("tavily response = %s", response)
            return response.choices[0].message.content
        except Exception as e:
            print("openai exception %s" % e)
            return e
