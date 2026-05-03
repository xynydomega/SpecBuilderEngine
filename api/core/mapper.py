import os
import json
from groq import Groq
from datetime import datetime

class MapperEngine:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None

    def extract_from_input(self, user_input, current_schema):
        if not self.client:
            return {"error": "GROQ_API_KEY not configured"}

        # Filter schema to relevant info for context to save tokens
        schema_context = {k: {"target": v["target"], "state": v["state"]} for k, v in current_schema.items()}

        prompt = f"""
        You are 'The Architect' Mapper Engine. 
        Your task is to translate user input into structured updates for a system schema based on 'Component = Unit of Meaning'.
        
        Current Schema Context: {json.dumps(schema_context)}
        
        User Input: "{user_input}"
        
        Extraction targets:
        - 'goal': The main outcome/vision.
        - 'type': Functional structure/modules.
        - 'input': Data requirements.
        - 'behavior': Execution flow/logic.
        - 'output': Expected results.
        - 'ui': Interface patterns.
        
        For each extraction:
        1. Define the 'goal' of the change (what is being added/updated).
        2. Define the 'direction' (how it evolves, e.g., "assign", "merge").
        3. Define the 'state' (the actual structured data).
        4. Assign 'confidence' (0.0 to 1.0).
        
        Return ONLY a JSON object mapping these keys to their new structures.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(chat_completion.choices[0].message.content)
            return self._build_patch(extracted_data)
        except Exception as e:
            return {"error": str(e)}

    def _build_patch(self, data):
        """Converts extracted data into a schema patch following the new contract."""
        patch = {}
        
        for key in ["goal", "type", "input", "output", "ui", "behavior"]:
            if key in data:
                node_data = data[key]
                patch[key] = {
                    "target": node_data.get("target") or node_data.get("goal_intent") or {},
                    "state": node_data.get("state") or {},
                    "direction": node_data.get("direction") or {},
                    "meta": {
                        "filled": True,
                        "confidence": node_data.get("confidence", 0.7),
                        "source": "inferred",
                        "last_updated": datetime.utcnow().isoformat()
                    }
                }
            
        return patch

mapper_engine = MapperEngine()
