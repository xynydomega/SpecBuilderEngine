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
        return "System vision initializing. Define the core intent (target and direction) of your goal."

    def generate_interrogation(self, user_input, current_schema, next_stage):
        """
        The Interrogator: Strict, polite, non-explanatory.
        Focuses on extracting logic and drawing the tree.
        """
        if not self.client:
            return f"Stage: {next_stage['stage']}. Please provide details for {next_stage.get('node_id') or 'next step'}."

        prompt = f"""
        You are THE INTERROGATOR. You are an autonomous architect.
        Your goal is to extract the system vision into a Pydantic-ready tree.
        
        Current Schema: {json.dumps(current_schema)}
        Current Protocol Stage: {next_stage['stage']}
        Node in focus: {next_stage.get('node_id') or next_stage.get('parent_id')}
        
        USER INPUT: "{user_input}"
        
        RULES:
        1. BE POLITE but STRICT.
        2. NO EXPLANATIONS. Do not tell the user WHY you need this.
        3. NO GREETINGS. NO CHITCHAT.
        4. Focus on the missing protocol requirements: Intent (Target/Direction), Constraints, or State.
        5. Read back the core of what was just extracted, then ask for the next part of the tree.
        6. Keep response under 40 words.
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": "You are a detail-strict system architect."},
                          {"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=100
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Interrogation error: {str(e)}"

    def generate_assistant_suggestion(self, user_input, current_schema, next_stage):
        """
        The Executive Assistant: Helpful, uses analogies, explains why.
        Provides a 'suggested version' of the idea.
        """
        if not self.client:
            return "I am here to help you build your idea. What can I clarify?"

        prompt = f"""
        You are THE EXECUTIVE ASSISTANT. You are a supportive guardian angel.
        You help the user navigate the Interrogator's strict demands.
        
        Current Schema: {json.dumps(current_schema)}
        Current Protocol Stage: {next_stage['stage']}
        
        USER INPUT: "{user_input}"
        
        TASKS:
        1. Explain WHY the Interrogator is asking for these specific details.
        2. Provide an ANALOGY or EXAMPLE to help the user provide good data.
        3. Build a "Suggested Version" of the next part of the idea.
        4. GUARDRAIL: Only talk about the task at hand. If the user is unrelated, decline politely.
        
        Response Format:
        Rationale: [Why it matters]
        Suggestion: [An example of what they could say]
        Analogy: [A helpful comparison]
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": "You are a helpful, proactive executive assistant."},
                          {"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=250
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Assistant error: {str(e)}"

    def extract_patch(self, user_input, current_schema, next_stage):
        """
        The Interrogator 'Draws' the tree by generating a JSON patch.
        """
        if not self.client:
            return {}

        prompt = f"""
        You are THE INTERROGATOR. Extract the user input into a JSON patch for the SchemaManager.
        The patch must follow this structure:
        {{
            "config": {{
                "data": {{ ... }},
                "children": {{
                    "child_id": {{ "type": "feature/component/tool", "data": {{ ... }} }}
                }}
            }}
        }}
        
        Current Stage: {next_stage['stage']}
        User Input: "{user_input}"
        
        Mandatory Fields for Nodes:
        - data.semantic_layer.intent (target, direction)
        - data.semantic_layer.constraints (global_rules, inheritance_rules)
        - data.state_system.config.data.initial
        
        If it's a Tool:
        - data.input, data.processing, data.output
        
        Return ONLY valid JSON.
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            res = json.loads(chat_completion.choices[0].message.content)
            return res
        except:
            return {}

agent_engine = AgentEngine()
