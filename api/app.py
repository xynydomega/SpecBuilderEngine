from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import traceback
from .core.schema import schema_engine
from .core.mapper import mapper_engine
from .core.sequencer import sequencer_engine
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
    try:
        data = request.json
        user_input = data.get("input")
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        
        current_schema = schema_engine.get_schema()
        
        # 1. Extraction & Relevance
        mapper_result = mapper_engine.extract_from_input(user_input, current_schema)
        if "error" in mapper_result:
            return jsonify({"error": mapper_result["error"]}), 500
            
        patch = mapper_result.get("patch", {})
        is_irrelevant = not mapper_result.get("is_relevant", True)
        
        # 2. Sequence Determination
        next_step = sequencer_engine.get_next_step(current_schema)
        
        # 3. Response Generation
        response_text = agent_engine.generate_response(user_input, patch, next_step, is_irrelevant)
        
        return jsonify({
            "patch": patch,
            "message": response_text
        }), 200
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/agent/confirm', methods=['POST'])
def agent_confirm():
    try:
        data = request.json
        patch = data.get("patch")
        if not patch:
            return jsonify({"error": "No patch provided"}), 400
        
        # Apply patch and mark as confirmed
        updated_schema = schema_engine.apply_patch(patch, mark_confirmed=True)
        next_step = sequencer_engine.get_next_step(updated_schema)
        
        return jsonify({
            "message": "Step confirmed.", 
            "schema": updated_schema,
            "next_step_prompt": next_step["prompt"]
        }), 200
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
