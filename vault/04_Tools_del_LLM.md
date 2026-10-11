---
tags: [llm, tools, function-calling]
created: 2026-05-29
status: draft
---

# Tools del LLM

> **Objetivo:** Definir el catálogo de funciones (tools) que el LLM puede invocar para responder a las preguntas del usuario. Cada tool tiene parámetros tipados y validados por Pydantic.

---

## Principio de Diseño

El LLM recibe:
1. Un **system prompt** que define su rol
2. La **pregunta del usuario** en lenguaje natural
3. Una lista de **tools** disponibles

El LLM decide:
- Qué tool llamar (o ninguna si es una pregunta conversacional)
- Con qué parámetros

La aplicación ejecuta la tool contra el repositorio y devuelve los resultados al LLM para que los formatee.

---

## Catálogo de Tools

### 1. `search_events`

Busca eventos con filtros combinables.

```python
{
    "name": "search_events",
    "description": "Busca eventos culturales en una ciudad con filtros opcionales de fecha, tipo y género.",
    "parameters": {
        "city": {
            "type": "string",
            "description": "Nombre de la ciudad. Ej: 'Gijón', 'Oviedo'."
        },
        "date_from": {
            "type": "string",
            "description": "Fecha de inicio en formato YYYY-MM-DD. Si el usuario dice 'este finde', calcular el viernes de esta semana."
        },
        "date_to": {
            "type": "string",
            "description": "Fecha de fin en formato YYYY-MM-DD. Si el usuario dice 'este finde', calcular el domingo de esta semana."
        },
        "event_type": {
            "type": "string",
            "enum": ["Música", "Teatro", "Exposición", "Cine", "Danza", "Literatura", "Infantil", "Otros"],
            "description": "Tipo de evento. Si el usuario no especifica, no filtrar por tipo."
        },
        "genre": {
            "type": "string",
            "description": "Género musical: 'rock', 'pop', 'jazz', 'indie', 'electrónica', 'flamenco', 'clásica', 'hip-hop', 'folk', 'metal'... Si no se menciona, no filtrar."
        },
        "venue": {
            "type": "string",
            "description": "Nombre aproximado del espacio. Si el usuario menciona un sitio concreto."
        },
        "limit": {
            "type": "integer",
            "default": 10,
            "description": "Número máximo de resultados."
        }
    },
    "required": ["city"]
}
```

**Ejemplos de invocación por el LLM:**

| Usuario dice | Tool call generada |
|-------------|-------------------|
| "¿Qué conciertos hay este finde en Gijón?" | `search_events(city="Gijón", event_type="Música", date_from="2026-05-30", date_to="2026-05-31")` |
| "¿Hay algo de jazz en el Teatro Jovellanos?" | `search_events(city="Gijón", genre="jazz", venue="Teatro Jovellanos")` |
| "Dime todos los eventos de esta semana" | `search_events(city="Gijón", date_from="2026-05-29", date_to="2026-06-04")` |

---

### 2. `get_event_details`

Obtiene la información completa de un evento específico (el usuario ha visto un resultado y quiere más detalles).

```python
{
    "name": "get_event_details",
    "description": "Obtiene todos los detalles de un evento concreto por su ID.",
    "parameters": {
        "event_id": {
            "type": "integer",
            "description": "ID del evento obtenido de una búsqueda previa."
        }
    },
    "required": ["event_id"]
}
```

---

### 3. `list_venues`

Lista los espacios disponibles en una ciudad.

```python
{
    "name": "list_venues",
    "description": "Devuelve la lista de espacios/salas en una ciudad.",
    "parameters": {
        "city": {
            "type": "string",
            "description": "Nombre de la ciudad."
        }
    },
    "required": ["city"]
}
```

---

### 4. `get_venue_events` *(futura, Fase 2+)*

Eventos en un venue concreto.

```python
{
    "name": "get_venue_events",
    "description": "Devuelve los próximos eventos en un espacio concreto.",
    "parameters": {
        "venue_id": {"type": "integer"},
        "date_from": {"type": "string"},
        "limit": {"type": "integer", "default": 10}
    },
    "required": ["venue_id"]
}
```

---

## Formato de Respuesta de las Tools

Cada tool devuelve al LLM una estructura JSON limpia para que pueda formatear la respuesta:

```json
{
    "events": [
        {
            "id": 42,
            "title": "Vetusta Morla",
            "event_type": "Música",
            "date_start": "2026-05-30T21:00:00",
            "venue": "Teatro Jovellanos",
            "city": "Gijón",
            "price_info": "20€ anticipada, 25€ taquilla",
            "genres": ["rock", "indie"],
            "url": "https://www.gijon.es/eventos/..."
        }
    ],
    "total": 1,
    "city": "Gijón"
}
```

---

## Validación y Seguridad

Cada tool call del LLM pasa por:

1. **Validación Pydantic**: parámetros tipados, rangos, enums
2. **Sanitización**: los strings se escapan antes de tocar la BD
3. **Rate limiting**: máximo N consultas por usuario/minuto (a implementar en la capa de aplicación)

Si el LLM genera parámetros inválidos (ej: `event_type="fiestón"`), Pydantic lanza `ValidationError` y la aplicación pide al LLM que reformule.

---

## System Prompt (Base)

El system prompt que acompaña a estas tools:

```
Eres un asistente cultural para la ciudad de {city}. 
Tu trabajo es ayudar a los usuarios a encontrar eventos culturales.

Reglas:
- Si el usuario pregunta por eventos, usa la tool search_events.
- Si el usuario pregunta por los detalles de un evento que ya has mostrado, usa get_event_details.
- Si el usuario pregunta por salas o espacios, usa list_venues.
- Interpreta expresiones temporales relativas: "este finde" = viernes a domingo de la semana actual, "mañana" = día siguiente, "la semana que viene" = lunes a domingo de la próxima semana.
- Si el usuario no especifica ciudad, asume {city}.
- Responde SIEMPRE en {locale}.
- Sé conciso pero amable. Incluye fecha, hora, lugar y precio cuando estén disponibles.
- Si no hay resultados, sugiere ampliar la búsqueda (otras fechas, otros tipos de evento).
```

Las variables `{city}` y `{locale}` se rellenan según el contexto del usuario (configuración o detección automática).

---

> **Siguiente lectura recomendada:** [[05_Estrategia_Scraping]]
