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
                "target": {
                    "role": "define system outcome",
                    "success_criteria": []
                },
                "state": {
                    "value": None,
                    "resolved": False
                },
                "meta": self._create_meta(source="user"),
                "direction": {
                    "on_update": [
                        { "type": "assign", "target": "goal.state.value", "from": "user.input" },
                        { "type": "validate", "target": "goal.state.value" },
                        { "type": "set", "target": "goal.meta.filled", "value": True },
                        { "type": "set", "target": "goal.meta.source", "value": "user" }
                    ],
                    "on_resolve": [
                        { "type": "branch", "condition": "valid", "next": "goal.state.resolved.true" },
                        { "type": "branch", "condition": "invalid", "next": "agent.ask_goal" }
                    ]
                }
            },
            "type": {
                "target": {
                    "role": "predict structure or intent"
                },
                "state": {
                    "candidates": [],
                    "selected": None,
                    "confidence": 0.0
                },
                "meta": self._create_meta(source="inferred", dependencies=["goal"]),
                "direction": {
                    "on_infer": [
                        { "type": "extract", "target": "user.input" },
                        { "type": "generate", "target": "candidates" },
                        { "type": "score", "target": "confidence" },
                        { "type": "set", "target": "meta.filled", "value": True }
                    ],
                    "on_validate": [
                        { "type": "branch", "condition": "confidence >= 0.6", "next": "select_candidate" },
                        { "type": "branch", "condition": "confidence < 0.6", "next": "agent.ask_type" }
                    ]
                }
            },
            "input": {
                "target": {
                    "role": "collect required data"
                },
                "state": {
                    "fields": {},
                    "valid": False
                },
                "meta": self._create_meta(source="mixed", dependencies=["goal"]),
                "direction": {
                    "on_input": [
                        { "type": "merge", "target": "input.state.fields", "from": "user.input" },
                        { "type": "validate", "target": "input.state.fields" },
                        { "type": "set", "target": "input.meta.filled", "value": True }
                    ]
                },
                "components": {}
            },
            "output": {
                "target": {
                    "role": "system outputs per component"
                },
                "state": {
                    "results": {},
                    "valid": False
                },
                "meta": self._create_meta(dependencies=["input"]),
                "direction": {
                    "on_output": [
                        { "type": "generate", "target": "results", "from": "input" }
                    ]
                }
            },
            "ui": {
                "target": {
                    "role": "render interface"
                },
                "state": {
                    "layout": None
                },
                "meta": self._create_meta(required=False, dependencies=["type"]),
                "direction": {
                    "on_render": [
                        { "type": "build", "target": "layout", "from": "components" }
                    ]
                }
            },
            "behavior": {
                "target": {
                    "role": "orchestrate execution"
                },
                "state": {
                    "current_step": None
                },
                "meta": self._create_meta(filled=True, confidence=1.0, status="locked", confirmed=True),
                "direction": {
                    "flow": [
                        { "type": "call", "target": "mapper.on_input" },
                        { "type": "call", "target": "sequencer.on_step" },
                        { "type": "call", "target": "agent.loop" }
                    ]
                }
            },
            "suggestions": {
                "target": {
                    "role": "assist missing components with safe patterns"
                },
                "state": {
                    "items": []
                },
                "meta": self._create_meta(required=False, source="inferred"),
                "direction": {
                    "on_generate": [
                        {
                            "type": "suggest",
                            "items": [
                                {
                                    "component": "password",
                                    "reason": "standard authentication pattern",
                                    "confidence": 0.7
                                }
                            ]
                        }
                    ]
                }
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
                    if "history" not in new_node["meta"]:
                         new_node["meta"]["history"] = []
                    new_node["meta"]["history"] = old_node["meta"].get("history", []) + [history_entry]
                
                new_node["meta"]["last_updated"] = datetime.now().isoformat()
                self.current_schema[key].update(new_node)
        return self.current_schema

schema_engine = SchemaEngine()
