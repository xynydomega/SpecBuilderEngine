from flask import Flask, jsonify, request
from flask_cors import CORS
from .core.schema import schema_engine
from .core.mapper import mapper_engine
from .core.sequencer import sequencer_engine
from .core.agent import agent_engine

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "SpecBuilderEngine API is running"}), 200

@app.route('/api/schema', methods=['GET'])
def get_schema():
    return jsonify(schema_engine.get_schema()), 200

@app.route('/api/schema/reset', methods=['POST'])
def reset_schema():
    new_schema = schema_engine.reset_schema()
    return jsonify({"message": "Schema reset successful", "schema": new_schema}), 200

@app.route('/api/agent/init', methods=['GET'])
def agent_init():
    greeting = agent_engine.get_initial_greeting()
    return jsonify({"message": greeting}), 200

@app.route('/api/agent/message', methods=['POST'])
def agent_message():
    data = request.json
    user_input = data.get("input")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    current_schema = schema_engine.get_schema()
    patch = mapper_engine.extract_from_input(user_input, current_schema)
    
    if "error" in patch:
        return jsonify(patch), 500
        
    # Get next step for the agent response context
    next_step = sequencer_engine.get_next_step(current_schema)
    response_text = agent_engine.generate_response(user_input, patch, next_step)
    
    return jsonify({
        "patch": patch,
        "message": response_text
    }), 200

@app.route('/api/agent/confirm', methods=['POST'])
def agent_confirm():
    data = request.json
    patch = data.get("patch")
    if not patch:
        return jsonify({"error": "No patch provided"}), 400
    
    updated_schema = schema_engine.apply_patch(patch)
    next_step = sequencer_engine.get_next_step(updated_schema)
    
    return jsonify({
        "message": "Patch applied successfully", 
        "schema": updated_schema,
        "next_step_prompt": next_step["prompt"]
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
