SEARCH_EVENTS_TOOL = {
    "type": "function",
    "function": {
        "name": "search_events",
        "description": (
            "Busca eventos culturales en una ciudad con filtros opcionales "
            "de fecha, tipo, género y sala."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nombre de la ciudad. Ej: 'Gijón'.",
                },
                "date_from": {
                    "type": "string",
                    "description": (
                        "Fecha de inicio en formato YYYY-MM-DD (ej: 2026-05-30). "
                        "SOLO incluir si el usuario pide una fecha concreta o un periodo."
                    ),
                },
                "date_to": {
                    "type": "string",
                    "description": (
                        "Fecha de fin en formato YYYY-MM-DD (ej: 2026-05-31). "
                        "SOLO incluir si el usuario pide una fecha concreta o un periodo."
                    ),
                },
                "event_type": {
                    "type": "string",
                    "enum": [
                        "Música",
                        "Teatro",
                        "Exposición",
                        "Cine",
                        "Danza",
                        "Literatura",
                        "Infantil",
                        "Otros",
                    ],
                    "description": (
                        "Tipo de evento. INFIERELO de las palabras del usuario: "
                        "si dice concierto, conciertos, musica, conciertu, tocata → Música. "
                        "si dice teatro, obra, representación → Teatro. "
                        "si dice exposición, expo, muestra → Exposición. "
                        "si dice cine, película → Cine. "
                        "Si no puedes inferirlo, no uses este filtro."
                    ),
                },
                "genre": {
                    "type": "string",
                    "description": (
                        "Género musical: rock, pop, jazz, indie, electrónica, flamenco, "
                        "clásica, hip-hop, folk, metal, blues, reggae, soul, funk, latina. "
                        "Si no se menciona, no filtrar."
                    ),
                },
                "venue": {
                    "type": "string",
                    "description": "Nombre aproximado del espacio o sala.",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Número máximo de resultados.",
                },
            },
            "required": ["city"],
        },
    },
}

GET_EVENT_DETAILS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_event_details",
        "description": "Obtiene todos los detalles de un evento concreto por su ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "integer",
                    "description": "ID del evento obtenido de una búsqueda previa.",
                },
            },
            "required": ["event_id"],
        },
    },
}

LIST_VENUES_TOOL = {
    "type": "function",
    "function": {
        "name": "list_venues",
        "description": "Devuelve la lista de espacios o salas en una ciudad.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nombre de la ciudad.",
                },
            },
            "required": ["city"],
        },
    },
}

ALL_TOOLS = [SEARCH_EVENTS_TOOL, GET_EVENT_DETAILS_TOOL, LIST_VENUES_TOOL]
