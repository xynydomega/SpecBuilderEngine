import copy
from datetime import datetime

class SchemaEngine:
    def __init__(self):
        self.default_meta = {
            "required": True,
            "filled": False,
            "confidence": 0.0,
            "confirmed": False,
            "status": "pending",
            "source": "none",
            "scope_locked": True,
            "scope": {
                "level": "MVP",
                "version": 1
            },
            "dependencies": [],
            "history": [],
            "last_updated": None
        }

        self.base_schema = {
            "goal": {
                "target": {
                    "role": "define main product idea",
                    "examples": ["math tutor", "fitness app", "login system"]
                },
                "state": {
                    "value": None,
                    "resolved": False
                },
                "meta": self._create_meta(source="user")
            },
            "type_hypothesis": {
                "target": {
                    "role": "decompose goal into functional modules"
                },
                "state": {
                    "components": [],
                    "scope": "MVP"
                },
                "meta": self._create_meta(source="inferred", dependencies=["goal"])
            },
            "inputs": {
                "target": {
                    "role": "collect required data"
                },
                "state": {
                    "fields": {}
                },
                "meta": self._create_meta(source="mixed", dependencies=["goal", "type_hypothesis"])
            },
            "outputs": {
                "target": {
                    "role": "system outputs per component"
                },
                "state": {
                    "results": {}
                },
                "meta": self._create_meta(dependencies=["inputs"])
            },
            "ui": {
                "target": {
                    "role": "render MVP interface only"
                },
                "state": {
                    "layout": "MVP"
                },
                "meta": self._create_meta(dependencies=["type_hypothesis"])
            },
            "behavior": {
                "target": {
                    "role": "control execution flow"
                },
                "state": {
                    "mode": "MVP_BUILD"
                },
                "meta": self._create_meta(filled=True, confidence=1.0, status="locked")
            },
            "suggestions": {
                "target": {
                    "role": "capture user requested modifications"
                },
                "state": {
                    "items": []
                },
                "meta": self._create_meta(required=False, source="user", scope_locked=False)
            }
        }
        self.current_schema = copy.deepcopy(self.base_schema)

    def _create_meta(self, **kwargs):
        meta = copy.deepcopy(self.default_meta)
        meta.update(kwargs)
        return meta

    def get_schema(self):
        return self.current_schema

    def reset_schema(self):
        self.current_schema = copy.deepcopy(self.base_schema)
        return self.current_schema

    def validate_node(self, node_data):
        """Ensures a node has the mandatory meta contract."""
        if not isinstance(node_data, dict) or "meta" not in node_data:
            return False, "Node must contain 'meta' object."
        
        required_meta_keys = set(self.default_meta.keys())
        provided_meta_keys = set(node_data["meta"].keys())
        
        missing_keys = required_meta_keys - provided_meta_keys
        if missing_keys:
            return False, f"Missing mandatory meta keys: {missing_keys}"
        
        return True, "Valid"

    def apply_patch(self, patch):
        """Merges a patch into the current schema with history tracking."""
        for key, new_node in patch.items():
            if key in self.current_schema:
                old_node = self.current_schema[key]
                # Push current state to history if it was filled
                if old_node["meta"]["filled"]:
                    history_entry = {
                        "state": copy.deepcopy(old_node["state"]),
                        "target": copy.deepcopy(old_node["target"]),
                        "meta": {
                            "source": old_node["meta"]["source"],
                            "confidence": old_node["meta"]["confidence"],
                            "timestamp": old_node["meta"].get("last_updated")
                        }
                    }
                    new_node["meta"]["history"] = old_node["meta"].get("history", []) + [history_entry]
                
                # Merge
                self.current_schema[key].update(new_node)
        return self.current_schema

schema_engine = SchemaEngine()
