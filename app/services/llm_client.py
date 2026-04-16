from __future__ import annotations

import json
from typing import Any

import httpx

from app.schemas import LLMConfig


class LLMClient:
    """Lightweight OpenAI-compatible chat client.

    Uses user-provided API key/base URL/model so users can bring their own key.
    """

    async def chat_json(self, *, config: LLMConfig, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        url = config.base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.model,
            "temperature": config.temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        if isinstance(content, str):
            return json.loads(content)
        raise ValueError("LLM response content is not text JSON")
