---
tags: [arquitectura, diseño]
created: 2026-05-29
status: draft
---

# Arquitectura General de Axenda

> **Objetivo de este documento:** Explicar la estructura de capas, el flujo de una consulta y los principios que garantizan la escalabilidad futura del proyecto.

## Principios Rectores

1. **Independencia del Dominio**: Las reglas de negocio (qué es un Evento, cómo se busca) no dependen de Telegram, de SQLite, ni del LLM concreto.
2. **Interfaces Intercambiables**: La capa de transporte (Telegram) es un plugin. Añadir una API REST o un frontend web no requiere tocar la lógica de negocio.
3. **Tool Calling, no SQL Generation**: El LLM no genera SQL arbitrario. Traduce la intención del usuario a una llamada de función predefinida y validada. Esto es más seguro, más testeable y más controlable.
4. **Configuración por Localidad**: Ciudades, idiomas y fuentes de scraping se configuran, no se hardcodean.

## Las Cuatro Capas (Clean Architecture)

```
┌─────────────────────────────────────────────────┐
│                 INTERFACES                       │
│  Telegram Bot  │  (futura API REST)              │
│  Adaptadores de entrada — hablan con el exterior │
└──────────────────────┬──────────────────────────┘
                       │  depende de
┌──────────────────────▼──────────────────────────┐
│                APLICACIÓN                        │
│  Casos de Uso  │  DTOs                          │
│  Orquestan el flujo: reciben input, coordinan,  │
│  devuelven output                                │
└──────────────────────┬──────────────────────────┘
                       │  depende de
┌──────────────────────▼──────────────────────────┐
│                  DOMINIO                         │
│  Entidades  │  Value Objects  │  Repositorios    │
│  (ABC)                                          │
│  NO depende de nada externo. Puro Python.       │
└──────────────────────┬──────────────────────────┘
                       │  implementado por
┌──────────────────────▼──────────────────────────┐
│              INFRAESTRUCTURA                     │
│  SQLAlchemy  │  Ollama  │  Scrapers  │  HTTP     │
│  Implementaciones concretas de las interfaces    │
│  definidas en el dominio                         │
└─────────────────────────────────────────────────┘
```

### Capa de Dominio (`src/axenda/domain/`)

Define **qué** es el sistema, sin decir **cómo** se implementa:

- **Entidades**: `Event`, `Venue`, `City` — objetos con identidad
- **Value Objects**: `DateRange`, `GeoCoordinates`, `Locale` — objetos definidos por sus atributos
- **Interfaces de Repositorio** (ABC): `EventRepository`, `VenueRepository` — contratos que la infraestructura debe cumplir

**Regla de oro**: Esta capa no importa nada de SQLAlchemy, Telegram, Ollama ni httpx. Si algún día cambias de ORM o de LLM, esta capa no se toca.

### Capa de Aplicación (`src/axenda/application/`)

Define **qué se puede hacer** en el sistema:

- **Casos de uso**: `SearchEvents`, `GetEventDetails`, `ListVenues` — cada uno es una clase o función que orquesta una operación completa
- **DTOs**: Objetos planos de entrada/salida para los casos de uso

Un caso de uso típico:
1. Recibe un input (query en lenguaje natural + locale + ciudad)
2. Llama al LLM para que traduzca la query a una tool call
3. Ejecuta la tool call contra el repositorio
4. Llama al LLM para que formatee la respuesta en lenguaje natural
5. Devuelve el resultado

### Capa de Infraestructura (`src/axenda/infrastructure/`)

Implementa **cómo** se hacen las cosas:

- `database/`: Modelos ORM de SQLAlchemy, engine, implementaciones concretas de los repositorios
- `llm/`: Cliente de Ollama, definición de tools, system prompts
- `scraper/`: Scrapers concretos para cada fuente de datos

### Capa de Interfaces (`src/axenda/interfaces/`)

Adaptadores de entrada — cómo el mundo exterior habla con el sistema:

- `telegram/`: Handlers de comandos y mensajes del bot
- `api/`: (futuro) Rutas de FastAPI

---

## Flujo de una Consulta Típica

```
Usuario Telegram: "¿Hay conciertos de rock este finde en Gijón?"
        │
        ▼
┌──────────────────────────────────────────────┐
│ INTERFACES: telegram/handlers.py             │
│ - Recibe el mensaje                          │
│ - Extrae texto, chat_id, locale del usuario   │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│ APLICACIÓN: application/search_events.py     │
│ - Caso de uso: SearchEventsUseCase           │
│ - Paso 1: Envía prompt + tools al LLM        │
│ - Paso 2: Recibe function_call del LLM:       │
│     search_events(city="gijon",              │
│       date_from="2026-05-30",                │
│       date_to="2026-05-31", genre="rock")    │
│ - Paso 3: Ejecuta contra EventRepository      │
│ - Paso 4: Formatea resultados vía LLM         │
│ - Paso 5: Devuelve respuesta                  │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│ DOMINIO: domain/repositories.py (ABC)        │
│ - EventRepository.search(criteria) -> [Event] │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│ INFRAESTRUCTURA: database/repositories.py    │
│ - Implementación SQL con SQLAlchemy          │
│ - Query parametrizada, nunca SQL crudo       │
└──────────────────────────────────────────────┘
```

---

## Cómo Escala

### Nueva interfaz (Web/Móvil)

Añadir `src/axenda/interfaces/api/` con FastAPI. Los handlers de la API llaman a los **mismos casos de uso** que usa Telegram. Cero cambios en dominio, aplicación o infraestructura.

### Nueva ciudad

1. Añadir una fila en la tabla `cities`
2. Implementar un scraper nuevo en `infrastructure/scraper/` (ej: `oviedo_opendata.py`)
3. Registrar el scraper en `registry.py`

El LLM ya sabe filtrar por ciudad porque la tool `search_events` acepta `city` como parámetro.

### Nuevo tipo de evento (teatro, exposiciones...)

1. Añadir el valor al enum `EventType` en dominio
2. El scraper ya puede clasificar eventos con ese tipo
3. La tool `search_events` ya filtra por tipo — el LLM lo usará cuando el usuario pregunte

### Nuevo idioma (asturiano)

1. Añadir un system prompt en asturiano en `infrastructure/llm/prompts.py`
2. El caso de uso selecciona el prompt según el locale del usuario
3. Las tools y la BD siguen en castellano — el LLM traduce la respuesta final

Ver [[06_Estrategia_Multilingue]] para más detalle.

---

> **Siguiente lectura recomendada:** [[02_Decisiones_Tecnicas]] — el porqué de cada tecnología.
