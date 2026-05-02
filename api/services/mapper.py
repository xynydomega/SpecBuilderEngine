import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel
try:
    from ..models.spec import ArchitectSpec
except ImportError:
    from api.models.spec import ArchitectSpec

def map_intent(user_text: str, current_field: str, goal: str) -> dict:
    """
    Uses Gemini to map user natural language into a structured JSON patch.
    """
    # Initialize Vertex AI with project from environment or default
    project = os.environ.get("GCP_PROJECT_ID")
    location = os.environ.get("GCP_LOCATION", "us-central1")
    vertexai.init(project=project, location=location)
    model = GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are the Semantic Mapper for the Architect engine. 
    Your job is to extract data for the field '{current_field}' from the user's text.
    The overall goal is: '{goal}'.

    User Input: "{user_text}"

    Rules:
    1. If the field is 'goal', extract the primary objective.
    2. If the field is 'type', 'inputs', 'ui', 'outputs', 'state', 'actions', 'validation', or 'api', return a JSON list of strings.
    3. If the field is 'responses', return a JSON object with 'success' and 'failure' keys.
    4. ONLY return valid JSON. Do not include markdown or explanations.
    5. If no relevant data is found, return an empty list or object.

    Output Example for 'inputs': ["email", "password"]
    Output Example for 'responses': {{"success": "redirect to home", "failure": "show error toast"}}
    """

    response = model.generate_content(prompt)
    
    try:
        # Clean potential markdown if the model included it
        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return [] if current_field != 'responses' else {}
