from pydantic import BaseModel, Field
from .base import Node, NodeType
from .semantic import SemanticLayer
from .state import StateSystem

class FeatureData(BaseModel):
    name: str = ""
    semantic_layer: SemanticLayer = Field(default_factory=SemanticLayer)
    state_system: StateSystem = Field(default_factory=StateSystem)
    # UNIFIED: components and tools are now in config.children

class Feature(BaseModel):
    config: Node[FeatureData] = Field(default_factory=lambda: Node(data=FeatureData(), type=NodeType.FEATURE))
