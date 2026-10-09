"""llm-serving-bench: a reproducible benchmark + cost harness for self-hosted LLMs.

The analysis core (workload, metrics, cost, slo, quantization, report) is pure
Python and unit-tested on CPU — no GPU, no server, no network. Live benchmarking
against vLLM / TGI lives in the clients + scripts and is clearly marked.
"""

__version__ = "0.1.0"
