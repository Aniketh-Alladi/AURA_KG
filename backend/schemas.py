from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str = Field(..., description="The natural language question to ask the knowledge graph.", example="What tools does AURA-KG use?")
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of primary anchor nodes to retrieve.")


class SupportingNode(BaseModel):
    id: str = Field(..., description="Unique graph node identifier.")
    name: str = Field(..., description="Display name or title of the node.")
    type: str = Field(..., description="Domain label/type of the node (e.g., Tool, Person, Project).")
    relevance: str = Field(..., description="Role in context ('primary_match' or 'connected_context').")


class QueryResponse(BaseModel):
    query: str
    answer: str
    supporting_nodes: List[SupportingNode]