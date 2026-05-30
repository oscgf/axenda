import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update


@pytest.fixture
def mock_update() -> Update:
    update = MagicMock(spec=Update)
    update.effective_chat = MagicMock(spec=Chat)
    update.effective_chat.id = 1234
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.message.chat = MagicMock(spec=Chat)
    update.message.chat.send_action = AsyncMock()
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    return MagicMock()


class TestStartHandler:
    def test_start_replies_with_welcome(self, mock_update, mock_context) -> None:
        from axenda.interfaces.telegram.handlers import start

        asyncio.run(start(mock_update, mock_context))
        mock_update.message.reply_text.assert_called_once()
        text = mock_update.message.reply_text.call_args[0][0]
        assert "Axenda" in text
        assert "Gijón" in text or "Gijon" in text


class TestHelpHandler:
    def test_help_replies_with_info(self, mock_update, mock_context) -> None:
        from axenda.interfaces.telegram.handlers import help_command

        asyncio.run(help_command(mock_update, mock_context))
        mock_update.message.reply_text.assert_called_once()
        text = mock_update.message.reply_text.call_args[0][0]
        assert "/start" in text
        assert "/help" in text


class TestIdiomaHandler:
    def test_idioma_replies(self, mock_update, mock_context) -> None:
        from axenda.interfaces.telegram.handlers import idioma

        asyncio.run(idioma(mock_update, mock_context))
        mock_update.message.reply_text.assert_called_once()


class TestMessageHandler:
    def test_handle_message_calls_llm(self, mock_update, mock_context) -> None:
        mock_update.message.text = "¿Hay conciertos?"

        with patch(
            "axenda.interfaces.telegram.handlers._get_answer",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = "3 conciertos encontrados"

            from axenda.interfaces.telegram.handlers import handle_message

            asyncio.run(handle_message(mock_update, mock_context))

            mock_get.assert_called_once()
            mock_update.message.chat.send_action.assert_called_once_with(
                action="typing"
            )
            mock_update.message.reply_text.assert_called_once_with(
                "3 conciertos encontrados"
            )

    def test_handle_message_timeout(self, mock_update, mock_context) -> None:
        mock_update.message.text = "pregunta lenta"

        with patch(
            "axenda.interfaces.telegram.handlers._get_answer",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.side_effect = asyncio.TimeoutError

            from axenda.interfaces.telegram.handlers import handle_message

            asyncio.run(handle_message(mock_update, mock_context))

            text = mock_update.message.reply_text.call_args[0][0]
            assert "⏳" in text

    def test_handle_message_error(self, mock_update, mock_context) -> None:
        mock_update.message.text = "pregunta rota"

        with patch(
            "axenda.interfaces.telegram.handlers._get_answer",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.side_effect = RuntimeError("boom")

            from axenda.interfaces.telegram.handlers import handle_message

            asyncio.run(handle_message(mock_update, mock_context))

            text = mock_update.message.reply_text.call_args[0][0]
            assert "❌" in text
