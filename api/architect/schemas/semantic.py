from pydantic import BaseModel, Field
from typing import List
from .base import Node, NodeType

class IntentData(BaseModel):
    target: str = ""
    direction: str = ""

class ConstraintsData(BaseModel):
    inheritance_rules: List[str] = Field(default_factory=list)
    global_rules: List[str] = Field(default_factory=list)

class SemanticLayer(BaseModel):
    intent: Node[IntentData] = Field(default_factory=lambda: Node(data=IntentData(), type=NodeType.INTENT))
    constraints: Node[ConstraintsData] = Field(default_factory=lambda: Node(data=ConstraintsData(), type=NodeType.CONSTRAINTS))
