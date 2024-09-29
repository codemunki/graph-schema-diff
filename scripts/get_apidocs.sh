#!/bin/bash

# API endpoint for apidocs
API_URL="http://127.0.0.1:5000/apidocs

# Send the GET request to the /apidocs endpoint using curl
RESPONSE=$(curl -s -X GET "$API_URL")

# Print the API response
echo "API Response:"
echo "$RESPONSE"
