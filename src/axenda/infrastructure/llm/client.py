from datetime import UTC, datetime

import httpx

from axenda.infrastructure.config import settings


class OllamaClient:
    def __init__(self) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        payload: dict = {
            "model": self._model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def generate(self, messages: list[dict]) -> str:
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]

    def build_system_message(self, city: str, locale: str = "es") -> dict:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        return {
            "role": "system",
            "content": (
                f"Eres un asistente cultural para {city}. Hoy es {today}.\n"
                f"Usa search_events si el usuario pregunta por eventos. "
                f"Usa list_venues si pregunta por salas. "
                f"Usa get_event_details si pregunta por un evento concreto.\n"
                f"Responde en {locale}.\n"
                f"Para 'finde' o 'fin de semana' usa date_from y date_to "
                f"con el viernes y domingo de esta semana. "
                f"Las fechas en formato YYYY-MM-DD."
            ),
        }
