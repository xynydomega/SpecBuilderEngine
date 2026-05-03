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
            "dependencies": [],
            "history": [],
            "last_updated": None
        }

        self.base_schema = {
            "goal": {
                "target": {}, "state": {}, "direction": {},
                "meta": self._create_meta(source="user")
            },
            "type": {
                "target": {}, "state": {}, "direction": {},
                "meta": self._create_meta(source="inferred", dependencies=["goal"])
            },
            "input": {
                "target": {}, "state": {}, "direction": {},
                "meta": self._create_meta(source="mixed", dependencies=["goal"])
            },
            "output": {
                "target": {}, "state": {}, "direction": {},
                "meta": self._create_meta(dependencies=["input"])
            },
            "ui": {
                "target": {}, "state": {}, "direction": {},
                "meta": self._create_meta(required=False, dependencies=["type"])
            },
            "behavior": {
                "target": {}, "state": {}, "direction": {},
                "meta": self._create_meta(filled=True, confidence=1.0, status="locked", confirmed=True)
            },
            "suggestions": {
                "target": {}, "state": {}, "direction": {},
                "meta": self._create_meta(required=False, source="inferred")
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

    def apply_patch(self, patch, mark_confirmed=False):
        """Merges a patch into the current schema with deep meta merging."""
        for key, new_data in patch.items():
            if key in self.current_schema:
                node = self.current_schema[key]
                
                # History tracking
                if node["meta"]["filled"]:
                    history_entry = {
                        "state": copy.deepcopy(node.get("state")),
                        "target": copy.deepcopy(node.get("target")),
                        "direction": copy.deepcopy(node.get("direction")),
                        "meta": {
                            "source": node["meta"]["source"],
                            "confidence": node["meta"]["confidence"],
                            "timestamp": node["meta"].get("last_updated")
                        }
                    }
                    node["meta"]["history"].append(history_entry)
                
                # Update data fields
                for field in ["target", "state", "direction"]:
                    if field in new_data:
                        node[field] = new_data[field]
                
                # Deep merge meta
                if "meta" in new_data:
                    for m_key, m_val in new_data["meta"].items():
                        if m_key != "history": # Preserve history
                            node["meta"][m_key] = m_val
                
                if mark_confirmed:
                    node["meta"]["confirmed"] = True
                    node["meta"]["status"] = "completed"
                
                node["meta"]["filled"] = True
                node["meta"]["last_updated"] = datetime.now().isoformat()
                
        return self.current_schema

schema_engine = SchemaEngine()
