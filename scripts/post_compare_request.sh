#!/bin/bash

# Ensure two arguments are passed (schema files)
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <schema1_file> <schema2_file>"
    exit 1
fi

# Read the GraphQL schemas from the provided files
SCHEMA1=$(<"$1")
SCHEMA2=$(<"$2")

# API endpoint for schema comparison
API_URL="http://127.0.0.1:5000/compare"

# Construct the JSON body using jq
BODY=$(jq -n \
  --arg schema1 "$SCHEMA1" \
  --arg schema2 "$SCHEMA2" \
  '{schema1: $schema1, schema2: $schema2}')

# Send the POST request to the /compare endpoint using curl
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$BODY" "$API_URL")

# Check if the response contains valid JSON and pretty print it using jq
if jq -e . >/dev/null 2>&1 <<<"$RESPONSE"; then
    echo "API Response (Pretty Printed):"
    echo "$RESPONSE" | jq
else
    echo "API Response (Raw):"
    echo "$RESPONSE"
fi
