from openai import OpenAI
import os
import streamlit as st
class Orchestrator:
    def __init__(self, system: str = ""):
        self.system = system

        # initialize the openai connection
        self.openai_client = OpenAI(
          # This is the default and can be omitted
          api_key=os.environ.get("OPENAI_API_KEY"),
        )

        # Store the system message if provided.
        self.system = system

        # Initialize an empty message list to track conversation history.
        self.messages = []

        # If a system message is provided, add it to the message history with the "system" role.
        if self.system:
            self.messages.append({"role": "system", "content": self.system})        

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
            st.write("openai response from orchestrator = %s" % response)

            # Extract and return the response content from the API's output.
            return response.choices[0].message.content

        except Exception as e:
            # Handle errors that may occur during the API request.
            # Return a formatted error message with details.
            print("openai exception %s" % e)
            return e        

    def add_agent(self, agent):
        self.agents.append(agent)

    def remove_agent(self, agent):
        self.agents.remove(agent)   

    def get_agents(self):
        return self.agents

    def get_system_prompt(self):
        return self.system_prompt
    
    def find_agent_for_query(self, query):
        # check if query is
        pass
        
        