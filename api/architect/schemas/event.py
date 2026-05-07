from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from .base import Node, NodeType

class EventData(BaseModel):
    event_id: str = ""
    name: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)
    source: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)

class EventsSystem(BaseModel):
    history: List[EventData] = Field(default_factory=list)
    rules: Node[Dict[str, Any]] = Field(default_factory=lambda: Node(data={}, type=NodeType.GENERIC))
