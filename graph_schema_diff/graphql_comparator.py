import json as js
import os
import re
import sys
import time
import logging
from guidance import models, gen, json as guidance_json

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class GraphQLComparator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton implementation to ensure only one instance of the class is created."""
        if cls._instance is None:
            cls._instance = super(GraphQLComparator, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_file, expected_json_path):
        if not hasattr(self, 'initialized'):  # Avoid re-initialization in singleton
            # Initialize model parameters
            self.model_file = model_file
            self.expected_obj = self._load_expected_json(expected_json_path)

            # Statistics tracking
            self.query_times = []
            self.api_calls = 0
            self.breaking_change_count = 0

            # Load model and track load time
            start_time = time.time()
            self.model = models.LlamaCpp(self.model_file)
            self.model_load_time = time.time() - start_time

            # Get the size of the model file
            self.model_size = self._get_model_size()

            self.initialized = True

    def _load_expected_json(self, expected_json_path):
        """
        Load the expected JSON schema from the provided file path.
        """
        with open(expected_json_path, 'r') as file:
            return js.load(file)

    def _get_model_size(self):
        """
        Get the size of the model file in bytes.
        """
        try:
            return os.path.getsize(self.model_file)
        except OSError as e:
            logger.error(f"Error getting model size: {e}")
            return 0

    def model_info(self):
        """
        Return information about the model such as path, load time, and size.
        """
        return {
            "model_path": self.model_file,
            "model_load_time": self.model_load_time,
            "model_size": self.model_size
        }

    def strip_html_tags(self, text):
        """
        Remove custom HTML-like tags from the text.
        """
        return re.sub(r"<\|\|_html.*?\|\|>", "", text)

    def read_file(self, file_path):
        """
        Utility function to read a file's content and return it as a string.
        """
        with open(file_path, 'r') as file:
            return file.read()

    def compare(self, schema1: str, schema2: str):
        """
        Compare two GraphQL schemas provided as strings and return the model's evaluation.
        Track the number of breaking changes detected.

        Args:
            schema1 (str): The first GraphQL schema as a string.
            schema2 (str): The second GraphQL schema as a string.

        Returns:
            A dictionary with:
            - status: "success" or "failure"
            - result: the generated JSON object (empty if failure)
        """
        logger.info("Comparing provided GraphQL schemas")

        try:
            # Query the model and track query time
            start_time = time.time()
            question = "Can you inspect the following graphql schemas and compare them for any breaking changes?"
            lm = self.model + f"{question}: {schema1}, {schema2}\n"
            lm += "Answer: " + gen(name='answer')
            lm += guidance_json(name="generated_object", schema=self.expected_obj)

            # Increment API call count
            self.api_calls += 1
            query_time = time.time() - start_time
            self.query_times.append(query_time)

            # Strip HTML tags and extract the result
            result = self.strip_html_tags(lm['answer'])
            logger.info(f"Model output: {result}\n")

            # Create json representation of the result
            output_json = js.loads(lm["generated_object"])

            # Count the number of breaking changes
            breaking_changes = [change for change in output_json.get('changes', []) if change.get('breaking', False)]
            self.breaking_change_count += len(breaking_changes)

            logger.info(f"Generated output: {js.dumps(output_json, indent=4)}")

            # Return the JSON result with status
            return {
                "status": "success",
                "result": output_json
            }

        except Exception as e:
            logger.error(f"Error during comparison: {e}")
            # Return failure status with an empty result
            return {
                "status": "failure",
                "result": {}
            }

    def statistics(self):
        """
        Return statistics such as query times, API call counter, and breaking changes count.
        """
        if self.query_times:
            avg_query_time = sum(self.query_times) / len(self.query_times)
        else:
            avg_query_time = 0

        return {
            "total_api_calls": self.api_calls,
            "breaking_changes": self.breaking_change_count,
            "average_query_time": avg_query_time,
            "total_query_time": sum(self.query_times),
        }


# Usage example
if __name__ == "__main__":
    # Function to load schema content from a file
    def load_schema_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    # Load schemas from files
    schema1 = load_schema_file("data/schema1.graphql")
    schema2 = load_schema_file("data/schema2.graphql")

    # Environment variables for model file and expected JSON file path
    model_file = os.getenv("MODEL_FILE", "models/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf")
    expected_json_path = os.getenv("EXPECTED_JSON_PATH", "data/expected.json")

    # Create the comparator instance
    comparator = GraphQLComparator(model_file=model_file, expected_json_path=expected_json_path)

    # Log model information
    logger.info(f"Model Information: {comparator.model_info()}")

    # Compare schemas
    result = comparator.compare(schema1, schema2)
    logger.info(f"Comparison Result: {result}")

    # Log statistics
    logger.info(f"Statistics: {comparator.statistics()}")
