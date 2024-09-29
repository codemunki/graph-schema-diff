import os
from flask import Flask, request, jsonify
from graphql_comparator import GraphQLComparator  # Assuming this class is implemented as above
from flasgger import Swagger

app = Flask(__name__)

# Initialize Swagger for automatic API documentation
swagger = Swagger(app)

# Read model_file and expected_json_path
model_file = os.getenv("MODEL_FILE", "models/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf")
expected_json_path = os.getenv("EXPECTED_JSON_PATH", "data/expected.json")

# Initialize the comparator with the environment variables or defaults
comparator = GraphQLComparator(model_file=model_file, expected_json_path=expected_json_path)

@app.route('/compare', methods=['POST'])
def compare():
    """
    Compare two GraphQL schemas and return the comparison results.
    ---
    parameters:
      - in: body
        name: schemas
        description: Two GraphQL schemas to compare
        schema:
          type: object
          properties:
            schema1:
              type: string
              description: The first GraphQL schema
              example: "type Query { hello: String }"
            schema2:
              type: string
              description: The second GraphQL schema
              example: "type Query { hello: String, goodbye: String }"
    responses:
      200:
        description: Successful comparison
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            result:
              type: object
              description: The comparison results
      400:
        description: Failure due to missing schemas
        schema:
          type: object
          properties:
            status:
              type: string
              example: "failure"
            message:
              type: string
              example: "Both schemas must be provided"
    """
    data = request.get_json()
    schema1 = data.get('schema1')
    schema2 = data.get('schema2')
    if not schema1 or not schema2:
        return jsonify({"status": "failure", "message": "Both schemas must be provided"}), 400

    result = comparator.compare(schema1, schema2)
    return jsonify(result)

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get statistics of API calls, query times, and breaking change counts.
    ---
    responses:
      200:
        description: Statistics for the GraphQL Comparator
        schema:
          type: object
          properties:
            total_api_calls:
              type: integer
            breaking_change_count:
              type: integer
            average_query_time:
              type: number
            total_query_time:
              type: number
    """
    stats = comparator.statistics()
    return jsonify(stats)

@app.route('/model-info', methods=['GET'])
def get_model_info():
    """
    Get information about the loaded model (path, load time, size).
    ---
    responses:
      200:
        description: Information about the model
        schema:
          type: object
          properties:
            model_path:
              type: string
            model_load_time:
              type: number
            model_size:
              type: integer
    """
    model_info = comparator.model_info()
    return jsonify(model_info)

if __name__ == '__main__':
    app.run(debug=True)
