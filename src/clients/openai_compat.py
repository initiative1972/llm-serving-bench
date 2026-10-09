"""OpenAI-compatible async client for vLLM / TGI (live GPU mode).

Captures TTFT from the first streamed token and counts streamed chunks as output
tokens. Requires ``httpx``, imported lazily so the rest of the harness stays
importable (and CI stays green) on a box without it. NOT exercised in CI.
"""
from __future__ import annotations

import time

from .base import RequestResult


class OpenAICompatClient:
    def __init__(self, base_url, model, api_key="EMPTY", endpoint="chat"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint

    def _payload(self, spec):
        # Simple repeatable filler; swap for real tokenised prompts if you need
        # exact input-length control in a formal benchmark.
        prompt = "word " * spec.prompt_tokens
        body = {
            "model": self.model,
            "max_tokens": spec.max_output_tokens,
            "temperature": 0.0,
            "stream": True,
        }
        if self.endpoint == "chat":
            body["messages"] = [{"role": "user", "content": prompt}]
            path = "/v1/chat/completions"
        else:
            body["prompt"] = prompt
            path = "/v1/completions"
        return path, body

    async def arun(self, spec, start_offset=0.0):
        import httpx  # lazy import so the package imports without httpx installed

        path, body = self._payload(spec)
        headers = {"Authorization": f"Bearer {self.api_key}"}
        t0 = time.perf_counter()
        ttft = None
        out_tokens = 0
        ok = True
        err = ""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream("POST", self.base_url + path,
                                         json=body, headers=headers) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        if line.strip() == "data: [DONE]":
                            break
                        if ttft is None:
                            ttft = time.perf_counter() - t0
                        out_tokens += 1
        except Exception as exc:  # benchmark records failures rather than raising
            ok = False
            err = str(exc)
        elapsed = time.perf_counter() - t0
        return RequestResult(
            request_id=spec.request_id,
            prompt_tokens=spec.prompt_tokens,
            output_tokens=max(out_tokens, 0),
            start_time=start_offset,
            end_time=start_offset + elapsed,
            ttft=ttft,
            success=ok,
            error=err,
        )
