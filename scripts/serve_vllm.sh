# serve_vllm.sh

```bash
#!/usr/bin/env bash

# Launch a vLLM OpenAI-compatible server.
# Requires a CUDA GPU and `pip install vllm`.
#
# Example:
#   MODEL=TheBloke/Mistral-7B-Instruct-v0.2-AWQ QUANT=awq bash scripts/serve_vllm.sh

set -euo pipefail

MODEL="${MODEL:-TheBloke/Mistral-7B-Instruct-v0.2-AWQ}"
QUANT="${QUANT:-awq}"
PORT="${PORT:-8000}"
MAXLEN="${MAXLEN:-8192}"

python -m vllm.entrypoints.openai.api_server \
  --model "${MODEL}" \
  --quantization "${QUANT}" \
  --max-model-len "${MAXLEN}" \
  --port "${PORT}" \
  --disable-log-requests
```

## Description

This script starts a **vLLM OpenAI-compatible API server** using a specified language model and quantization method. It is intended for running LLM inference on a CUDA-enabled GPU.

### Prerequisites

- NVIDIA CUDA-compatible GPU
- Python environment with `vllm` installed:

```bash
pip install vllm
```

### Environment Variables

| Variable | Default Value | Description |
|----------|--------------|-------------|
| `MODEL` | `TheBloke/Mistral-7B-Instruct-v0.2-AWQ` | Hugging Face model to serve |
| `QUANT` | `awq` | Quantization method |
| `PORT` | `8000` | API server port |
| `MAXLEN` | `8192` | Maximum model context length |

### Example Usage

```bash
MODEL=TheBloke/Mistral-7B-Instruct-v0.2-AWQ \
QUANT=awq \
bash scripts/serve_vllm.sh
```

### Command Breakdown

```bash
python -m vllm.entrypoints.openai.api_server
```

Starts the OpenAI-compatible REST API server provided by vLLM.

Parameters:

- `--model "${MODEL}"`  
  Loads the specified model.

- `--quantization "${QUANT}"`  
  Enables the selected quantization format (e.g., AWQ).

- `--max-model-len "${MAXLEN}"`  
  Sets the maximum context window.

- `--port "${PORT}"`  
  Exposes the API on the specified port.

- `--disable-log-requests`  
  Disables request logging to reduce console output and overhead.

### Default Endpoint

Once started, the API is typically accessible at:

```text
http://localhost:8000
```

and supports OpenAI-compatible endpoints such as:

```text
/v1/chat/completions
/v1/completions
/models
```