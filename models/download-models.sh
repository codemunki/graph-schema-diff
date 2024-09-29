#!/bin/bash

# Define the directory for downloads
DOWNLOAD_DIR="./"

# Create the downloads directory if it doesn't exist
mkdir -p "$DOWNLOAD_DIR"

# Define a list of models as URL, expected SHA256, and enabled flag (true/false)
models=(
    "https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/resolve/main/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf 9193684683657e90707087bd1ed19fd0b277ab66358d19edeadc26d6fdec4f53 true"
    # Add more models in the format: "<URL> <SHA256> <enabled>"
    # "https://another-model-url <SHA256_2> false"
)

# Loop through each model in the list
for model in "${models[@]}"; do
    # Split the model data into URL, SHA256, and enabled flag
    MODEL_URL=$(echo "$model" | awk '{print $1}')
    EXPECTED_SHA=$(echo "$model" | awk '{print $2}')
    ENABLED=$(echo "$model" | awk '{print $3}')

    # Check if the download is enabled
    if [[ "$ENABLED" == "false" ]]; then
        echo "Skipping download for $MODEL_URL (disabled)."
        continue
    fi

    # Filename extracted from the URL
    MODEL_FILE=$(basename "$MODEL_URL")

    # Full path of the model in the download directory
    MODEL_PATH="$DOWNLOAD_DIR/$MODEL_FILE"

    # Check if the model file already exists
    if [[ -f "$MODEL_PATH" ]]; then
        echo "File $MODEL_FILE already exists, checking its SHA256 checksum..."

        # Calculate the SHA256 checksum of the existing file
        CALCULATED_SHA=$(shasum -a 256 "$MODEL_PATH" | awk '{ print $1 }')

        # Compare the calculated SHA256 with the expected one
        if [[ "$CALCULATED_SHA" == "$EXPECTED_SHA" ]]; then
            echo "SHA256 checksum for $MODEL_FILE is correct, skipping download."
            continue
        else
            echo "SHA256 checksum for $MODEL_FILE is incorrect!"
            echo "Expected: $EXPECTED_SHA"
            echo "Got: $CALCULATED_SHA"
            echo "Redownloading the file..."
        fi
    fi

    # Download the model file if it doesn't exist or if the checksum is incorrect
    echo "Downloading model from $MODEL_URL..."
    curl -L -o "$MODEL_PATH" "$MODEL_URL"

    # Check if the download was successful
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to download the model $MODEL_FILE."
        continue
    fi

    # Calculate the SHA256 checksum of the downloaded file
    echo "Calculating SHA256 checksum for $MODEL_FILE..."
    CALCULATED_SHA=$(shasum -a 256 "$MODEL_PATH" | awk '{ print $1 }')

    # Compare the calculated SHA256 with the expected one
    if [[ "$CALCULATED_SHA" == "$EXPECTED_SHA" ]]; then
        echo "SHA256 checksum for $MODEL_FILE is correct."
    else
        echo "SHA256 checksum for $MODEL_FILE is incorrect!"
        echo "Expected: $EXPECTED_SHA"
        echo "Got: $CALCULATED_SHA"
        rm "$MODEL_PATH"  # Optionally remove the file if checksum fails
    fi
    echo
done

echo "All models processed."
