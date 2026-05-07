from pydantic import BaseModel, Field
from typing import Dict, Optional
from .base import Node, NodeType, RelationshipType

class RelationshipData(BaseModel):
    type: RelationshipType = RelationshipType.DEPENDENCY
    source_node_id: str = ""
    target_node_id: str = ""
    on_trigger: str = ""
    condition: Optional[str] = None
    data_mapping: Dict[str, str] = Field(default_factory=dict)

class Relationship(BaseModel):
    config: Node[RelationshipData] = Field(default_factory=lambda: Node(data=RelationshipData(), type=NodeType.RELATIONSHIP))
