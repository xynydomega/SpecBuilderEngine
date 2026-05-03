from flask import Flask, jsonify, request
from flask_cors import CORS
from .core.schema import schema_engine

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
    
    # For now, we validate if the top-level nodes are valid
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
