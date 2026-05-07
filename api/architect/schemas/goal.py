from pydantic import BaseModel, Field
from .base import Node, NodeType
from .semantic import SemanticLayer
from .state import StateSystem
from .event import EventsSystem
from .engine import EngineSystem
from .ui import UISystem

class GoalData(BaseModel):
    name: str = ""
    semantic_layer: SemanticLayer = Field(default_factory=SemanticLayer)
    state_system: StateSystem = Field(default_factory=StateSystem)
    # UNIFIED: features and relationships are now in config.children
    events: EventsSystem = Field(default_factory=EventsSystem)
    engine: EngineSystem = Field(default_factory=EngineSystem)
    ui: UISystem = Field(default_factory=UISystem)

class Goal(BaseModel):
    """The Root of the System Vision."""
    config: Node[GoalData] = Field(default_factory=lambda: Node(data=GoalData(), type=NodeType.GOAL))
