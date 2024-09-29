python3 -m venv .venv
source .venv/bin/activate

# Install python bindings for llama cpp
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python


