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
        """Generates an inspiring philosophical quote about structured building."""
        if not self.client:
            return "Architecture begins where engineering ends. Describe your vision, and we shall build its blueprint."

        prompt = "Generate a short, inspiring, and philosophical quote about the beauty of structured building, architecture, or turning ideas into blueprints. Keep it under 30 words."
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content.strip().replace('"', '')
        except:
            return "Structure is the skeleton of vision. Let us define the bones of your idea."

    def generate_response(self, user_input, patch, next_step):
        """Generates a conversational response based on the extraction and next step."""
        if not self.client:
            return f"I've analyzed your input. Based on our blueprint, the next logical step is to look at the {next_step['node']}."

        prompt = f"""
        You are 'The Architect', a philosophical and expert system designer. 
        The user just said: "{user_input}"
        
        Our Mapper extracted these potential updates (patch): {json.dumps(patch)}
        The Sequencer says the next target node is: "{next_step['node']}" (Action: {next_step['action']})
        
        Instructions:
        1. Respond to the user's input naturally. 
        2. Briefly acknowledge what was understood (the goal or components) without being mechanical.
        3. Transition smoothly to the next step suggested by the sequencer.
        4. Keep the tone collaborative, professional, and slightly philosophical.
        5. DO NOT mention internal terms like 'patch', 'node', or 'sequencer'.
        
        Response:
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"I understand your vision for {next_step['node']}. Let's continue by defining it further."

agent_engine = AgentEngine()
