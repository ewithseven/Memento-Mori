"""Minimal Ollama client (standard library only)."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

URL = os.environ.get("HAKEM_OLLAMA_URL", "http://localhost:11434") + "/api/chat"
MODEL = "qwen2.5:7b"
RETRIES = 6


@dataclass(frozen=True)
class Reply:
    text: str
    prompt_tokens: int
    output_tokens: int


def chat(system: str | None, user: str, *, seed: int, temperature: float = 0.4, top_p: float = 0.95,
         max_tokens: int = 350, num_ctx: int = 4096, timeout: float = 600, model: str | None = None) -> Reply:
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    body = {
        "model": model or MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "top_p": top_p, "num_predict": max_tokens,
                    "num_ctx": num_ctx, "seed": seed},
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            break
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if attempt == RETRIES - 1:
                raise
            time.sleep(10 * (attempt + 1))  # the server may be restarting; the seed keeps the reply the same
    return Reply(data["message"]["content"], data.get("prompt_eval_count", 0), data.get("eval_count", 0))
