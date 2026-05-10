import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Union
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from .cognition import (
    RuntimeState, ShadowGraph, ConfirmedTree, ShadowNode, ShadowEdge,
    InterrogatorMessage, AssistantMessage, GraphEvolutionUpdate, UncertaintyResolution,
    Alternative, MutationEvent, ConfidenceMetrics
)

class CognitionEngine:
    def __init__(self):
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "cloudshell-gca")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        vertexai.init(project=project_id, location=location)
        # We initialize without system_instruction here, and set it per call if needed
        # or use a default one.
        self.base_model = "gemini-1.5-pro"

    def process_turn(self, user_input: str, state: RuntimeState) -> Union[InterrogatorMessage, AssistantMessage]:
        """
        Implementation of the SpecBuilderCognitionRuntime v1.3.0 Convergence Cycle.
        """
        state.turn_index += 1
        
        # 1. INTENT PULSE & GRAPH EVOLUTION
        evolution_update = self._run_graph_evolution_engine(user_input, state)
        self._apply_graph_evolution(state.shadow_graph, evolution_update)
        
        # 2. RELATIONAL RESOLUTION (Contradiction pruning)
        self._resolve_contradictions(state)
        
        # 3. TOPOLOGY PROPAGATION (Confidence Flow)
        self._propagate_topology_state(state)
        
        # 4. STABILIZED PROJECTION (Harden nodes)
        self._project_stabilized_regions(state)
        
        # 5. UNCERTAINTY RESOLUTION
        resolution = self._run_uncertainty_resolution(state)
        state.dialogue_state["active_focus_node"] = resolution.next_focus_node
        
        # 6. ACTOR SELECTION
        # Global entropy check
        if state.shadow_graph.global_entropy > 0.8:
            return self._run_assistant(state, "System: Global entropy threshold exceeded. Topology requires stabilization.")
            
        if resolution.ambiguity_threshold_exceeded:
            return self._run_interrogator(state, user_input)
        else:
            return self._run_assistant(state, user_input)

    def _run_graph_evolution_engine(self, user_input: str, state: RuntimeState) -> GraphEvolutionUpdate:
        system_prompt = """
        You are THE GRAPH EVOLUTION ENGINE (v1.3.0).
        Focus on the RELATIONAL SUBSTRATE.
        
        TASKS:
        1. Node Creation/Mutation based on user Intent.
        2. EDGE EVOLUTION: Create explicit edges (dependency, execution, ownership, state_flow, causal).
        3. Assign Edge weights and confidence.
        
        Produce a JSON following GraphEvolutionUpdate schema.
        """
        user_prompt = f"Intent: {user_input}\nState: {state.shadow_graph.model_dump_json()}"
        res = self._call_gemini(system_prompt, user_prompt, is_json=True)
        return GraphEvolutionUpdate.model_validate(res)

    def _apply_graph_evolution(self, shadow_graph: ShadowGraph, update: GraphEvolutionUpdate):
        shadow_graph.nodes = update.nodes
        shadow_graph.edges = update.edges
        shadow_graph.active_frontier = update.active_frontier
        shadow_graph.global_entropy = update.global_entropy
        shadow_graph.convergence_score = update.convergence_score

    def _resolve_contradictions(self, state: RuntimeState):
        for node in state.shadow_graph.nodes:
            if node.confidence_metrics.contradiction_penalty > 0.8:
                node.status = "contradicted"
            if node.total_confidence < 0.1 and node.status not in ["confirmed", "stabilizing"]:
                node.status = "deprecated"

    def _propagate_topology_state(self, state: RuntimeState):
        """
        Calculates confidence and support based on relational substrate.
        Formula: Structural Support = Σ (ParentNode.Confidence * Edge.Weight * Edge.Confidence)
        """
        confirmed_ids = {n["id"] for n in state.confirmed_tree.nodes}
        
        for node in state.shadow_graph.nodes:
            m = node.confidence_metrics
            
            # Find edges where this node is the 'to_node'
            inbound_edges = [e for e in state.shadow_graph.edges if e.to_node == node.id]
            support_score = 0.0
            for edge in inbound_edges:
                # Source confidence: either from confirmed tree or from shadow node
                source_node = next((sn for sn in state.shadow_graph.nodes if sn.id == edge.from_node), None)
                source_conf = 1.0 if edge.from_node in confirmed_ids else (source_node.total_confidence if source_node else 0.0)
                
                support_score += source_conf * edge.weight * edge.confidence
            
            m.structural_support = min(1.0, support_score)
            
            # Aggregate Confidence (v1.3.0 Formula)
            node.total_confidence = (
                m.reinforcement * 0.2 +
                m.user_confirmation * 0.3 +
                m.structural_support * 0.5
            ) * (1.0 - m.contradiction_penalty)

    def _project_stabilized_regions(self, state: RuntimeState):
        for node in state.shadow_graph.nodes:
            if node.status == "stabilizing" and node.total_confidence > 0.9:
                node.status = "confirmed"
                if node.id not in [n.get("id") for n in state.confirmed_tree.nodes]:
                    state.confirmed_tree.nodes.append({"id": node.id, **node.hypothesis})
                    state.confirmed_tree.projection_timestamp = datetime.datetime.now().isoformat()

    def _run_uncertainty_resolution(self, state: RuntimeState) -> UncertaintyResolution:
        system_prompt = "UNCERTAINTY RESOLVER: Analyze node AND edge stability. Identify the next focus node."
        user_prompt = f"Shadow Graph: {state.shadow_graph.model_dump_json()}"
        res = self._call_gemini(system_prompt, user_prompt, is_json=True)
        return UncertaintyResolution.model_validate(res)

    def _run_interrogator(self, state: RuntimeState, user_input: str) -> InterrogatorMessage:
        system_prompt = "INTERROGATOR: Focus on resolving relational ambiguity. Ask targeted questions."
        focus = state.dialogue_state.get("active_focus_node", "root")
        user_prompt = f"Focus: {focus}\nGraph: {state.shadow_graph.model_dump_json()}"
        res = self._call_gemini(system_prompt, user_prompt, is_json=True)
        return InterrogatorMessage.model_validate(res)

    def _run_assistant(self, state: RuntimeState, user_input: str) -> AssistantMessage:
        system_prompt = "ASSISTANT: Explain the architectural topology and constraints. Provide alternatives."
        user_prompt = f"Graph: {state.shadow_graph.model_dump_json()}"
        res = self._call_gemini(system_prompt, user_prompt, is_json=True)
        return AssistantMessage.model_validate(res)

    def _call_gemini(self, system_prompt: str, user_prompt: str, is_json: bool = False) -> Dict[Any, Any]:
        config = GenerationConfig(response_mime_type="application/json") if is_json else None
        model = GenerativeModel(self.base_model, system_instruction=system_prompt)
        response = model.generate_content(user_prompt, generation_config=config)
        
        if is_json:
            try:
                # Clean up markdown code blocks if Gemini returns them
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text)
            except Exception as e:
                print(f"JSON Parsing Error: {e}")
                print(f"Raw Response: {response.text}")
                return {}
        return response.text

cognition_engine = CognitionEngine()
