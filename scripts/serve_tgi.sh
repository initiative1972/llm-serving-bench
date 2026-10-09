# serve_tgi.sh

```bash
#!/usr/bin/env bash

# Launch Text Generation Inference (TGI) via Docker.
# Requires the NVIDIA runtime.
#
# Example:
#   MODEL=TheBloke/Mistral-7B-Instruct-v0.2-GPTQ QUANT=gptq bash scripts/serve_tgi.sh

set -euo pipefail

MODEL="${MODEL:-TheBloke/Mistral-7B-Instruct-v0.2-GPTQ}"
QUANT="${QUANT:-gptq}"
PORT="${PORT:-8080}"
VOLUME="${VOLUME:-$PWD/.hf-cache}"

docker run --gpus all --shm-size 1g -p "${PORT}:80" \
  -v "${VOLUME}:/data" \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id "${MODEL}" \
  --quantize "${QUANT}" \
  --max-input-length 4096 \
  --max-total-tokens 8192
```

## Description

This script launches a Hugging Face Text Generation Inference (TGI) server in a Docker container with NVIDIA GPU support.

### Environment Variables

| Variable | Default Value |
|----------|--------------|
| `MODEL` | `TheBloke/Mistral-7B-Instruct-v0.2-GPTQ` |
| `QUANT` | `gptq` |
| `PORT` | `8080` |
| `VOLUME` | `$PWD/.hf-cache` |

### Example Usage

```bash
MODEL=TheBloke/Mistral-7B-Instruct-v0.2-GPTQ \
QUANT=gptq \
bash scripts/serve_tgi.sh
```

### Docker Command Details

- `--gpus all` : Exposes all available GPUs to the container.
- `--shm-size 1g` : Sets shared memory size to 1 GB.
- `-p "${PORT}:80"` : Maps the host port to container port 80.
- `-v "${VOLUME}:/data"` : Mounts a local directory for model/cache storage.
- `--model-id` : Specifies the Hugging Face model to load.
- `--quantize` : Enables model quantization mode.
- `--max-input-length 4096` : Maximum input token length.
- `--max-total-tokens 8192` : Maximum total tokens (input + output).