# import the 'tool' decorator
from langchain.tools import tool
from agent.agent import EnhancedAgent
import os
import requests
import streamlit as st

# Define a system prompt that sets the behavior of the AI assistant.
# Ensure the prompt includes guidelines on how responses should be structured.
# Include rules for clarity, handling of sensitive information, and accuracy.
system_prompt = """
You are a cybersecurity agent. You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop, you output an Answer.

Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:
malicious_ip_detection_virustotal:
e.g. malicious_ip_detection_virustotal: IP
Performs a VirusTotal lookup for a IP.

Question: Check if the IP 8.8.8.8 is malicious.
Thought: I should perform a VirusTotal lookup for the IP.
Action: malicious_ip_detection_virustotal: 8.8.8.8
PAUSE

You will be called again with this:
Observation: {"data": "VirusTotal data for 8.8.8.8"}
Thought: I think I have found the answer.
Action: Answer: The IP 8.8.8.8 is malicious based on VirusTotal data.

Now it's your turn:
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
    print(response.json())
    response_json = response.json()
    if response.status_code == 200 and 'detected_urls' in response_json and len(response_json['detected_urls']) > 0:
        return response_json['detected_urls']
    return None

tools = {"malicious_ip_detection_virustotal": malicious_ip_detection_virustotal}

def thought_action_pause_observation_loop(max_iterations=10, query: str = ""):
    """Main interaction loop for the agent."""

    # Initialize the enhanced agent with the system prompt.
    agent = EnhancedAgent(system=system_prompt)

    # Set the initial query and iteration counter.
    query = query
    i = 0
    while i < max_iterations:
        i += 1  # Increment the loop counter.

        # Process the current prompt using the agent.
        resp = agent.__call__(query)

        # Retrieve and print the response.
        st.write("\n agent response from openai call: \n%s\n" % resp)

        # Check if the response contains a "PAUSE" signal indicating an action request.
        if "PAUSE" in resp:
          # Use a regular expression to extract the requested action and its argument.
          action_match = resp.split("\n")[1]
          action_match = action_match.split("Action:")
          if len(action_match) < 2:
            continue
          else:
            action_match = action_match[1]
            action_match = action_match.split(":")
            print("action match = %s" % action_match)

        resp = ""
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
                resp = tools[chosen_tool](str(arg))

                # Capture the tool's output and truncate it if necessary.
                st.write("tool response is %s" % resp)

                if resp is None:
                  print("Not malicious")
                  return "Not malicious"

                resp = truncate_response(resp)

                # Mask PII in the tool result before sending it back into the loop.

                # Update the next prompt with the tool's output for further processing.
                print("Malicious")  
                return "Malicious"

        # Check if the response contains an "Answer" signal, indicating completion.
        if "Answer" in resp or "Not malicious" in resp:
          break

    return resp


