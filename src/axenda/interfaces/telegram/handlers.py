import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from axenda.application.search_events import SearchEventsUseCase
from axenda.infrastructure.config import settings
from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.repositories import (
    SQLEventRepository,
    SQLVenueRepository,
)
from axenda.infrastructure.llm.client import OllamaClient


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 ¡Hola! Soy **Axenda**, tu asistente cultural para Gijón.\n\n"
        "Pregúntame lo que quieras sobre eventos:\n"
        "• \"¿Qué conciertos hay este finde?\"\n"
        "• \"Dime eventos de teatro\"\n"
        "• \"¿Qué salas hay en Gijón?\"\n\n"
        "Comandos: /help /idioma"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "**Axenda** — asistente cultural de Gijón\n\n"
        "/start — Mensaje de bienvenida\n"
        "/help — Esta ayuda\n"
        "/idioma — Cambiar idioma (es / ast)\n\n"
        "Fuente de datos: Open Data Gijón"
    )


async def idioma(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Por ahora solo estoy disponible en castellano. "
        "L'asturianu llegará más tarde 💙💛"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip()
    if not user_text:
        return

    await update.message.chat.send_action(action="typing")

    try:
        async with asyncio.timeout(45):
            answer = await _get_answer(user_text, settings.default_city)
    except TimeoutError:
        answer = (
            "⏳ El asistente está tardando más de lo normal. "
            "Intenta con una pregunta más concreta o prueba de nuevo."
        )
    except Exception:
        answer = "❌ Ha ocurrido un error. Prueba de nuevo en unos segundos."

    await update.message.reply_text(answer)


async def _get_answer(question: str, city: str) -> str:
    llm = OllamaClient()
    async with async_session() as session:
        use_case = SearchEventsUseCase(
            llm,
            SQLEventRepository(session),
            SQLVenueRepository(session),
        )
        return await use_case.execute(question, city.lower())
