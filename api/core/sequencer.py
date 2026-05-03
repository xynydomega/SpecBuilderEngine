class SequencerEngine:
    def __init__(self):
        self.priority_order = ["goal", "type", "input", "behavior", "output", "ui"]
        self.sub_priority = ["target", "state", "direction"]
        
        # Masking internal nodes for the prompt
        self.node_masks = {
            "goal": "main objective",
            "type": "functional modules",
            "input": "data requirements",
            "behavior": "system flow",
            "output": "expected results",
            "ui": "user interface"
        }
        
        # Masking internal sub-steps
        self.sub_masks = {
            "target": "core purpose",
            "state": "data structure",
            "direction": "execution rules"
        }

    def get_next_step(self, schema):
        """Finds the first node and sub-field needing attention."""
        for node_key in self.priority_order:
            node = schema.get(node_key)
            if not node: continue
            
            meta = node["meta"]
            if meta["confirmed"]:
                continue

            # Target -> State -> Direction
            for sub_key in self.sub_priority:
                val = node.get(sub_key)
                is_empty = not val or (isinstance(val, dict) and not any(val.values()))
                
                if is_empty or meta["confidence"] < 0.6:
                    return {
                        "node": node_key,
                        "sub_step": sub_key,
                        "action": "ask",
                        "prompt": f"Define the {self.sub_masks[sub_key]} for the {self.node_masks[node_key]}."
                    }

            # If all sub-steps filled but not confirmed
            return {
                "node": node_key,
                "sub_step": "confirmation",
                "action": "confirm",
                "prompt": f"Confirm the details for the {self.node_masks[node_key]}."
            }

        return {
            "node": "complete",
            "sub_step": "none",
            "action": "lock",
            "prompt": "System design finalized."
        }

sequencer_engine = SequencerEngine()
