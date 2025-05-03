# import the 'tool' decorator
from langchain.tools import tool
from agent_malicious_ip_detection.agent import EnhancedAgent
from agent_web_tavily.agent import AgentWebTavily
from langchain_community.tools.tavily_search import TavilySearchResults
from orchestrator.orchestrator import Orchestrator

import os
import re
import requests
import streamlit as st



# Define a system prompt that sets the behavior of the AI assistant.
# Ensure the prompt includes guidelines on how responses should be structured.
# Include rules for clarity, handling of sensitive information, and accuracy.
system_prompt_malicious_ip_detector = """
You are a cybersecurity agent. You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop, you output an Answer.

Please note that the IP addresses provided are masked by using uuid.
So, just return the IP addresses in the original format.

The final answer should clearly state the IP addresses and whether they are malicious or not.

Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:
malicious_ip_detection_virustotal:
e.g. malicious_ip_detection_virustotal: IP
Performs a VirusTotal lookup for a IP.

get_ip_address_from_text:
e.g. get_ip_address_from_text: text
Extracts IP addresses from text.

Following is the format number 1 of the question:
Question: Check if the IP 8.8.8.8 is malicious.
Thought: I should perform a VirusTotal lookup for the IP.
Action: malicious_ip_detection_virustotal: 8.8.8.8
PAUSE

You will be called again with this:
Observation: {"data": "tool response is The IP address 8.8.8.8 is malicious based on the following URLs"}
Thought: I think I have found the answer.
Action: Final Answer: The IP 8.8.8.8 is malicious based on VirusTotal data.
End of format number 1.

Following is the format number 2 of the question:
Question: Check if IP addresses 5.5.5.5 and 4.4.4.4 are malicious.
Thought: I should perform a VirusTotal lookup for IP 5.5.5.5 first.
Action: malicious_ip_detection_virustotal: 5.5.5.5
PAUSE

You will be called again with this:
Observation: {"data": tool response is The IP address  5.5.5.5 is malicious based on the following URLs"}
Thought: I think I have found one answer.
Action: Answer: The IP 5.5.5.5 is malicious based on VirusTotal data.

Thought: IP 5.5.5.5 is malicious. Now, I need to perform a VirusTotal lookup for 4.4.4.4
Action: malicious_ip_detection_virustotal: 4.4.4.4
PAUSE

You will be called again with this:
Observation: {"data": "tool response is The IP address 4.4.4.4 is not malicious based on the following URLs"}
Thought: I think I have found the next answer.
Action: Answer: The IP 4.4.4.4 is not malicious based on VirusTotal data.

Thought: I have found answers for both the IP addresses.
Action: Final Answer: IP 5.5.5.5 is malicious and IP 4.4.4.4 is not malicious.
End of format number 2.

Now it's your turn:
"""

system_prompt_tavily = """
You are a web search agent, also called a tavily agent. You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop, you output an Answer.

For any questions not related to maliciousness of IP addresses, you must use the search_tavily tool.

Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:
search_tavily:
e.g. search_tavily: query
Performs a web search using the TavilySearchResults tool for the given query.

Following is an example question:
Question: Check the latest news on the stock market.
Thought: I should perform a web search for the latest news on the stock market.
Action: search_tavily: latest news on the stock market
PAUSE

You will be called again with this:
Observation: {"data": "stock market today is doing well"}
Thought: I think I have found the answer.
Action: Final Answer: stock market today is doing well

End of example question 1.

Here is another example question:
Question: What is the weather in Tokyo?
Thought: I should perform a web search for the weather in Tokyo.
Action: search_tavily: weather in Tokyo
PAUSE

You will be called again with this:
Observation: {"data": "Weather in Tokyo is sunny and warm with a temperature of 25 degrees Celsius."}
Thought: I think I have found the answer.
Action: Final Answer: Weather in Tokyo is sunny and warm with a temperature of 25 degrees Celsius.
End of example question 2.

Now it's your turn:
"""

# classify the query and route it to the appropriate agent
ip_agent = EnhancedAgent(system=system_prompt_malicious_ip_detector)
web_agent = AgentWebTavily(system=system_prompt_tavily)

agents = [ip_agent, web_agent]

system_prompt_orchestrator = f"""
You are an orchestrator. You are responsible for orchestrating the agents.
You will be given a query and you will need to determine which agent to route the query to.
You have the following agents available to you:


You are an expert intent classifier.
You need will use the user's input to classify the intent and select the appropriate agent.                

Here are the available agents and their descriptions:
{", ".join([f"- {agent.name}: {agent.description}" for agent in agents])}

Return the agent name in the response.

"""

def truncate_response(response, max_length=1000):
    """Truncate and format API responses to prevent token limit issues."""

    response_str = ""
    # Check if the response is a dictionary.
    if  isinstance(response, dict):
      # Convert the dictionary to a string representation for length evaluation.
      response_str = str(response)

    # Check if the length of the string exceeds the maximum allowed length.
    if len(response_str) > max_length:
        # If it exceeds, truncate the string to the specified maximum length.
        truncated_response = response_str[:max_length]
        # - Append a marker to indicate truncation
        response_str += "#"

    return response_str

@tool
def malicious_ip_detection_virustotal(ip_address: str):
    """Search for maliciousness of the IP address.
    For any questions related to maliciousness of IP, this tool must be used."""
    key = os.getenv("VIRUSTOTAL_API_KEY")
    #ip_address = "222.128.28.51"
    url = 'https://www.virustotal.com/vtapi/v2/ip-address/report'
    params = {'apikey': key, 'ip': ip_address}
    response = requests.get(url, params=params)
    if response is None or response.status_code != 200:
       return None
    
    st.write("json response from virus total:\n%s" % response.json())
    response_json = response.json()

    if response.status_code == 200 and 'detected_urls' in response_json and len(response_json['detected_urls']) > 0:
        response_json = response.json()
        return "The IP address %s is malicious based on the following URLs: %s" % (ip_address, response_json['detected_urls'])
        
    return "Ip address %s is not malicious" % ip_address

@tool
def get_ip_address_from_text(text: str):
    """Extract IP addresses from text.
    For any questions related to extracting IP addresses from text, this tool must be used."""
    ip_list = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', text)
    return ip_list

@tool
def search_tavily(query: str):
    """Search the web for information."""
    # Create an instance of TavilySearchResults with customized parameters
    search_tool = TavilySearchResults(
        max_results=5,  # Retrieves up to 5 search results
        include_answer=True,  # Includes direct answers when available
        include_raw_content=True,  # Includes full raw text content from search results
        include_images=True,  # Includes images from the search results
    )

    # Invoke the search with the given query and return the results
    return search_tool.invoke(query)    

tools = {"malicious_ip_detection_virustotal": malicious_ip_detection_virustotal, "get_ip_address_from_text": get_ip_address_from_text, "search_tavily": search_tavily}
agent_names_to_agent_map = {"malicious_ip_detection": ip_agent, "web_search": web_agent}

def thought_action_pause_observation_loop(max_iterations=10, query: str = "", context: str = ""):
    """Main interaction loop for the agent."""

    # first call the orchestrator to get the agent name
    orchestrator = Orchestrator(system=system_prompt_orchestrator)
    resp = orchestrator.__call__(query + "\n\n" + context + "\n\n" + "Please select the agent to route the query to.")
    st.write("orchestrator response: %s" % resp)

    agent_name = resp.strip()
    agent = agent_names_to_agent_map[agent_name]
    if agent_name == "malicious_ip_detection":
       query = query + "\n" + context

    results_so_far = ""
    i = 0
    answers_confirmed = 0
    action_match = []
    resp = ""
    while i < max_iterations:
        # Check if the response contains an "Answer" signal, indicating completion.
        if "Final Answer" in resp:
          break
        
        i += 1  # Increment the loop counter.

        # Process the current prompt using the agent.
        resp = agent.__call__(query)

        # Retrieve and print the response.
        st.write("\n agent response from openai call: \n%s\n" % resp)

        # Check if the response contains a "PAUSE" signal indicating an action request.
        if "PAUSE" in resp:
          # Use a regular expression to extract the requested action and its argument.
          action_match = resp.split("PAUSE")[0]
          action_match = action_match.split("Action:")
          if len(action_match) < 2:
            continue
          else:
            action_match = action_match[1]
            action_match = action_match.split(":")
            print("action match = %s" % action_match)

        if len(action_match) == 2:
            chosen_tool, arg = action_match[0].strip(), action_match[1].strip()  # Extract tool name and argument.
            print("chosen tool = %s, arg = %s" % (chosen_tool, arg))

            # Verify that the requested tool exists in the available tools list.
            # If not found, set an appropriate response and continue.

            if chosen_tool in tools.keys():
                # Unmask PII in the extracted argument if necessary.
                st.write("chosen tool %s found" % chosen_tool)

                # Ensure the argument is properly formatted as a string for execution.

                # Execute the tool using the provided argument.
                tool_resp = tools[chosen_tool](str(arg))

                # Capture the tool's output and truncate it if necessary.
                st.write("tool response is %s" % tool_resp)
                answers_confirmed += 1
                
                if tool_resp is None:
                  print("No record found for %s" % arg)                  
                  continue
                
                tool_resp = truncate_response(tool_resp)

                # Mask PII in the tool result before sending it back into the loop.

                # Update the next prompt with the tool's output for further processing.                 
                query =  tool_resp + "\n" + "answers found so far: %d" % answers_confirmed

        # Check if the response contains an "Answer" signal, indicating completion.
        if "Final Answer" in resp:
          break

    return resp


