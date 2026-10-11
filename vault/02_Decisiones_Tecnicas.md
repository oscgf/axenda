---
tags: [adr, decisiones, tecnologia]
created: 2026-05-29
status: draft
---

# Decisiones Técnicas (ADRs)

> **Architecture Decision Records**: Cada decisión técnica relevante se documenta aquí con su contexto, opciones consideradas, decisión tomada y consecuencias.

---

## ADR-001: Python + Poetry como Stack Base

**Fecha**: 2026-05-29
**Estado**: Aceptado

### Contexto
Necesitamos un lenguaje con buen ecosistema para bots de Telegram, scraping, bases de datos e integración con LLMs. El desarrollador tiene experiencia previa en Python.

### Opciones Consideradas

| Opción | Pros | Contras |
|--------|------|---------|
| **Python + Poetry** | Ecosistema maduro (PTB, SQLAlchemy, Ollama SDK, FastAPI), el dev ya lo conoce, tipado progresivo con mypy/pyright | Rendimiento menor que Go/Rust (no crítico para un bot) |
| TypeScript + Bun | Tipado fuerte, buen ecosistema de bots (grammY) | El dev no tiene experiencia previa, ecosistema de IA menos maduro para tool calling local |
| Go | Rendimiento excelente, binarios estáticos | Ecosistema de IA aún verde, más verboso para prototipado rápido |

### Decisión
**Python 3.12+ con Poetry como gestor de dependencias.**

### Consecuencias
- Rápido desarrollo de MVP
- Acceso a todo el ecosistema de datos/IA de Python
- Poetry garantiza entornos reproducibles con lockfile
- Si el bot escala masivamente, se puede reescribir la capa de infraestructura en Go manteniendo el dominio

---

## ADR-002: SQLite para MVP, Migrable a PostgreSQL

**Fecha**: 2026-05-29
**Estado**: Aceptado

### Contexto
Necesitamos almacenar eventos, venues y ciudades. El volumen inicial es bajo (cientos/miles de eventos en una ciudad). Queremos empezar rápido pero sin hipotecar el futuro.

### Opciones Consideradas

| Opción                     | Pros                                                                            | Contras                                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **SQLite + SQLAlchemy**    | Cero configuración, sin servidor, archivo único, SQLAlchemy abstrae el dialecto | Concurrent writes limitados, no escala horizontalmente                                                  |
| PostgreSQL desde el inicio | Escalable, concurrente,全文搜索 nativo                                              | Requiere servidor, más configuración, overkill para MVP                                                 |
| MongoDB                    | Schemaless, flexible                                                            | Menos adecuado para datos relacionales (eventos ↔ venues ↔ ciudades), tool calling más complejo sin SQL |

### Decisión
**SQLite para desarrollo y MVP. SQLAlchemy como ORM para que migrar a PostgreSQL sea cambiar una línea de configuración.**

### Consecuencias
- Arranque inmediato: `poetry run alembic upgrade head` sin instalar Postgres
- Alembic gestiona las migraciones igual en ambos motores
- Cuando el proyecto crezca (múltiples scrapers concurrentes, alta concurrencia de usuarios), migrar a Postgres es trivial: cambiar `DATABASE_URL` y re-ejecutar migraciones.

---

## ADR-003: LLM Local con Ollama

**Fecha**: 2026-05-29
**Estado**: Aceptado

### Contexto
El bot necesita traducir lenguaje natural a consultas estructuradas (tool calling). Queremos empezar sin coste de API y con privacidad total de los datos.

### Opciones Consideradas

| Opción | Pros | Contras |
|--------|------|---------|
| **Ollama (llama3.1:8b / mistral:7b)** | Gratis, local, privacidad, soporta tool calling nativo en modelos recientes | Requiere hardware (Apple Silicon lo maneja bien), modelos pequeños pueden alucinar más |
| OpenAI API (gpt-4o-mini) | Excelente tool calling, sin carga de hardware | Coste por uso, dependencia externa, latencia de red, privacidad |
| Groq / Together.ai | Rápidos, tool calling decente, free tier generoso | Dependencia externa, latencia |

### Decisión
**Ollama con `llama3.1:8b` o `mistral:7b` como modelo local.** Se recomienda empezar con `llama3.1:8b` por su buen soporte de tool calling. Si la precisión no es suficiente, se evalúa migrar a OpenAI.

### Consecuencias
- Necesario tener Ollama instalado y el modelo descargado
- Tool calling con modelos locales puede requerir prompts más detallados y validación extra
- La capa de infraestructura abstrae el proveedor → cambiar a OpenAI en el futuro es implementar otro adapter, no reescribir nada

---

## ADR-004: python-telegram-bot (PTB) sobre Alternativas

**Fecha**: 2026-05-29
**Estado**: Aceptado

### Contexto
Necesitamos un framework para interactuar con la API de Telegram de forma async.

### Opciones Consideradas

| Opción | Pros | Contras |
|--------|------|---------|
| **python-telegram-bot v21** | Más maduro (2015), async nativo, documentación excelente, comunidad grande, maneja polling y webhook | Algo más verboso que alternativas minimalistas |
| aiogram | Moderno, async, buen router | Comunidad más pequeña, menos recursos de aprendizaje |
| pyTelegramBotAPI | Simple, síncrono | Sin soporte async nativo, bloquearía el event loop con llamadas al LLM |

### Decisión
**python-telegram-bot v21+.**

### Consecuencias
- Integración natural con el resto del stack async (FastAPI futuro, httpx, SQLAlchemy async)
- El código de los handlers queda limpio y testeable
- Al estar en la capa de interfaces, cambiar de framework en el futuro no afecta al dominio

---

## ADR-005: Tool Calling en lugar de Generación SQL

**Fecha**: 2026-05-29
**Estado**: Aceptado

### Contexto
El LLM debe traducir "¿qué conciertos hay de rock este finde?" en una consulta a la base de datos. Hay dos enfoques posibles.

### Opciones Consideradas

| Opción | Pros | Contras |
|--------|------|---------|
| **Tool Calling** | El LLM elige una función predefinida con parámetros validados. Seguro, testeable, controlado. El repositorio ejecuta SQL parametrizado. | Requiere modelos con soporte de tool calling |
| Text-to-SQL | El LLM genera la query SQL directamente. Más flexible para consultas ad-hoc. | Riesgo de SQL injection, queries ineficientes, difícil de validar y testear |

### Decisión
**Tool Calling.** Se definen funciones (`search_events`, `get_event_details`, `list_venues`) con parámetros tipados. El LLM decide qué función llamar y con qué parámetros. La capa de aplicación ejecuta la función contra el repositorio.

### Consecuencias
- Seguridad: nunca se ejecuta SQL generado por el LLM
- Testabilidad: las tools se prueban unitariamente sin LLM
- Control: si el LLM alucina parámetros, la validación de Pydantic los rechaza antes de tocar la BD
- Limitación: consultas no previstas requieren añadir una tool nueva (poco frecuente en este dominio)

---

> **Siguiente lectura recomendada:** [[03_Modelo_de_Datos]]
