import json
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ProjectManifest(BaseModel):
    files: List[Dict[str, Any]] = []
    dependencies: List[str] = []
    env_vars: Dict[str, str] = {}

class ProjectResolver:
    """
    The Compiler Frontend: Resolves a semantic graph into a 
    deterministic Project Manifest using the Mapping Registry.
    """

    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.mappings = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.registry_path):
            return {}
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
            return {m["id"]: m for m in data.get("mappings", [])}

    def resolve_graph(self, committed_graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Walks the committed graph and resolves its implementation requirements.
        """
        manifest = {
            "files": [],
            "dependencies": set(),
            "env_vars": {}
        }
        
        # Start resolving from the root (Goal)
        root = committed_graph.get("config", {})
        self._resolve_node(root, manifest)
        
        # Convert set to list for JSON serialization
        manifest["dependencies"] = list(manifest["dependencies"])
        return manifest

    def _resolve_node(self, node: Dict[str, Any], manifest: Dict[str, Any]):
        node_id = node.get("id")
        node_type = node.get("type")
        data = node.get("data", {})
        name = data.get("name", "").lower().replace(" ", "_")
        
        # Attempt to find a mapping by name or type-derived ID
        mapping = self.mappings.get(name) or self.mappings.get(node_id)
        
        if mapping:
            manifest["files"].append({
                "template": mapping["template_path"],
                "target_path": f"src/{mapping['type'].lower()}s/{name}.tsx",
                "bindings": self._resolve_bindings(mapping.get("bindings", {}), data)
            })
            for dep in mapping.get("dependencies", []):
                manifest["dependencies"].add(dep)
        
        # Recurse children
        children = node.get("children", {})
        for child in children.values():
            self._resolve_node(child, manifest)

    def _resolve_bindings(self, binding_map: Dict[str, str], node_data: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        for semantic_key, template_key in binding_map.items():
            if semantic_key in node_data:
                resolved[template_key] = node_data[semantic_key]
            elif semantic_key == "target":
                sl = node_data.get("semantic_layer", {})
                intent = sl.get("intent", {}).get("data", {})
                resolved[template_key] = intent.get("target", "")
        return resolved
