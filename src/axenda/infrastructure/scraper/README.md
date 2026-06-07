# Catálogo de datos de scrapers

Mapeo entre los campos de salida del modelo `Event` y los campos de origen
de cada scraper. Solo se documentan los scrapers implementados; para añadir
uno nuevo, subclase `BaseScraper` y regístrelo en `registry.py`.

## Salida común (modelo `Event`)

Todos los scrapers producen instancias de `axenda.domain.models.Event` con
los siguientes campos:

| Campo          | Tipo            | Notas                                       |
|----------------|-----------------|---------------------------------------------|
| `id`           | `int`           | Asignado por la base de datos (`0` en scrap)|
| `title`        | `str`           | Obligatorio                                |
| `event_type`   | `EventType`     | Enum (`Música`, `Teatro`, …)                |
| `description`  | `str \| None`   | Texto plano                                 |
| `event_date`   | `datetime` (UTC)| Fecha de inicio                             |
| `price_info`   | `str \| None`   | Texto libre                                 |
| `url`          | `str \| None`   | URL canónica del evento en la fuente        |
| `source`       | `str`           | Identificador de la fuente (constante)      |
| `source_id`    | `str`           | ID en la fuente original                    |
| `image_url`    | `str \| None`   | URL absoluta de la imagen                   |
| `venue_id`     | `int \| None`   | Asignado por la base de datos               |
| `city_id`      | `int`           | Asignado por la base de datos (`0` en scrap)|
| `venue`        | `Venue \| None` | Resuelto por el pipeline de ingesta         |
| `genres`       | `list[str]`     | Vacío por defecto                           |

## `GijonOpenDataScraper`

- **Fuente:** `https://drupal.gijon.es/es/listado_eventos_tes4/?_format=json`
- `source` = `gijon_drupal`
- `city_name` = `Gijón` (`gijon`)
- Filtro: eventos con `fecha_inicio >= 2026-01-01 UTC`.

| Campo Event      | Campo origen                              | Transformación                          |
|------------------|-------------------------------------------|-----------------------------------------|
| `title`          | `titulo`                                  | `_clean_html` (unescape + normalizar)   |
| `event_type`     | `tipo`                                    | `EventType(...)`; fallback `OTROS`      |
| `description`    | —                                         | `None` (no se popula)                   |
| `event_date`     | `fecha_inicio`                            | `_parse_date` → UTC                     |
| `price_info`     | —                                         | `None` (no se popula)                   |
| `url`            | `alias`                                   | `https://www.gijon.es/eventos/{alias}`  |
| `source`         | constante                                 | `gijon_drupal`                          |
| `source_id`      | `id`                                      | `str(id)` o hash SHA-256 (fallback)     |
| `image_url`      | `imagen`                                  | `https://www.gijon.es/{path}`           |
| `venue.name`     | `titulo_directorio`                       | `get_venue_name`                        |
| `venue.address`  | `direccion_directorio`                    | `get_venue_address`                     |
| `venue.url`      | `alias_directorio`                        | `https://www.gijon.es/directorio/{...}` |

## `MusicasturianaScraper`

- **Fuente:** `https://musicasturiana.com/wp-json/tribe/events/v1/events`
- `source` = `musicasturiana`
- `city_name` = `asturias`
- Filtro: eventos con `start_date >= 2026-01-01 UTC`.
- Paginación: sigue `next_rest_url` con `per_page=100`.

| Campo Event      | Campo origen                       | Transformación                       |
|------------------|------------------------------------|--------------------------------------|
| `title`          | `title`                            | `unescape`                           |
| `event_type`     | constante                          | `MUSICA`                             |
| `description`    | `description`                      | `_strip_html`                        |
| `event_date`     | `start_date`                       | `_parse_date` → UTC                  |
| `price_info`     | `cost`                             | Sin transformación                   |
| `url`            | `url`                              | Sin transformación                   |
| `source`         | constante                          | `musicasturiana`                     |
| `source_id`      | `id`                               | `str(id)`                            |
| `image_url`      | `image.url`                        | Sin transformación                   |
| `venue.name`     | `venue.venue`                      | `get_venue_name`                     |
| `venue.address`  | `venue.address` + `venue.city`     | `get_venue_address` (unido con `, `) |
