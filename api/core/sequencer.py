class SequencerEngine:
    def __init__(self):
        self.priority_order = ["goal", "type_hypothesis", "inputs", "ui", "outputs"]
        self.prompts = {
            "goal": {
                "ask": "What is the primary vision for the system you want to build?",
                "refine": "I have a goal, but I need more clarity on the core purpose. Can you expand on it?",
                "confirm": "Does this summary accurately capture your goal?"
            },
            "type_hypothesis": {
                "ask": "Based on your goal, what are the main functional modules or features we need?",
                "refine": "I've drafted some modules, but they seem incomplete. What other core features should we include?",
                "confirm": "Are these the correct functional modules for your MVP?"
            },
            "inputs": {
                "ask": "What specific data or inputs will these components need to function?",
                "refine": "We need to clarify the data requirements for some components. Can you provide more details?",
                "confirm": "Do these input fields cover everything the system needs to collect?"
            },
            "ui": {
                "ask": "How should the interface look and feel for this MVP?",
                "refine": "Let's refine the layout and user interaction patterns.",
                "confirm": "Is this MVP layout alignment correct?"
            },
            "outputs": {
                "ask": "What are the expected results or outputs the system should produce?",
                "refine": "We need to clarify the final system results.",
                "confirm": "Are these the correct outputs for your system?"
            }
        }

    def get_next_step(self, schema):
        """
        Logic: dependencies > confidence > priority
        Ensures MVP First constraint.
        """
        candidates = []

        # 1. Scan and filter
        for key in self.priority_order:
            node = schema.get(key)
            if not node:
                continue

            meta = node["meta"]
            
            # Skip if locked/completed
            if meta["status"] in ["locked", "completed"]:
                continue

            # Check Dependencies
            dependencies_met = True
            for dep in meta.get("dependencies", []):
                dep_node = schema.get(dep)
                if not dep_node or not dep_node["meta"]["filled"] or not dep_node["meta"]["confirmed"]:
                    dependencies_met = False
                    break
            
            if not dependencies_met:
                continue

            # Determine if node needs attention
            needs_attention = False
            action = "ask"
            
            if not meta["filled"]:
                needs_attention = True
                action = "ask"
            elif meta["confidence"] < 0.6:
                needs_attention = True
                action = "refine"
            elif not meta["confirmed"]:
                needs_attention = True
                action = "confirm"

            if needs_attention:
                # Calculate Score
                # weight = (dependency_count * 10) + (1.0 - confidence) + (priority_index_inverse)
                dep_weight = self._get_dependency_weight(key, schema)
                conf_gap = 1.0 - meta["confidence"]
                priority_score = len(self.priority_order) - self.priority_order.index(key)
                
                score = (dep_weight * 10) + conf_gap + priority_score
                
                candidates.append({
                    "node": key,
                    "action": action,
                    "score": score,
                    "prompt": self.prompts.get(key, {}).get(action, "What is the next step?")
                })

        # Sort by score descending
        if not candidates:
            return {
                "node": "complete",
                "action": "lock",
                "prompt": "The blueprint is complete and the MVP is locked.",
                "score": 0
            }

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[0]

    def _get_dependency_weight(self, key, schema):
        """Counts how many other nodes depend on this key."""
        count = 0
        for node in schema.values():
            if key in node["meta"].get("dependencies", []):
                count += 1
        return count

sequencer_engine = SequencerEngine()
