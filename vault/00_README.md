---
tags: [proyecto, overview]
created: 2026-05-29
status: draft
---

# Axenda — Agregador Inteligente de Conciertos

**Axenda** es un chatbot de Telegram que consulta una base de datos propia de eventos musicales para responder en lenguaje natural a preguntas como *"¿Qué conciertos hay este fin de semana en Gijón?"*, evitando que el usuario tenga que revisar redes sociales o múltiples webs de ticketeras.

## Problema que Resuelve

La información sobre conciertos en Gijón está dispersa: web del ayuntamiento, ticketeras, Instagram, carteles físicos. Axenda centraliza estos datos mediante scrapers automatizados y los expone a través de una conversación natural con un bot de Telegram.

## Stack Tecnológico

| Capa | Tecnología | Notas |
|------|-----------|-------|
| Lenguaje | Python 3.12+ | |
| Gestor de dependencias | Poetry | Entornos virtuales y lockfile |
| Framework Telegram | python-telegram-bot v21+ | Async nativo |
| API futura | FastAPI | Para interfaz web/móvil |
| Base de datos | SQLite → PostgreSQL | SQLite para MVP, migrable vía SQLAlchemy |
| ORM | SQLAlchemy 2.0 + Alembic | Async-ready, migraciones versionadas |
| Validación | Pydantic v2 | Tipado fuerte, settings desde .env |
| LLM | Ollama (modelo local) | Tool Calling con llama3.1 / mistral |
| Scraping | httpx + BeautifulSoup4 | HTTP async |
| Logging | structlog | JSON estructurado |
| Testing | pytest + pytest-asyncio | |

## Principios de Arquitectura

- **Clean Architecture**: dominio independiente de frameworks externos
- **Tool Calling**: el LLM no genera SQL — traduce lenguaje natural a llamadas de función controladas
- **Interfaz intercambiable**: Telegram hoy; Web/móvil mañana sin tocar la lógica de negocio
- **Regionalizable**: una ciudad hoy (Gijón), múltiples mañana
- **Multilingüe**: castellano ahora, asturiano añadiendo solo un system prompt

## Separación Documentación / Código

El proyecto Axenda vive en **dos ubicaciones** independientes:

| Qué | Dónde | Herramienta |
|-----|-------|-------------|
| **Documentación** | `~/Documents/Proyectos/Axenda/` | Obsidian |
| **Código** | `~/oscgf/github/axenda/` | Git + Poetry |

La documentación describe el *qué* y el *por qué*. El código implementa el *cómo*.
El código **no** se aloja dentro de la carpeta de Obsidian — son mundos separados.

## Estructura del Código

```
~/oscgf/github/axenda/
├── pyproject.toml               ← Poetry: dependencias, scripts
├── .env.example
├── .gitignore
├── alembic.ini
├── alembic/
│   └── versions/
├── src/
│   └── axenda/                  ← paquete Python principal
│       ├── domain/              ← Entidades, value objects, interfaces (ABC)
│       ├── application/         ← Casos de uso
│       ├── infrastructure/      ← BD, LLM, scrapers
│       └── interfaces/          ← Telegram bot, futura API REST
├── scripts/                     ← Puntos de entrada (scrapers)
└── tests/
```

## Documentación del Proyecto

| Documento | Contenido |
|-----------|-----------|
| [[01_Arquitectura_General]] | Capas, flujo de consulta, principios de diseño |
| [[02_Decisiones_Tecnicas]] | ADRs justificando cada elección tecnológica |
| [[03_Modelo_de_Datos]] | Entidades, atributos, relaciones, esquema |
| [[04_Tools_del_LLM]] | Catálogo de funciones que el LLM puede invocar |
| [[05_Estrategia_Scraping]] | Fuentes de datos, mapeo, frecuencia, deduplicación |
| [[06_Estrategia_Multilingue]] | Soporte castellano + asturiano en la capa LLM |
| [[07_Guia_Desarrollo]] | Setup local, comandos, flujo de trabajo, testing |
| [[08_Roadmap]] | Fases del proyecto e hitos |

## Requisitos Previos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Ollama](https://ollama.com/) con un modelo compatible con tool calling (llama3.1:8b o mistral:7b)
- Un token de bot de Telegram (obtenido de [@BotFather](https://t.me/BotFather))

## Quickstart

```bash
# 1. Clonar el repo (o navegar al directorio local)
cd ~/oscgf/github/axenda

# 2. Instalar dependencias
poetry install

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu TELEGRAM_BOT_TOKEN

# 4. Ejecutar migraciones
poetry run alembic upgrade head

# 5. Ejecutar scrapers (poblar BD)
poetry run python scripts/run_scrapers.py

# 6. Arrancar el bot
poetry run python -m axenda.interfaces.telegram.bot
```

---

> **Estado actual:** Fase 0 — Documentación completada. Siguiente: inicializar repo en `~/oscgf/github/axenda/`.
> Siguiente paso → [[07_Guia_Desarrollo]]
