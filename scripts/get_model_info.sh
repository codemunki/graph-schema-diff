#!/bin/bash

# API endpoint for model info
API_URL="http://127.0.0.1:5000/model-info"

# Send the GET request to the /model-info endpoint using curl
RESPONSE=$(curl -s -X GET "$API_URL")

# Print the API response
echo "API Response:"
echo "$RESPONSE"
