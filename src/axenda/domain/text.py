"""Utilidades de texto compartidas por las capas de dominio y aplicación."""


def _normalize_city(name: str) -> str:
    """Normaliza un nombre de ciudad: minúsculas y sin acentos.

    Usado para matching case/accent-insensitive en nombres de ciudades.
    """
    if not name:
        return ""
    accents = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
    }
    for accented, plain in accents.items():
        name = name.replace(accented, plain)
    return name.lower()
