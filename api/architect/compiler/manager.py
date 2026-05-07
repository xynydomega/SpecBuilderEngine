import copy
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from enum import Enum
from ..schemas.goal import Goal
from ..schemas.base import Node, NodeStatus, NodeType
from ..schemas.feature import Feature, FeatureData
from ..schemas.component import Component, ComponentData
from ..schemas.tool import Tool, ToolData
from ..schemas.relationship import Relationship, RelationshipData

class ExtractionStage(str, Enum):
    GOAL_DEFINITION = "goal_definition"
    FEATURE_DECOMPOSITION = "feature_decomposition"
    FEATURE_DEFINITION = "feature_definition"
    COMPONENT_DECOMPOSITION = "component_decomposition"
    COMPONENT_DEFINITION = "component_definition"
    TOOL_DEFINITION = "tool_definition"
    COMPLETE = "complete"

class SchemaManager:
    def __init__(self, initial_goal: Optional[Goal] = None):
        self.goal = initial_goal or Goal()

    def get_current_stage(self) -> Dict[str, Any]:
        """
        Determines the next required action based on the protocol.
        Protocol: Every node must have Intent, Constraints, State.
        Sequence: Goal -> Features -> Components -> Tools.
        """
        root = self.goal.config
        
        # 1. Check Goal Definition
        if not self._is_node_defined(root):
            return {"stage": ExtractionStage.GOAL_DEFINITION, "node_id": root.id, "type": root.type}

        # 2. Check Feature Decomposition
        features = [n for n in root.children.values() if n.type == NodeType.FEATURE]
        if not features:
            return {"stage": ExtractionStage.FEATURE_DECOMPOSITION, "parent_id": root.id}

        # 3. Check each Feature's Definition and its Components
        for feat in features:
            if not self._is_node_defined(feat):
                return {"stage": ExtractionStage.FEATURE_DEFINITION, "node_id": feat.id, "name": feat.data.name}
            
            components = [n for n in feat.children.values() if n.type == NodeType.COMPONENT]
            if not components:
                return {"stage": ExtractionStage.COMPONENT_DECOMPOSITION, "parent_id": feat.id, "name": feat.data.name}
            
            for comp in components:
                if not self._is_node_defined(comp):
                    return {"stage": ExtractionStage.COMPONENT_DEFINITION, "node_id": comp.id, "name": comp.data.name}
                
                # Check for Tools
                tools = [n for n in comp.children.values() if n.type == NodeType.TOOL]
                if not tools:
                    # Components might have sub-components or tools.
                    return {"stage": ExtractionStage.COMPONENT_DECOMPOSITION, "parent_id": comp.id, "name": comp.data.name}
                
                for tool in tools:
                    if not self._is_tool_defined(tool):
                        return {"stage": ExtractionStage.TOOL_DEFINITION, "node_id": tool.id, "name": tool.data.name}

        return {"stage": ExtractionStage.COMPLETE}

    def _is_node_defined(self, node: Node) -> bool:
        """Checks if a node has Intent (Target/Direction), Constraints, and State."""
        if not node.data:
            return False
        
        # Check Semantic Layer (Intent & Constraints)
        sl = getattr(node.data, "semantic_layer", None)
        if not sl:
            return False
        
        intent = sl.intent.data
        if not intent or not intent.target or not intent.direction:
            return False
            
        constraints = sl.constraints.data
        if not constraints:
            return False
            
        # Check State System
        ss = getattr(node.data, "state_system", None)
        if not ss or not ss.config.data or not ss.config.data.initial:
            return False
            
        return True

    def _is_tool_defined(self, tool: Node) -> bool:
        """Checks if a tool has Input, Processing, and Output."""
        data: ToolData = tool.data
        if not data: return False
        return bool(data.input and data.processing and data.output)

    def apply_patch(self, patch: Dict[str, Any]):
        """Recursively applies a JSON patch to the Goal tree."""
        self._merge_node(self.goal.config, patch.get("config", {}))

    def _merge_node(self, node: Node, patch: Dict[str, Any]):
        if not patch:
            return

        # 1. Update Metadata
        if "meta" in patch:
            for key, value in patch["meta"].items():
                if hasattr(node.meta, key):
                    setattr(node.meta, key, value)
            node.meta.last_updated = datetime.now()

        # 2. Update Data (Pydantic model merge)
        if "data" in patch:
            new_data = patch["data"]
            if hasattr(node.data, "model_dump"):
                # Merge current data with patch and re-validate
                updated_data_dict = node.data.model_dump()
                self._deep_update(updated_data_dict, new_data)
                node.data = node.data.__class__.model_validate(updated_data_dict)
            else:
                node.data = new_data

        # 3. Update Children Recursively
        if "children" in patch:
            for child_id, child_patch in patch["children"].items():
                if child_id in node.children:
                    self._merge_node(node.children[child_id], child_patch)
                else:
                    # Create new child node if type is provided
                    if "type" in child_patch:
                        new_node = self._create_node_by_type(child_patch["type"], child_patch.get("data", {}))
                        new_node.id = child_id # Sync ID with patch key
                        node.children[child_id] = new_node
                        self._merge_node(new_node, child_patch)

    def _deep_update(self, base_dict: Dict[str, Any], patch_dict: Dict[str, Any]):
        for key, value in patch_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _create_node_by_type(self, node_type: Union[str, NodeType], data: Dict[str, Any]) -> Node:
        # Convert string to NodeType enum if necessary
        if isinstance(node_type, str):
            node_type = NodeType(node_type)

        if node_type == NodeType.FEATURE:
            return Node(type=NodeType.FEATURE, data=FeatureData(**data))
        elif node_type == NodeType.COMPONENT:
            return Node(type=NodeType.COMPONENT, data=ComponentData(**data))
        elif node_type == NodeType.TOOL:
            return Node(type=NodeType.TOOL, data=ToolData(**data))
        elif node_type == NodeType.RELATIONSHIP:
            return Node(type=NodeType.RELATIONSHIP, data=RelationshipData(**data))
        else:
            return Node(type=node_type, data=data)

    def export_schema(self) -> Dict[str, Any]:
        """Returns a serializable dictionary of the entire goal tree."""
        return {"config": self._dump_node(self.goal.config)}

    def _dump_node(self, node: Node) -> Dict[str, Any]:
        res = node.model_dump(exclude={"children"})
        res["children"] = {k: self._dump_node(v) for k, v in node.children.items()}
        return res
