Securely detect flagged IP addresses from multiple databases, ensuring no PII sharing.

For the MCP server setup, please refer this:
https://medium.com/data-engineering-with-dremio/building-a-basic-mcp-server-with-python-4c34c41031ed

Why was langchain Agent APIs not directly used?
The application needed customizations like redacting PII data while trying to answer questions like finding maliciousness of a random sample of IP addresses.

Also, we wanted this to also act as a general chatbot, capable of answering questions from a RAG database or a web browser tool like Tavily.

Thus, these inclusions were implemented by defining separate agents with separate system prompts.

Also, from testing, we noticed that the out-of-the-box spacy models did not accurately detect the named entities and PII data.
The datasets used by spacy are not diverse enough to handle PII across different geographical regions.
For this reason, we had to fine tune the spacy models to handle the diverse use cases.

Spacy model use is currently disabled, as it needs more testing. It would be enabled after more testing.