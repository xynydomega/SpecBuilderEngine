from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import traceback
from .core.schema import schema_engine
from .core.agent import agent_engine

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/agent/init', methods=['GET'])
def agent_init():
    try:
        greeting = agent_engine.get_initial_greeting()
        return jsonify({"message": greeting}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/message', methods=['POST'])
def agent_message():
    """Endpoint for the Interrogator-Architect."""
    try:
        data = request.json
        user_input = data.get("input")
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        
        current_schema = schema_engine.get_schema()
        next_stage = schema_engine.get_current_stage()
        
        # 1. Extraction (Interrogator 'Draws' the patch)
        patch = agent_engine.extract_patch(user_input, current_schema, next_stage)
        
        # 2. Interrogation Response
        response_text = agent_engine.generate_interrogation(user_input, current_schema, next_stage)
        
        return jsonify({
            "patch": patch,
            "message": response_text,
            "stage": next_stage["stage"]
        }), 200
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/agent/assistant', methods=['POST'])
def agent_assistant():
    """Endpoint for the Executive Assistant floating box."""
    try:
        data = request.json
        user_input = data.get("input") # Can be empty if just asking for help
        
        current_schema = schema_engine.get_schema()
        next_stage = schema_engine.get_current_stage()
        
        suggestion = agent_engine.generate_assistant_suggestion(user_input, current_schema, next_stage)
        
        return jsonify({
            "message": suggestion,
            "stage": next_stage["stage"]
        }), 200
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/confirm', methods=['POST'])
def agent_confirm():
    try:
        data = request.json
        patch = data.get("patch")
        if not patch:
            return jsonify({"error": "No patch provided"}), 400
        
        # Apply patch to the Pydantic-based manager
        updated_schema = schema_engine.apply_patch(patch, mark_confirmed=True)
        next_stage = schema_engine.get_current_stage()
        
        return jsonify({
            "message": "Protocol step confirmed.", 
            "schema": updated_schema,
            "next_stage": next_stage
        }), 200
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
