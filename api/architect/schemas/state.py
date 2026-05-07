from pydantic import BaseModel, Field
from typing import Dict, List, Any
from .base import Node, NodeType

class StateTransition(BaseModel):
    from_state: str = ""
    to_state: str = ""
    trigger: str = ""

class StateData(BaseModel):
    initial: Dict[str, Any] = Field(default_factory=dict)
    current: Dict[str, Any] = Field(default_factory=dict)
    transitions: List[StateTransition] = Field(default_factory=list)

class StateSystem(BaseModel):
    config: Node[StateData] = Field(default_factory=lambda: Node(data=StateData(), type=NodeType.STATE))
