from pydantic import BaseModel
from typing import List,Dict, Any, Optional

class AgentState(BaseModel):
    messages: List[Dict[str, Any]]
    current_agent: str
    user_query: str
    extracted_text: Optional[str] = None
    final_response: Optional[str] = None

