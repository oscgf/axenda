---
tags: [desarrollo, setup, guia]
created: 2026-05-29
status: draft
---

# Guía de Desarrollo

> **Objetivo:** Documentar el entorno de desarrollo, comandos esenciales, flujo de trabajo y convenciones.

---

## Ubicación del Código

```
~/oscgf/github/axenda/          ← Repositorio Git
```

La documentación del proyecto vive en `~/Documents/Proyectos/Axenda/` (vault de Obsidian).
Son dos ubicaciones independientes. Los paths de esta guía asumen que estás en el repo de código.

---

## Requisitos Previos

| Herramienta | Versión mínima | Verificación |
|------------|---------------|--------------|
| Python | 3.12+ | `python --version` |
| Poetry | 1.8+ | `poetry --version` |
| Ollama | latest | `ollama --version` |
| Git | 2.40+ | `git --version` |

### Instalación de Ollama y Modelo

```bash
# Instalar Ollama (macOS)
brew install ollama

# Descargar modelo con soporte de tool calling
ollama pull llama3.1:8b

# Verificar que funciona
ollama run llama3.1:8b "Hola, ¿qué eres?"
```

### Token de Telegram

1. Abrir Telegram y hablar con [@BotFather](https://t.me/BotFather)
2. Enviar `/newbot` y seguir las instrucciones
3. Guardar el token (algo como `123456:ABC-DEF1234gh...`)
4. Añadirlo al archivo `.env`

---

## Primeros Pasos

```bash
# 1. Situarse en el repositorio
cd ~/oscgf/github/axenda

# 2. Instalar dependencias
poetry install

# 3. Activar el entorno virtual
poetry shell

# 4. Copiar y editar variables de entorno
cp .env.example .env
# Editar .env con tu editor favorito

# 5. Ejecutar migraciones
alembic upgrade head

# 6. Ejecutar scrapers (primera carga de datos)
python scripts/run_scrapers.py

# 7. Arrancar el bot
python -m axenda.interfaces.telegram.bot
```

---

## Variables de Entorno (`.env`)

```bash
# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234gh...

# Base de datos (SQLite por defecto)
DATABASE_URL=sqlite:///data/axenda.db

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Logging
LOG_LEVEL=DEBUG

# Ciudad por defecto
DEFAULT_CITY=Gijón
```

---

## Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `poetry install` | Instalar dependencias |
| `poetry add <pkg>` | Añadir una dependencia |
| `poetry run pytest` | Ejecutar tests |
| `poetry run alembic revision --autogenerate -m "descripcion"` | Crear migración |
| `poetry run alembic upgrade head` | Aplicar migraciones |
| `poetry run alembic downgrade -1` | Revertir última migración |
| `poetry run python scripts/run_scrapers.py` | Ejecutar scrapers |
| `poetry run python -m axenda.interfaces.telegram.bot` | Arrancar el bot |

---

## Estructura de Ramas Git

```
main            ← Producción (siempre deployable)
├── develop     ← Integración
│   ├── feat/nombre-funcionalidad
│   ├── fix/nombre-bug
│   └── docs/nombre-doc
```

Convención de commits: [Conventional Commits](https://www.conventionalcommits.org/)

```
feat(scraper): añadir scraper de la API open data de Gijón
fix(llm): corregir parseo de fechas relativas
docs(adr): documentar decisión de usar Ollama
refactor(domain): extraer DateRange como value object
test(search): añadir tests para búsqueda por género
```

---

## Flujo de Trabajo Diario

```bash
# 1. Actualizar desde develop
git checkout develop
git pull origin develop

# 2. Crear rama para la tarea
git checkout -b feat/nombre-funcionalidad

# 3. Desarrollar (TDD recomendado)
#    - Escribir test → verlo fallar
#    - Implementar → verlo pasar
#    - Refactorizar → tests siguen en verde

# 4. Antes de commit, ejecutar
poetry run pytest
poetry run ruff check src/ tests/
poetry run mypy src/

# 5. Commit y push
git add .
git commit -m "feat: descripción"
git push origin feat/nombre-funcionalidad

# 6. Pull Request a develop
```

---

## Testing

- **Framework**: pytest + pytest-asyncio
- **BD en tests**: SQLite en memoria (`sqlite:///:memory:`) — rápido y aislado
- **Mocks**: Para la capa de LLM y la API de Telegram, usar `unittest.mock` o `pytest-mock`
- **Cobertura objetivo**: >80% en dominio y aplicación

```bash
# Ejecutar todos los tests
poetry run pytest

# Ejecutar tests de un módulo concreto
poetry run pytest tests/domain/

# Con cobertura
poetry run pytest --cov=src --cov-report=term-missing
```

---

## Linting y Tipado

```bash
# Linter (Ruff — rápido, reemplaza flake8 + isort)
poetry run ruff check src/ tests/

# Formateo automático
poetry run ruff format src/ tests/

# Type checker
poetry run mypy src/
```

---

## Recursos de Aprendizaje

- [Clean Architecture en Python](https://www.cosmicpython.com/) — libro gratuito online
- [Documentación de python-telegram-bot](https://docs.python-telegram-bot.org/)
- [Documentación de Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html)
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/)

---

> **Siguiente lectura recomendada:** [[08_Roadmap]]
