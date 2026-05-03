from flask import Flask, jsonify, request
from flask_cors import CORS
from .core.schema import schema_engine
from .core.mapper import mapper_engine

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "SpecBuilderEngine API is running"}), 200

@app.route('/api/schema', methods=['GET'])
def get_schema():
    return jsonify(schema_engine.get_schema()), 200

@app.route('/api/schema/validate', methods=['POST'])
def validate_schema():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    errors = {}
    for key, node in data.items():
        is_valid, message = schema_engine.validate_node(node)
        if not is_valid:
            errors[key] = message
            
    if errors:
        return jsonify({"valid": False, "errors": errors}), 400
    
    return jsonify({"valid": True}), 200

@app.route('/api/schema/reset', methods=['POST'])
def reset_schema():
    new_schema = schema_engine.reset_schema()
    return jsonify({"message": "Schema reset successful", "schema": new_schema}), 200

@app.route('/api/mapper/extract', methods=['POST'])
def mapper_extract():
    data = request.json
    user_input = data.get("input")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    current_schema = schema_engine.get_schema()
    patch = mapper_engine.extract_from_input(user_input, current_schema)
    
    if "error" in patch:
        return jsonify(patch), 500
        
    return jsonify({"patch": patch}), 200

@app.route('/api/mapper/apply', methods=['POST'])
def mapper_apply():
    data = request.json
    patch = data.get("patch")
    if not patch:
        return jsonify({"error": "No patch provided"}), 400
    
    updated_schema = schema_engine.apply_patch(patch)
    return jsonify({"message": "Patch applied successfully", "schema": updated_schema}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
