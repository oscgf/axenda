---
tags: [scraping, fuentes, futuro]
created: 2026-05-29
status: draft
---

# Fuentes Futuras

> **Objetivo:** Documentar las fuentes candidatas para futura ampliación del scraper. Cada fuente se evalúa antes de implementar: viabilidad legal (ToS), estabilidad del formato y solapamiento con fuentes ya cubiertas.

---

# Fuentes importantes
| Fuente          | URL                                                                                                                                                                                                                       | Tipo         | Prioridad | Cobertura                                   | Notas |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | --------- | ------------------------------------------- | ----- |
| musicaasturiana | https://musicasturiana.com/axenda (general)<br>https://musicasturiana.com/axenda/lista/ (vista lista con 14 elementos)<br>https://musicasturiana.com/axenda/mes/ (vista calendario con eventos de las próximas 4 semanas) | Web scraping |           | Bastantes conciertos de música en asturiano |       |
|                 |                                                                                                                                                                                                                           |              |           |                                             |       |

# Sugerencias
## Ticketeras y Plataformas de Venta

| Fuente                     | URL                                      | Tipo               | Prioridad | Cobertura | Notas                                                                                              |
| -------------------------- | ---------------------------------------- | ------------------ | --------- | --------- | -------------------------------------------------------------------------------------------------- |
| Entradas.com               | `https://www.entradas.com`               | Web scraping       | Media     | Nacional  | API no documentada, carga dinámica (JS). Buscar endpoints internos con DevTools.                   |
| Ticketmaster               | `https://www.ticketmaster.es`            | Web scraping / API | Media     | Nacional  | API `discovery` v2 documentada pero con API key. Evaluar si la key gratuita cubre eventos locales. |
| El Corte Inglés (entradas) | `https://www.elcorteingles.es/entradas/` | Web scraping       | Baja      | Nacional  | Solapamiento parcial con Ticketmaster.                                                             |
| SeeTickets                 | `https://www.seetickets.com/es`          | Web scraping       | Baja      | Nacional  | Menor presencia en Asturias.                                                                       |
| Giglon                     | `https://www.giglon.com`                 | Web scraping       | Media     | España    | Buena cobertura de conciertos pequeños. Carga dinámica.                                            |
| Wegow                      | `https://www.wegow.com`                  | Web scraping       | Media     | España    | Comunidad de conciertos, buena fuente de eventos pequeños.                                         |
| Mutick                     | `https://www.mutick.com`                 | Web scraping       | Baja      | España    | Ticketera pequeña, eventos de sala.                                                                |

---

## Ayuntamientos y Open Data

| Fuente            | URL                                                               | Tipo          | Prioridad | Notas                                                                |
| ----------------- | ----------------------------------------------------------------- | ------------- | --------- | -------------------------------------------------------------------- |
| Open Data Oviedo  | Por determinar                                                    | Open Data     | Media     | Verificar si tienen portal de datos abiertos con agenda cultural.    |
| Open Data Avilés  | Por determinar                                                    | Open Data     | Media     | Ídem.                                                                |
| Agenda Web Gijón  | https://www.gijon.es/es/eventos?materia=Cultural&tipo=M%C3%BAsica | Scraping HTML | Media     | Si la API no cubre todos los eventos, scrapear la web como fallback. |
| Agenda Web Oviedo | `https://www.oviedo.es/...`                                       | Scraping HTML | Baja      | Fallback si no hay open data.                                        |
| Agenda Web Avilés | `https://aviles.es/...`                                           | Scraping HTML | Baja      | Ídem.                                                                |
| Santander         | `https://www.santander.es/...`                                    | Scraping HTML | Baja      | Expansión fuera de Asturias.                                         |
| Bilbao / Donosti  | Por determinar                                                    | Open Data     | Baja      | Corredor norte, cuando el modelo multi-ciudad esté maduro.           |

---

## Redes Sociales

| Fuente | URL | Tipo | Prioridad | Notas |
|--------|-----|------|-----------|-------|
| Instagram (salas) | `https://www.instagram.com/{sala}/` | API Graph / scraping | Baja | API oficial muy restrictiva (solo cuentas Business conectadas). Scraping frágil, cambios frecuentes de UI. Solo si un venue no publica por otro canal. |
| Facebook (salas) | `https://www.facebook.com/{sala}/events` | API Graph | Baja | API de Events deprecated. Solo páginas con token. Valorar si merece la pena. |
| X / Twitter (salas) | `https://x.com/{sala}` | API v2 / scraping | Muy baja | API de pago. Scraping muy frágil. Casi nunca es fuente primaria de eventos. |
| Telegram (canales) | `t.me/{canal}` | API Bot | Baja | Algunas salas publican en canales. API de Bot gratuita y estable, pero formato no estructurado. |

---

## Salas y Venues Directos (Web Propia)

| Fuente | URL | Tipo | Prioridad | Notas |
|--------|-----|------|-----------|-------|
| Sala Albéniz (Gijón) | `https://www.salaalbeniz.com/` | Scraping HTML | Alta | Programación en web propia, no siempre en ticketeras. |
| Sala Acapulco (Gijón) | `https://www.salaacapulco.com/` | Scraping HTML | Alta | Ídem. |
| Sala Whippoorwill (Oviedo) | Por determinar | Scraping HTML | Media | Sala de referencia en Oviedo. |
| Sala Sir Laurens (Oviedo) | Por determinar | Scraping HTML | Media | Ídem. |
| Sala Tribeca (Avilés) | Por determinar | Scraping HTML | Baja | Sala de referencia en Avilés. |
| OTRA Sala (Gijón) | Por determinar | Scraping HTML | Media | Eventos de pequeño formato. |
| CPAS (Gijón) | Por determinar | Scraping HTML | Media | Centro de cultura anticuada, programación alternativa. |
| Teatro Jovellanos | `https://www.teatrojovellanos.com/` | Scraping HTML | Media | Ya cubierto parcialmente por Open Data Gijón. Evaluar solapamiento. |
| Laboral Ciudad de la Cultura | `https://www.laboralciudaddelacultura.com/` | Scraping HTML | Media | Eventos culturales y conciertos. |

---

## Agregadores y Fuentes Especializadas

| Fuente | URL | Tipo | Prioridad | Notas |
|--------|-----|------|-----------|-------|
| Spotify (conciertos cercanos) | API | API | Media | API devuelve conciertos de artistas seguidos. Requiere auth de usuario. |
| Songkick | `https://www.songkick.com` | API | Media | Buena cobertura de conciertos. Evaluar ToS de API. |
| Bandsintown | `https://www.bandsintown.com` | API | Media | Ídem. |
| Last.fm Events | `https://www.last.fm` | API | Baja | Menos cobertura en España. |
| Resident Advisor | `https://ra.co` | Scraping | Baja | Electrónica. Muy poca cobertura en Asturias. |
| Infolocal (Comarca) | Por determinar | Scraping HTML | Media | Agenda cultural de comarca. Formato simple, buen candidato para scraping. |

---

## Criterios de Evaluación de una Fuente

Antes de implementar un scraper para una fuente, se evalúa:

1. **Legal**: ¿Los ToS permiten scraping? ¿Hay API pública? ¿Se puede obtener permiso?
2. **Estabilidad**: ¿El formato/schema cambia a menudo? ¿El HTML tiene selectores estables?
3. **Cobertura**: ¿Aporta eventos que no están ya en otras fuentes? (evitar duplicados de scraping)
4. **Calidad**: ¿Los datos vienen completos? (título, fecha, hora, precio, descripción, venue)
5. **Volumen**: ¿Cuántos eventos nuevos/mes aporta? Si son 2 al mes, mejor entrada manual que mantener un scraper.
6. **Esfuerzo**: ¿Es un JSON/API sencillo o requiere navegación Selenium + resolver CAPTCHAs?

---

## Priorización Recomendada

1. **Fase 1 (tras MVP con Open Data Gijón):** Salas con web propia en Gijón (Albéniz, Acapulco) — son las que más eventos musicales generan fuera del circuito municipal.
2. **Fase 2:** Ticketeras (Giglon, Wegow, Entradas.com) — cubren el circuito comercial que Open Data no captura.
3. **Fase 3:** Expansión a Oviedo y Avilés (Open Data o scraping de webs municipales).
4. **Fase 4:** Agregadores (Songkick, Bandsintown) como fuentes complementarias.
5. **Fase 5:** RRSS solo si una sala no publica por ningún otro canal.

---

> **Siguiente lectura recomendada:** [[05_Estrategia_Scraping]]
