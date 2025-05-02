import openai
import os
from openai import OpenAI
from pii_masker.pii_masker import PIIMasker, EnhancedPIIMasker
import streamlit as st

class MaliciousIpDetectorAgent:
    def __init__(self, system: str = ""):
        self.name = "malicious_ip_detector"
        self.description = "Execute a malicious ip detection using the virustotal api."
        """Initialize the agent with an optional system message and PII masking support."""
        # initialize the openai connection
        self.openai_client = OpenAI(
          # This is the default and can be omitted
          api_key=os.environ.get("OPENAI_API_KEY"),
        )

        # Store the system message if provided.
        self.system = system

        # Initialize an empty message list to track conversation history.
        self.messages = []

        # Create an instance of the PII masker to handle sensitive data.
        self.pii_masker = PIIMasker()

        # If a system message is provided, add it to the message history with the "system" role.
        if self.system:
            self.messages.append({"role": "system", "content": self.system})

    def __call__(self, message=""):
        """Process a user message, mask PII, send it to OpenAI, and return the response."""
        if message:
            # Apply PII masking before sending the message to the OpenAI API.
            masked_message = self.pii_masker.mask(message)

            # Append the masked user message to the conversation history.
            self.messages.append({"role": "user", "content": masked_message})
            print(self.messages)
            # Call the execution method to get a response from the OpenAI API.
            response = self.execute()

            # Apply PII masking to the received response before returning it.
            #masked_response = self.pii_masker.mask(response)

            # Append the masked assistant response to the conversation history.
            self.messages.append({"role": "assistant", "content": response})

            # Call PII unmasking to masked response
            unmasked_response = self.pii_masker.unmask(response)

            return unmasked_response

    def execute(self):
        """Send messages to OpenAI's API and retrieve the response."""
        try:
            # Call OpenAI's chat completion API using the stored conversation history.
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo", messages=self.messages
            )
            print("openai response = %s" % response)

            # Extract and return the response content from the API's output.
            return response.choices[0].message.content

        except Exception as e:
            # Handle errors that may occur during the API request.
            # Return a formatted error message with details.
            print("openai exception %s" % e)
            return e

# Enhanced Agent class with improved PII masking capabilities.
class EnhancedAgent(MaliciousIpDetectorAgent):
    def __init__(self, system: str = "") -> None:
        """Initialize the agent with an enhanced PII masker and custom detection pipeline."""
        # Call the parent class constructor to inherit existing functionality.
        super().__init__(system)
        self.name = "malicious_ip_detection"
        self.description = "Execute a malicious ip detection using the virustotal api."

        # Initialize the enhanced PII masker with extended capabilities.
        self.pii_masker = EnhancedPIIMasker()
