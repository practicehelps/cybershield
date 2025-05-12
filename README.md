Securely detect flagged IP addresses from multiple databases, ensuring strict PII confidentiality between client and server.


What kind of agent orchestration framework was used?
It follows the Workflow: Orchestrator-workers design pattern
Reference: https://www.anthropic.com/engineering/building-effective-agents

Why were langchain Agent APIs and CrewAI APIs not directly used?
As previously detailed by Harrison Chase from langchain, we had to balance the autonomous nature of the agents with the control needed over the agents for the specific use case.

Choosing between Horizontal Agents and Vertical Agents:
Reference: https://relevanceai.com/blog/ai-agents-vertical-vs-horizontal-whats-best-for-you

Since the application is handling a lot of PII data, we want the application to not leak any PII data while answering the questions.
Thus, we lean in to use vertical agents, which are heavily customized to redact all PII data on the client side itself.

While answering questions like finding maliciousness of a random sample of IP addresses, we wanted the application to redact the PII data like IP addresses, credit card numbers,
on the client side itself, instead of relying on the models on the server side. This ensures strict confidentiality on the client side itself.

At the same time, we also wanted the same chatbot to be able to answer generic questions like scraping the latest CVEs from the web.
Thus, this part was handled by a horizontal agent via the tavily tool.

Named entity recognition functionality: (In Progress)
From testing, we noticed that the out-of-the-box spacy NLP datasets like en_core_web_sm did not accurately detect the named entities and PII data.
The datasets used by spacy are not diverse enough to handle PII across different geographical regions.
For this reason, we had to fine tune the spacy models to handle the diverse use cases.

Spacy model use is currently disabled, as it needs more testing. It would be enabled after more testing.
It also seems promising to use the presidio libraries that are built on top of the spacy libraries.

Does it use MCP (Model Context Protocol)? (In Progress)
https://medium.com/data-engineering-with-dremio/building-a-basic-mcp-server-with-python-4c34c41031ed
Currently, the plan is to let the Shodan agent uses the MCP protocol. We are considering to migrate more components to adhere to the MCP protocol.

How and why is Shodan used?
For more detailed questions about the city hosting the IP address, and the vulnerabilities present on the entity (server, router),
the shodan database is able to answer these effectively.
Thus, the orchestrator routes these queries to the shodan agent at these URLs:
1. Geographical data (city): https://www.shodan.io/host/189.219.36.213
2. CVEs: https://internetdb.shodan.io/222.128.28.51

Does the solution hallucinate and have indeterministic nature in rare cases?
Yes, in rare scenarios, the solution does hallucinate. The agents in rare cases are unable to distinguish the request to focus on the given input,
and not on the sample inputs given in the prompt.