from pydantic import BaseModel, Field
from typing import List
from .base import Node, NodeType

class ToolIO(BaseModel):
    name: str = ""
    type: str = ""

class ToolData(BaseModel):
    name: str = ""
    input: List[ToolIO] = Field(default_factory=list)
    processing: List[str] = Field(default_factory=list)
    output: List[ToolIO] = Field(default_factory=list)

class Tool(BaseModel):
    config: Node[ToolData] = Field(default_factory=lambda: Node(data=ToolData(), type=NodeType.TOOL))
