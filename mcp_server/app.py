# mcp imports
from mcp_schema.schema import MCPContext
# fastapi imports
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
import streamlit as st
import os

# math_server.py
from mcp.server.fastmcp import FastMCP
from agent_malicious_ip_detection.agent import EnhancedAgent

from agent_system_prompts.agent_system_prompts import *

ip_agent = EnhancedAgent(system=system_prompt_malicious_ip_detector)

mcp = FastMCP("MaliciousIpDetection")
@mcp.tool()
def malicious_ip_detector(a: int, b: int) -> int:
    """Malicious IP Detection"""
    return a + b

# app = FastAPI()
# openai_client = OpenAI(
#     # This is the default and can be omitted
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )

# def execute(openai_client: OpenAI, model:str, history:list):
#     """Send messages to OpenAI's API and retrieve the response."""
#     try:
#         # Call OpenAI's chat completion API using the stored conversation history.
#         response = openai_client.chat.completions.create(
#             model=model, messages=history
#         )   
#         st.write("mcp server response based on open ai chat completion = %s", response)
#         return response.choices[0].message.content
#     except Exception as e:
#         print("openai exception %s" % e)
#         return e



# @app.post("/shodan")
# async def handle_shodan(request: Request):
#     data = await request.json()
#     context = MCPContext(**data)

#     response = execute(openai_client, context.llm_model, context.history)
#     return JSONResponse({"FastMCP Reply": f"[Shodan Response]: {response}"})

if __name__ == "__main__":
    mcp.run(transport="stdio")

