from __future__ import annotations

import os

import httpx


class ParseurClient:
    """Minimal Parseur API client.

    This client is intentionally small so it can be swapped for a richer implementation later.
    """

    def __init__(self) -> None:
        self.token = os.getenv("PARSEUR_API_TOKEN")
        self.mailbox_id = os.getenv("PARSEUR_MAILBOX_ID")

    def is_enabled(self) -> bool:
        return bool(self.token and self.mailbox_id)

    async def fetch_document_text(self, document_id: str) -> str | None:
        if not self.is_enabled():
            return None

        url = f"https://api.parseur.com/mailboxes/{self.mailbox_id}/documents/{document_id}"
        headers = {"Authorization": f"Token {self.token}"}

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None
            data = resp.json()

        # Different Parseur templates can map fields differently.
        # We fallback over common keys and finally serialized payload.
        for key in ("content", "body", "text", "raw"):
            if key in data and isinstance(data[key], str):
                return data[key]

        return str(data)
