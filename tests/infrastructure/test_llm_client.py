
from axenda.infrastructure.llm.client import OllamaClient


class TestOllamaClient:
    def test_build_system_message_spanish(self) -> None:
        client = OllamaClient()
        msg = client.build_system_message("Gijón", "es")
        assert msg["role"] == "system"
        assert "Gijón" in msg["content"]
        assert "search_events" in msg["content"]

    def test_build_system_message_includes_today(self) -> None:
        client = OllamaClient()
        msg = client.build_system_message("Gijón")
        assert "NO inventes" in msg["content"]

    def test_build_system_message_asturian_locale(self) -> None:
        client = OllamaClient()
        msg = client.build_system_message("Gijón", "ast")
        assert msg["role"] == "system"
        assert "ast" in msg["content"]
