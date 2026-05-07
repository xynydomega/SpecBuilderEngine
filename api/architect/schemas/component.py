from pydantic import BaseModel, Field
from typing import List, Optional
from .base import Node, NodeType
from .semantic import SemanticLayer
from .state import StateSystem

class ComponentData(BaseModel):
    name: str = ""
    description: Optional[str] = None
    structure: str = "generic" 
    semantic_layer: SemanticLayer = Field(default_factory=SemanticLayer)
    state_system: StateSystem = Field(default_factory=StateSystem)

class Component(BaseModel):
    config: Node[ComponentData] = Field(default_factory=lambda: Node(data=ComponentData(), type=NodeType.COMPONENT))
