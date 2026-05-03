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

        prompt = f"""
        You are 'The Architect' Mapper Engine. 
        Your task is to translate user input into structured updates for a system schema.
        
        Current Schema Context: {json.dumps(current_schema)}
        
        User Input: "{user_input}"
        
        Instructions:
        1. Extract the primary 'goal' (what they want to build).
        2. Decompose the goal into 'functional modules' for the 'type_hypothesis'.
        3. Identify specific 'inputs' (data fields) required.
        4. For each extraction, provide a 'reason' (target.role).
        5. Assign a 'confidence' score (0.0 to 1.0).
        
        Return ONLY a JSON object in this exact format:
        {{
            "goal": {{
                "value": "string",
                "reason": "string",
                "confidence": 0.9
            }},
            "type_hypothesis": [
                {{ "name": "string", "reason": "string", "confidence": 0.8 }}
            ],
            "inputs": [
                {{ "field": "string", "reason": "string", "confidence": 0.7 }}
            ]
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(chat_completion.choices[0].message.content)
            return self._build_patch(extracted_data)
        except Exception as e:
            return {"error": str(e)}

    def _build_patch(self, data):
        """Converts extracted data into a schema patch."""
        patch = {}
        
        if "goal" in data and data["goal"].get("value"):
            patch["goal"] = {
                "state": {"value": data["goal"]["value"], "resolved": True},
                "target": {"role": data["goal"]["reason"]},
                "meta": {
                    "filled": True,
                    "confidence": data["goal"]["confidence"],
                    "source": "inferred",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
            
        if "type_hypothesis" in data and data["type_hypothesis"]:
            patch["type_hypothesis"] = {
                "state": {"components": data["type_hypothesis"]},
                "target": {"role": "decompose goal into functional modules"},
                "meta": {
                    "filled": True,
                    "confidence": sum(c.get("confidence", 0) for c in data["type_hypothesis"]) / len(data["type_hypothesis"]) if data["type_hypothesis"] else 0,
                    "source": "inferred",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
            
        if "inputs" in data and data["inputs"]:
            patch["inputs"] = {
                "state": {"fields": {i["field"]: {"reason": i["reason"]} for i in data["inputs"] if "field" in i}},
                "target": {"role": "collect required data"},
                "meta": {
                    "filled": True,
                    "confidence": sum(c.get("confidence", 0) for c in data["inputs"]) / len(data["inputs"]) if data["inputs"] else 0,
                    "source": "inferred",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
            
        return patch

mapper_engine = MapperEngine()
