"""Primary LLM path: NVIDIA Nemotron via the Meterless engine.

Sponsor requirement: the product runs on NVIDIA Nemotron, directly or
through Meterless. Credentials + exact model IDs are issued in the HackOS
workspace (see docs/METERLESS_SETUP.md) — they are env vars, never code.

Model-per-step (the course's own wording: "choose the right model for
each step"):
- planner_model (reasoning-class Nemotron) → THINK hypotheses.
- fast_model (small fast Nemotron) → draft-reply responder (see
  reasoning/respond.py). If no fast model is configured, the responder
  is skipped — never faked with a template.

Transport: curl subprocess. urllib proxy-tunnels time out in this
sandbox (the Jev client already uses the curl path for the same reason).
The API shape is OpenAI-compatible (/v1/chat/completions); the base URL
comes from the Meterless workspace.
"""
from __future__ import annotations

import json
import os
import subprocess

from .base import LLMProvider, LLMResponse


class MeterlessNemotron(LLMProvider):
    name = "nemotron-via-meterless"

    def __init__(self, api_url: str, api_key: str, planner_model: str,
                 fast_model: str = ""):
        if not api_url or not api_key:
            raise ValueError("MeterlessNemotron needs api_url and api_key")
        if not planner_model:
            raise ValueError("MeterlessNemotron needs planner_model "
                             "(from the HackOS Meterless workspace)")
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.planner_model = planner_model
        self.fast_model = fast_model

    def _call(self, model: str, system: str, user: str,
              max_tokens: int) -> str:
        env = {k: v for k, v in os.environ.items()
               if k not in ("no_proxy", "NO_PROXY")}
        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        })
        proc = subprocess.run(
            ["curl", "-sS", "--max-time", "70",
             f"{self.api_url}/v1/chat/completions",
             "--noproxy", "127.0.0.1,localhost",
             "-H", f"Authorization: Bearer {self.api_key}",
             "-H", "Content-Type: application/json",
             "--data", payload],
            capture_output=True, text=True, timeout=80, env=env,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Meterless call failed: {proc.stderr.strip()[:300]}")
        try:
            body = json.loads(proc.stdout)
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, json.JSONDecodeError):
            raise RuntimeError(f"unexpected Meterless response: {proc.stdout[:300]}")

    def generate(self, system: str, user: str, max_tokens: int = 800) -> LLMResponse:
        """Planner call (reasoning model)."""
        return LLMResponse(
            text=self._call(self.planner_model, system, user, max_tokens),
            model=self.planner_model,
        )

    def generate_fast(self, system: str, user: str,
                      max_tokens: int = 400) -> LLMResponse | None:
        """Responder call (fast small model). None when not configured."""
        if not self.fast_model:
            return None
        return LLMResponse(
            text=self._call(self.fast_model, system, user, max_tokens),
            model=self.fast_model,
        )
