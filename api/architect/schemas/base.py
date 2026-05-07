from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List, Any, Dict, Union, Generator
from datetime import datetime
from enum import Enum
from uuid import uuid4

T = TypeVar('T')

class NodeType(str, Enum):
    GOAL = "goal"
    FEATURE = "feature"
    COMPONENT = "component"
    TOOL = "tool"
    STATE = "state"
    INTENT = "intent"
    CONSTRAINTS = "constraints"
    RELATIONSHIP = "relationship"
    SEQUENCER = "sequencer"
    RUNTIME = "runtime"
    GENERIC = "generic"

class RelationshipType(str, Enum):
    PARENT_CHILD = "parent_child"
    TOOL_TO_STATE = "tool_to_state"
    COMPONENT_TO_TOOL = "component_to_tool"
    EVENT_TRIGGER = "event_trigger"
    DATA_MAPPING = "data_mapping"
    DEPENDENCY = "dependency"

class NodeStatus(str, Enum):
    PENDING = "pending"
    EXTRACTED = "extracted"
    CONFLICT = "conflict"
    CONFIRMED = "confirmed"
    LOCKED = "locked"

class NodeMeta(BaseModel):
    """Agentic metadata for the node."""
    required: bool = True
    confidence: float = 0.0
    status: NodeStatus = NodeStatus.PENDING
    source: str = "none"
    last_updated: Optional[datetime] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

class RelationshipRef(BaseModel):
    """A pointer to another node with a specific relationship type."""
    target_id: str
    relationship_type: RelationshipType = RelationshipType.DEPENDENCY

class Node(BaseModel, Generic[T]):
    """
    The Universal Execution Primitive.
    UNIFIED HIERARCHY: All decomposition happens via .children
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for graph mapping")
    type: NodeType = NodeType.GENERIC
    
    # The Payload
    data: Optional[T] = None
    
    # User-facing/Runtime metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # The Agent's Internal Context
    meta: NodeMeta = Field(default_factory=NodeMeta)

    # RECURSIVE: The Tree structure (The ONLY hierarchy)
    children: Dict[str, Node] = Field(default_factory=dict)

    # GRAPH: Horizontal bindings
    relationships: List[RelationshipRef] = Field(default_factory=list)

    def update_data(self, new_data: T, confidence: float = 1.0, source: str = "inferred"):
        self.data = new_data
        self.meta.confidence = confidence
        self.meta.source = source
        self.meta.status = NodeStatus.EXTRACTED
        self.meta.last_updated = datetime.now()

    # --- Traversal API ---

    def add_child(self, child: Node) -> Node:
        """Adds a child node to the hierarchy."""
        self.children[child.id] = child
        return child

    def find_node(self, node_id: str) -> Optional[Node]:
        """Deep search for a node by ID."""
        if self.id == node_id:
            return self
        if node_id in self.children:
            return self.children[node_id]
        for child in self.children.values():
            found = child.find_node(node_id)
            if found:
                return found
        return None

    def walk(self) -> Generator[Node, None, None]:
        """Depth-first traversal generator."""
        yield self
        for child in self.children.values():
            yield from child.walk()

    class Config:
        arbitrary_types_allowed = True

Node.model_rebuild()
