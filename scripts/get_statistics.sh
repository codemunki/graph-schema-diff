#!/bin/bash

# API endpoint for statistics
API_URL="http://127.0.0.1:5000/statistics"

# Send the GET request to the /statistics endpoint using curl
RESPONSE=$(curl -s -X GET "$API_URL")

# Print the API response
echo "API Response:"
echo "$RESPONSE"
