---
tags: [i18n, l10n, asturiano, llm]
created: 2026-05-29
status: draft
---

# Estrategia Multilingüe

> **Objetivo:** Diseñar la capa de IA para que el chatbot pueda interactuar en castellano (fase 1) y asturiano (fase 2) sin cambios estructurales en el código.

---

## Principio de Diseño

**Los datos se almacenan en un idioma canónico (castellano). El LLM traduce la respuesta al idioma del usuario.**

Esto es preferible a:
- Tener la BD en dos idiomas (duplicación, complejidad de sincronización)
- Traducir con APIs externas (coste, latencia, dependencia)

El LLM ya entiende asturiano razonablemente bien (los modelos modernos han visto texto en asturiano durante el entrenamiento). La calidad depende del modelo concreto, pero para un asistente conversacional es suficiente.

---

## Cómo Funciona

### Fase 1: Solo Castellano (AHORA)

```
Usuario (es): "¿Qué conciertos hay este finde?"
        │
        ▼
System prompt: locale="es"
        │
        ▼
LLM responde en castellano
```

- `default_locale` de la ciudad Gijón = `"es"`
- El system prompt se carga en castellano
- Las tools devuelven datos en castellano
- El LLM responde en castellano

### Fase 2: Castellano + Asturiano (FUTURO)

```
Usuario (ast): "¿Qué conciertos hai esti fin de selmana?"
        │
        ▼
System prompt: locale="ast"
        │
        ▼
LLM responde n'asturianu
```

El cambio es mínimo:

1. **Detección de locale**: el usuario configura su preferencia (`/idioma ast`), o el sistema detecta el idioma de la pregunta
2. **System prompt en asturiano**: se añade un archivo de prompt alternativo
3. **Las tools no cambian**: los parámetros y respuestas de las tools siguen en castellano (datos canónicos)
4. **El LLM traduce al vuelo**: recibe los datos en castellano y los expresa en asturiano en la respuesta final

---

## Implementación Técnica

### Archivos de Prompt

```
infrastructure/llm/prompts/
├── system_es.txt       # Prompt en castellano
└── system_ast.txt      # Prompt en asturiano (futuro)
```

### Selección de Prompt

```python
def get_system_prompt(city: City, user_locale: str | None = None) -> str:
    locale = user_locale or city.default_locale  # "es" o "ast"
    template = load_prompt(f"system_{locale}.txt")
    return template.format(city=city.name, locale=locale)
```

### Comando de Cambio de Idioma (Fase 2)

```
Usuario: /idioma ast
Bot: "Entendío. A partir d'agora falaré n'asturianu."
```

Se guarda la preferencia en la tabla de usuarios (a crear cuando se implemente multi-usuario).

---

## System Prompt en Asturiano (Borrador)

Borrador para validar con hablantes nativos cuando se active la fase 2:

```
Yes un asistente cultural pa la ciudá de {city}.
El to trabayu ye ayudar a los usuarios a atopar eventos culturales.

Regles:
- Si l'usuariu entruga por eventos, usa la ferramienta search_events.
- Si l'usuariu entruga polos detalles d'un eventu que yá amosesti, usa get_event_details.
- Si l'usuariu entruga por sales o espacios, usa list_venues.
- Interpreta espresiones temporales relatives: "esti fin de selmana" = vienres a domingu de la selmana actual, "mañana" = día siguiente, "la selmana que vien" = llunes a domingu de la próxima selmana.
- Si l'usuariu nun especifica ciudá, asume {city}.
- Respuende SIEMPRE n'{locale}.
- Sé concisu pero amable. Inclúi fecha, hora, llugar y preciu cuando tean disponibles.
- Si nun hai resultaos, suxer ampliar la gueta (otres feches, otros tipos d'eventu).
```

---

## Consideraciones

- **Calidad del asturiano**: Los modelos actuales (Llama 3.1, Mistral) generan asturiano aceptable pero pueden cometer errores. Idealmente validar con un hablante nativo antes de activar.
- **Nombres propios**: Títulos de eventos, nombres de salas y direcciones no se traducen (permanecen en castellano o en su idioma original).
- **Fallback**: Si el LLM no genera buen asturiano, se puede implementar un fallback a castellano + pedir disculpas.
- **Expansión futura**: El mismo patrón sirve para añadir euskera, catalán, gallego, inglés...

---

> **Siguiente lectura recomendada:** [[07_Guia_Desarrollo]]
