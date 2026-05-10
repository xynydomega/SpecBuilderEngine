from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .cognition import ShadowGraph

class ValidationError(BaseModel):
    type: str
    message: str
    rationale: str

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationError] = Field(default_factory=list)

class TruthGate:
    """
    The Enforcement Layer (v1.3.0): Validates Shadow Graphs 
    against Axiomatic Kernel laws.
    """

    def validate_graph(self, graph: ShadowGraph) -> ValidationResult:
        errors = []
        
        # 1. Identity Law: Every system must have a core identity/goal
        has_goal = any(n.type.upper() == "GOAL" for n in graph.nodes)
        if not has_goal:
            errors.append(ValidationError(
                type="identity_void",
                message="Goal node is missing.",
                rationale="Every system must have a clear identity (GOAL node) to exist in the substrate."
            ))

        # 2. Ontological Law: Edge connects valid nodes
        node_ids = {n.id for n in graph.nodes}
        for edge in graph.edges:
            if edge.from_node not in node_ids:
                errors.append(ValidationError(
                    type="ontological_drift",
                    message=f"Edge source '{edge.from_node}' does not exist.",
                    rationale="Edges cannot originate from non-existent nodes."
                ))
            if edge.to_node not in node_ids:
                errors.append(ValidationError(
                    type="ontological_drift",
                    message=f"Edge target '{edge.to_node}' does not exist.",
                    rationale="Edges cannot point to non-existent nodes."
                ))

        # 3. Determinism Law: State flow integrity
        for node in graph.nodes:
            if not node.hypothesis:
                 errors.append(ValidationError(
                    type="deterministic_void",
                    message=f"Node '{node.id}' has no hypothesis.",
                    rationale="A node without a hypothesis is non-deterministic."
                ))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )

truth_gate = TruthGate()
