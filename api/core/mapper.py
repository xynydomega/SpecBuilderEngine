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

        schema_context = {k: {"target": v["target"], "state": v["state"]} for k, v in current_schema.items()}

        prompt = f"""
        You are a Mapper. Extract data into 'target' (purpose), 'state' (structure), and 'direction' (logic flow).
        
        User Input: "{user_input}"
        Schema Context: {json.dumps(schema_context)}
        
        Tasks:
        1. Check relevance. If user talks about unrelated topics (e.g. Rome, history, personal chatter), set "is_relevant" to false.
        2. If relevant, extract into the proper keys (goal, type, input, behavior, output, ui).
        3. Inside those keys, map data strictly to 'target', 'state', or 'direction'.
        4. Assign confidence (0.0 to 1.0).
        
        Return ONLY valid JSON:
        {{
            "is_relevant": true/false,
            "patch": {{
                "node_name": {{
                    "target": {{}},
                    "state": {{}},
                    "direction": {{}},
                    "confidence": 0.9
                }}
            }}
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            
            res = json.loads(chat_completion.choices[0].message.content)
            
            patch = res.get("patch", {})
            for key in patch:
                patch[key]["meta"] = {
                    "filled": True,
                    "confidence": patch[key].get("confidence", 0.7),
                    "source": "inferred",
                    "last_updated": datetime.utcnow().isoformat()
                }
                # Remove raw confidence key from patch payload
                patch[key].pop("confidence", None)
            
            return {
                "is_relevant": res.get("is_relevant", True),
                "patch": patch
            }
        except Exception as e:
            return {"error": str(e), "is_relevant": True, "patch": {}}

mapper_engine = MapperEngine()
