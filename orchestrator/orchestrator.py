from openai import OpenAI
import os
import streamlit as st
from utils.utils import truncate_response
from tools.tools import *
from concurrent.futures import ProcessPoolExecutor
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_fixed)

class Orchestrator:
    def __init__(self, agent_names_to_agent_map):
        self.agent_names_to_agent_map = agent_names_to_agent_map
        self.system = self.get_system_prompt(agent_names_to_agent_map.values())

        # initialize the openai connection
        self.openai_client = OpenAI(
          # This is the default and can be omitted
          api_key=os.environ.get("OPENAI_API_KEY"),
        )

        # Initialize an empty message list to track conversation history.
        self.messages = []

        # If a system message is provided, add it to the message history with the "system" role.
        if self.system:
            self.messages.append({"role": "system", "content": self.system})      

    def get_system_prompt(self, agents):
        return f"""
        You are an expert agent classifier.
        You will use the user's input and select the appropriate agents to route the query to.

        Here are the available agents and their descriptions:
        {", ".join([f"- {agent.name}: {agent.description}" for agent in agents])}

        If the query is related to maliciousness of IP addresses, you must use the malicious_ip_detection agent.
        If the query is related to the geography and vulnerabilities for a specific IP address, you must first use the malicious_ip_detection agent,
        and then use the geography_and_vulnerabilities_for_ip agent.
        For all other queries, you must use the web_search agent.

        If the query needs  malicious_ip_detection,  geography_and_vulnerabilities_for_ip and web_search agents, you return the malicious_ip_detection agent first,
        folowed by geography_and_vulnerabilities_for_ip agent, followed by the web_search agent.

        Return the agent names in the response, separated by a comma.

        Also, you might be asked to summarize some content. Please do that if requested.
        """    

    def __call__(self, message=""):
        """Process a user message, send it to OpenAI, and return the response."""
        if message:
            self.messages.append({"role": "user", "content": message})

        # Call the OpenAI API to generate a response.
        response = self.execute()        
        st.write("orchestrator response = %s" % response)

        # Add the response to the message history.
        self.messages.append({"role": "assistant", "content": response})
        return response

    def execute(self):
        """Send messages to OpenAI's API and retrieve the response."""
        try:
            # Call OpenAI's chat completion API using the stored conversation history.
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo", messages=self.messages
            )

            # Extract and return the response content from the API's output.
            return response.choices[0].message.content

        except Exception as e:
            # Handle errors that may occur during the API request.
            # Return a formatted error message with details.
            print("openai exception %s" % e)
            return e        

    def thought_action_pause_observation_loop(self, max_iterations=10, query: str = "", context: str = ""):
        # Pass the query to the orchestrator. It follows the Workflow: Orchestrator-workers design pattern
        # Ref: https://www.anthropic.com/engineering/building-effective-agents
        resp = self.__call__(query + "\n\n" + context + "\n\n" + "Please select the agent to route the query to.")
        st.write("orchestrator response: %s" % resp)

        # remove the white spaces and split the response by comma
        agent_names = resp.strip().split(",")
        agent_names = [name.strip() for name in agent_names]
        resp = ""

        # TODO: get the response from the agents in parallel
        # Streamlit has problems with parallel tasks.
        final_response = ""

        for agent in agent_names:
            agent_obj = self.agent_names_to_agent_map[agent]
            response = self.get_response(agent_obj, query + "\n" + context, max_iterations)
            st.write("response from agent", agent)
            st.write(response)
            #st.write("Here is the message history of all calls to LLM to answer the question:", "Agent" + agent_obj.name, agent_obj.messages)

            final_response += response

        resp = self.__call__(final_response + "\n" + "Summarize the given content.")
        return resp


    def get_response(self, agent, query, max_iterations):
        i = 0
        answers_confirmed = 0
        action_match = []    
        resp = ""
        tool_resp = ""
        while i < max_iterations:
            # Check if the response contains an "Answer" signal, indicating completion.
            if "Final Answer" in resp:
                return resp
            
            i += 1  # Increment the loop counter.

            # Process the current prompt using the agent.
            resp = agent.__call__(query)

            # Retrieve and print the response.
            st.write("\n orchestrator agent response from openai call: \n%s\n" % resp)

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

                    if chosen_tool in all_tools.keys():
                        # Unmask PII in the extracted argument if necessary.
                        st.write("chosen tool %s found" % chosen_tool)

                        # Execute the tool using the provided argument.
                        tool_resp = all_tools[chosen_tool](str(arg))

                        # Capture the tool's output and truncate it if necessary.
                        st.write("tool response is %s" % tool_resp)
                        
                        if tool_resp is None:
                            print("No record found for %s" % arg)                  
                            continue
                    
                        tool_resp = truncate_response(tool_resp)

                        # Update the next prompt with the tool's output for further processing.                 
                        query =  tool_resp

            # Check if the response contains an "Answer" signal, indicating completion.
            if "Final Answer" in resp:
                return resp

        return resp
        
                