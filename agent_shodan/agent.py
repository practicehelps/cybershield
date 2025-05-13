


import ast
import json
import os
import streamlit as st
import requests
from mcp_schema.schema import MCPContext
from openai import OpenAI

"""
Executes geography search and cve search for a given ip address
Parameters:
    query (str): ip address
Returns:
    list: A list of search results containing geographical data and cve data.
"""
class AgentShodan:
    def __init__(self, system: str = ""):
        self.openai_client = OpenAI(
          # This is the default and can be omitted
          api_key=os.environ.get("OPENAI_API_KEY"),
        )

        self.name = "geography_and_vulnerabilities_for_ip"
        self.description = "Executes geography search and cve search for a given ip address."
        self.system = system
        self.instructions = system
        st.session_state["history"].append({"role":"system", "content": self.instructions})

    def __call__(self, query: str):
        # Build MCP payload
        st.write("streamlit history", st.session_state["history"])
        mcp_context = MCPContext(
            user={"id": "0", "role": "user"},
            history=st.session_state["history"],
            instructions=self.instructions,
            llm_model="gpt-4-turbo",
        )

        # call the mcp server endpoint hosted via fast api
        # Replace with your MCP Server URL
        response = requests.post("http://localhost:8000/shodan", json=mcp_context.model_dump())

        if response.status_code == 200:
            reply = response.json()["reply"]
            st.session_state["history"].append({"role":"assistant", "content": reply})
        else:
            st.error("Failed to contact MCP server.")
 
        return response
