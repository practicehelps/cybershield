# Ref: https://www.comparepriceacross.com/post/host_mcp_client_or_server_using_streamlit/
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
from openai import OpenAI

class MCPContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user: Dict[str, str]
    history: List[Dict]
    tools: Optional[Dict[str, str]] = {}
    instructions: Optional[str] = ""
    llm_model: Optional[str] = ""