from pydantic import BaseModel, Field
from typing import List
from .base import Node, NodeType

class SequencerData(BaseModel):
    stages: List[str] = Field(default_factory=list)
    current_stage: str = ""

class RuntimeData(BaseModel):
    event_queue: List[str] = Field(default_factory=list)
    is_active: bool = False

class EngineSystem(BaseModel):
    sequencer: Node[SequencerData] = Field(default_factory=lambda: Node(data=SequencerData(), type=NodeType.SEQUENCER))
    runtime: Node[RuntimeData] = Field(default_factory=lambda: Node(data=RuntimeData(), type=NodeType.RUNTIME))
