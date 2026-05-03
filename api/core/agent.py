import os
import json
from groq import Groq

class AgentEngine:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None

    def get_initial_greeting(self):
        return "System active. Define the core purpose of the main objective."

    def generate_response(self, user_input, patch, next_step, is_irrelevant=False):
        """Generates a strict, masked interrogation response under 30 words."""
        if is_irrelevant:
            return "I do not see how this relates to a goal. Stay on task."

        if not self.client:
            return next_step['prompt']

        prompt = f"""
        You are an Interrogator gathering system specs.
        
        User Input: "{user_input}"
        Extraction: {json.dumps(patch)}
        Next Question to ask: "{next_step['prompt']}"
        
        RULES:
        1. MAX 30 WORDS.
        2. NO conversation, NO philosophy, NO greetings.
        3. Read back what was just defined.
        4. Ask the Next Question exactly or closely.
        
        Response Format Example:
        "Extracted [X]. Now, [Next Question]"
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=50
            )
            return chat_completion.choices[0].message.content.strip()
        except:
            return next_step['prompt']

agent_engine = AgentEngine()
