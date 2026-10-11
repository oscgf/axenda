---
tags: [scraping, datos, fuentes]
created: 2026-05-29
status: draft
---

# Estrategia de Scraping

> **Objetivo:** Documentar las fuentes de datos, el mapeo de campos, la frecuencia de actualización y las reglas de deduplicación.

---

## Fuentes de Datos

### Fuente 1: API Drupal del Ayuntamiento de Gijón (ACTUAL)

| Campo                                  | Valor                                                                  |
| -------------------------------------- | ---------------------------------------------------------------------- |
| **Nombre técnico**                     | `gijon_drupal`                                                         |
| **URL**                                | `https://drupal.gijon.es/es/listado_eventos_tes4/?_format=json`        |
| **Formato**                            | JSON                                                                   |
| **Tipo de acceso**                     | API pública, sin autenticación                                         |
| **Frecuencia de scraping**             | 1 vez al día                                                           |
| **Cobertura**                          | Eventos de 2026 (~470). Música, teatro, exposiciones, cine, danza...   |
| **Nota**                               | Datos actualizados. Sustituye a la API Open Data que solo tenía 2025.  |

### Fuente 2: API Open Data del Ayuntamiento de Gijón (OBSOLETA)

| Campo                                  | Valor                                                                                               |
| -------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **Nombre técnico**                     | `gijon_opendata`                                                                                    |
| **URL**                                | `https://opendata.gijon.es/descargar.php?id=728&tipo=JSON`                                          |
| **Estado**                             | ⚠️ Obsoleta — solo contiene datos hasta mediados de 2025. Reemplazada por la API Drupal.            |
| **Formato**                            | JSON                                                                                                |
| **Tipo de acceso**                     | API pública, sin autenticación                                                                      |
| **Frecuencia de actualización**        | Cada hora                                                                                           |
| **Frecuencia de scraping recomendada** | 1 vez al día (los eventos no cambian cada hora)                                                     |
| **Cobertura**                          | Eventos culturales de Gijón: música, teatro, exposiciones, cine, danza, literatura, infantil, otros |
| **Script existente**                   | [[base_script]]                                                                                     |

#### Mapeo de Campos

| Campo API Open Data | Campo en BD (`Event`) | Transformación |
|---------------------|----------------------|----------------|
| `titulo` | `title` | Limpiar entidades HTML (`&quot;` → `"`, `&#039;` → `'`, `&amp;` → `&`) |
| `tipo` | `event_type` | Mapeo directo: "Música" → "Música" |
| `fecha_inicio` | `date_start` | Parsear `YYYY-MM-DD` (primera línea, ignorar horas múltiples) |
| `fecha_fin` | `date_end` | Parsear si está disponible, si no `null` |
| `titulo_directorio` | → `Venue.name` | Nombre del espacio |
| `direccion_directorio` | → `Venue.address` | Dirección del espacio |
| `alias` | `url` | Construir URL: `https://www.gijon.es/eventos/{slug}` donde slug = último segmento del alias |
| `descripcion` | `description` | Si existe en la API (verificar) |
| `precio` | `price_info` | Si existe en la API (verificar) |
| — | `source` | Hardcodeado: `"gijon_opendata"` |
| `id` o hash | `source_id` | Usar el ID interno si existe, o hash de título+fecha+venue |
| — | `city_id` | Referencia a la ciudad "Gijón" en la BD |
| — | `genres` | No disponible en esta fuente. Dejar vacío por ahora. |

#### Notas del Script Existente

El script [[base_script]] actual:
- Filtra solo eventos de tipo `"Música"` (nos interesa mantener el filtro configurable para capturar todos los tipos en la BD)
- Usa `urllib` síncrono → migrar a `httpx` async
- Usa `pandas` para formatear → innecesario en el nuevo flujo; trabajaremos con objetos Pydantic
- Imprime con `tabulate` → la salida será insertar en BD, no imprimir

---

### Fuentes Futuras Planeadas

| Fuente                                     | Tipo                 | Prioridad | Notas                                                           |
| ------------------------------------------ | -------------------- | --------- | --------------------------------------------------------------- |
| Ticketeras (Entradas.com, Ticketmaster...) | Web scraping         | Media     | Requiere estudio legal de ToS. Pueden tener API no documentada. |
| Otras ciudades (Oviedo, Avilés, Santander) | Open Data / scraping | Baja      | Cuando el modelo de ciudad esté validado con Gijón              |
| RRSS (Instagram, Facebook de salas)        | Scraping/API         | Baja      | Muy frágil, baja prioridad                                      |
| Web del ayuntamiento (otras secciones)     | Scraping HTML        | Media     | Si la API no cubre todos los eventos                            |

> **Nota:** El detalle de cada fuente futura está documentado en [[09_Fuentes_Futuras]].

---

## Arquitectura del Scraper

```
┌────────────────────────────────────────────┐
│            scripts/run_scrapers.py          │
│  Punto de entrada. Itera el registry.      │
└────────────────────┬───────────────────────┘
                     │
┌────────────────────▼───────────────────────┐
│      infrastructure/scraper/registry.py     │
│  Dict: {"gijon_opendata": GijonOpenData()} │
└────────────────────┬───────────────────────┘
                     │
┌────────────────────▼───────────────────────┐
│   infrastructure/scraper/gijon_opendata.py  │
│  - fetch(): descarga JSON                  │
│  - parse(): convierte a lista de Events    │
│  - upsert(): inserta/actualiza en BD       │
└────────────────────────────────────────────┘
```

Cada scraper implementa la interfaz:

```python
class BaseScraper(ABC):
    source: str                          # Identificador único
    city_name: str                       # Ciudad objetivo

    async def fetch(self) -> list[dict]  # Obtener datos crudos de la fuente
    def parse(self, raw: list[dict]) -> list[Event]  # Transformar a entidades
    async def upsert(self, events: list[Event]) -> ScrapeLog  # Guardar en BD (vía repositorio)
```

---

## Reglas de Deduplicación

Ver [[03_Modelo_de_Datos#Estrategia de Deduplicación]].

Resumen:
1. Buscar por `source + source_id`
2. Si no hay `source_id`, buscar por `title + date_start + venue_id + city_id`
3. Si existe → UPDATE (precio, descripción, fecha_fin si cambió)
4. Si no existe → INSERT

---

## Programación de Ejecución

Para MVP, un script ejecutado vía cron:

```bash
# crontab -e
0 8 * * * cd /path/to/musicbot && poetry run python scripts/run_scrapers.py
```

En el futuro, si hay múltiples scrapers con diferentes frecuencias, se puede migrar a APScheduler dentro del propio proceso.

---

## Consideraciones de Robustez

- **Timeout HTTP**: 30 segundos máximo por fuente
- **Reintentos**: 3 intentos con backoff exponencial (1s, 2s, 4s)
- **Rate limiting**: Respetar si la API lo requiere (por ahora no)
- **Validación de esquema**: Si la API cambia el formato del JSON, el parser debe fallar explícitamente (no silenciosamente). El `ScrapeLog` registra el error.
- **Idempotencia**: Ejecutar el scraper 2 veces seguidas no debe duplicar eventos.

---

> **Siguiente lectura recomendada:** [[06_Estrategia_Multilingue]]
