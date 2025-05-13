import time
import streamlit as st
import pytesseract
from PIL import Image
from agent_system_prompts import *
from agent_malicious_ip_detection.agent import EnhancedAgent
from orchestrator.orchestrator import Orchestrator
from agent_web_tavily.agent import AgentWebTavily
from agent_shodan.agent import AgentShodan
from agent_system_prompts.agent_system_prompts import *

# Session state to keep track of history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Try spawning the fastapi service in the background
import subprocess
subprocess.Popen(["fastapi","run","mcp_server/app.py"])

# classify the query and route it to the appropriate agent
ip_agent = EnhancedAgent(system=system_prompt_malicious_ip_detector)
web_agent = AgentWebTavily(system=system_prompt_tavily)
shodan_agent = AgentShodan(system=system_prompt_shodan)
agent_names_to_agent_map = {"malicious_ip_detection_virustotal": ip_agent, "web_search": web_agent,
                            "geography_and_vulnerabilities_for_ip": shodan_agent}

st.title("CyberShield")
st.write("Upload an image containing IP addresses. Let the agent use multiple data sources/tools like virus total, shodan to answer questions like malaciousness or ip reputation")

input_file_present = st.selectbox('Image Input file?', ('No', 'Yes'))
st.write('You selected:', input_file_present)

input_txt = ""
if input_file_present == "Yes":
    image_file = st.file_uploader('Upload the image')

    # wait until resume is uploaded
    while image_file is None:
        time.sleep(1)

    im = Image.open(image_file)
    text = pytesseract.image_to_string(im)

    input_prompt = st.text_area(
        "Ask a question from the uploaded image:",
        "Pick any IP address from the list and detect if it is malicious",
    )
    # Pass the ip addresses list as the context to the input_prompt
    if st.button("Submit"):
        st.session_state["history"].append({"role":"user", "content":input_prompt + "\n" + text})

        orchestrator = Orchestrator(agent_names_to_agent_map)

        response = orchestrator.thought_action_pause_observation_loop(max_iterations=10, query=input_prompt, context=text)
        st.write("Final response: %s" % response)

