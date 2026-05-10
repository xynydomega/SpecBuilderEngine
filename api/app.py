from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import traceback
import uuid
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(base_dir, ".."))
env_local = os.path.join(root_dir, ".env.local")
env_standard = os.path.join(root_dir, ".env")

if os.path.exists(env_local):
    load_dotenv(env_local)
elif os.path.exists(env_standard):
    load_dotenv(env_standard)

from core.schema import schema_engine
from core.cognition_engine import cognition_engine
from core.cognition import RuntimeState, InterrogatorMessage, AssistantMessage
from core.truth_gate import truth_gate
from architect.registry.resolver import ProjectResolver

app = Flask(__name__)
CORS(app)

REGISTRY_PATH = os.path.join(base_dir, "architect", "registry", "mappings.json")
project_resolver = ProjectResolver(REGISTRY_PATH)

# Global Runtime State for SpecBuilderCognitionRuntime
RUNTIME_STATE = RuntimeState(conversation_id=str(uuid.uuid4()))

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/cognition/message', methods=['POST'])
def cognition_message():
    """Endpoint for the SpecBuilderCognitionRuntime Conversation Cycle."""
    try:
        data = request.json
        user_input = data.get("input")
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        
        # Process turn through the engine
        response = cognition_engine.process_turn(user_input, RUNTIME_STATE)
        
        return jsonify({
            "response": response.model_dump(),
            "state": RUNTIME_STATE.model_dump()
        }), 200
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": f"Cognition Error: {str(e)}"}), 500

@app.route('/api/cognition/confirm', methods=['POST'])
def cognition_confirm():
    """Commits structural hypotheses to the Confirmed Tree and Substrate."""
    try:
        data = request.json
        # In this runtime, we confirm specific hypotheses from the Shadow Tree
        hypothesis_id = data.get("hypothesis_id")
        
        # Mapping Shadow -> Confirmed logic would go here
        # For simplicity, we sync the current most-confident shadow state
        # In a real implementation, we'd use the confirmation_engine rules.
        
        # 1. Update Substrate
        # (This is still using the older generate_commit_patch for now, 
        # refactoring it to use the new ShadowTree model would be next)
        # patch = cognition_engine.generate_commit_patch(RUNTIME_STATE.shadow_tree.model_dump())
        # updated_schema = schema_engine.apply_patch(patch, mark_confirmed=True)
        
        # 2. Update Confirmed Tree in Runtime State
        # RUNTIME_STATE.confirmed_tree.features = ...
        
        return jsonify({
            "message": "Convergence step successful.",
            "state": RUNTIME_STATE.model_dump()
        }), 200
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": f"Confirm Error: {str(e)}"}), 500

@app.route('/api/agent/init', methods=['GET'])
def agent_init():
    return jsonify({"message": "SpecBuilderCognitionRuntime Initialized. Define your core intent."}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
