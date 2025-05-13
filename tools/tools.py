
# import the 'tool' decorator
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
import requests
import streamlit as st
import re
import os
#import shodan

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
        
    return "Ip address %s is not malicious. Detailed response from VirusTotal: %s" % (ip_address, response.json())

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

@tool
def get_city_from_ip(query: str):
    """Get the city from the IP address"""
    # key = os.getenv("SHODAN_API_KEY")
    # api = shodan.Shodan(os.environ.get("SHODAN_API_KEY"))
    # host = api.host(query)
    # return host.get('city', 'n/a')
    return str(requests.get(f"https://www.shodan.io/host/{query}").content)

@tool
def get_vulnerabilities_for_ip(query: str):
    """ Get the vulns associated with the ip address"""
    # key = os.getenv("SHODAN_API_KEY")
    # api = shodan.Shodan(os.environ.get("SHODAN_API_KEY"))
    # host = api.host(query)
    # return host.get('city', 'n/a')
    return str(requests.get(f"https://internetdb.shodan.io/{query}").content)



all_tools = {"malicious_ip_detection_virustotal": malicious_ip_detection_virustotal, "get_ip_address_from_text": get_ip_address_from_text,
             "get_city_from_ip": get_city_from_ip,
             "get_vulnerabilities_for_ip": get_vulnerabilities_for_ip,
             "search_tavily": search_tavily}
