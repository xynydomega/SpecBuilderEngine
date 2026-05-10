from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field

# --- V1.3 CONVERGENCE MODELS (RELATIONAL SUBSTRATE) ---

class MutationEvent(BaseModel):
    turn_index: int
    actor: str
    change_type: str  # "creation", "mutation", "merge", "split"
    rationale: str

class ConfidenceMetrics(BaseModel):
    recency: float = 1.0
    reinforcement: float = 0.0
    contradiction_penalty: float = 0.0
    structural_support: float = 0.0
    user_confirmation: float = 0.0

class ShadowNode(BaseModel):
    id: str
    type: str
    hypothesis: Dict[str, Any]
    confidence_metrics: ConfidenceMetrics = Field(default_factory=ConfidenceMetrics)
    total_confidence: float = 0.0
    status: Literal["speculative", "stabilizing", "confirmed", "contradicted", "deprecated"]
    mutation_history: List[MutationEvent] = Field(default_factory=list)
    # Pragmatic helper fields for fast traversal
    parent_nodes: List[str] = Field(default_factory=list)
    child_nodes: List[str] = Field(default_factory=list)
    ambiguity_score: float = 1.0

class ShadowEdge(BaseModel):
    id: str
    from_node: str
    to_node: str
    type: Literal["dependency", "execution", "ownership", "state_flow", "causal"]
    confidence: float = 0.0
    weight: float = 1.0
    is_directed: bool = True
    constraints: List[str] = Field(default_factory=list)
    inferred_by: str

class ShadowGraph(BaseModel):
    nodes: List[ShadowNode] = Field(default_factory=list)
    edges: List[ShadowEdge] = Field(default_factory=list)
    active_frontier: List[str] = Field(default_factory=list)
    global_entropy: float = 1.0
    convergence_score: float = 0.0

class ConfirmedTree(BaseModel):
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    projection_timestamp: Optional[str] = None

class RuntimeState(BaseModel):
    conversation_id: str
    turn_index: int = 0
    shadow_graph: ShadowGraph = Field(default_factory=ShadowGraph)
    confirmed_tree: ConfirmedTree = Field(default_factory=ConfirmedTree)
    dialogue_state: Dict[str, Any] = Field(default_factory=dict)

# --- MESSAGE PROTOCOL ---

class InterrogatorMessage(BaseModel):
    type: Literal["INTERROGATOR_MESSAGE"] = "INTERROGATOR_MESSAGE"
    focus_node: str
    question: str
    optional_suggestion: Optional[str] = None
    expected_resolution: str

class Alternative(BaseModel):
    option: str
    impact: str

class AssistantMessage(BaseModel):
    type: Literal["ASSISTANT_MESSAGE"] = "ASSISTANT_MESSAGE"
    concept: str
    explanation: str
    alternatives: List[Alternative] = Field(default_factory=list)

# --- ENGINE OUTPUTS ---

class GraphEvolutionUpdate(BaseModel):
    nodes: List[ShadowNode]
    edges: List[ShadowEdge]
    active_frontier: List[str]
    unresolved_regions: List[str]
    global_entropy: float
    convergence_score: float

class UncertaintyResolution(BaseModel):
    next_focus_node: str
    ambiguity_threshold_exceeded: bool
    rationale: str
