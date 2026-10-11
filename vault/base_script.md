```python
#!/usr/bin/env python3

import urllib.request

import json

import pandas as pd

from datetime import datetime

from tabulate import tabulate

  

API_URL = "https://opendata.gijon.es/descargar.php?id=728&tipo=JSON"

  

with urllib.request.urlopen(API_URL) as r:

data = json.loads(r.read().decode())

  

musica = [e for e in data if e.get("tipo") == "Música"]

  

rows = []

for e in musica:

name = e.get("titulo", "").replace("&quot;", "\"").replace("&#039;", "'").replace("&amp;", "&")

date_str = e.get("fecha_inicio", "").split("\n")[0].strip()

try:

date = datetime.strptime(date_str, "%Y-%m-%d")

except ValueError:

date = datetime.min

place = e.get("titulo_directorio", "") or ""

addr = e.get("direccion_directorio", "") or ""

location = f"{place}, {addr}".strip(", ")

slug = e.get("alias", "").strip("/").split("/")[-1] or ""

url = f"https://www.gijon.es/eventos/{slug}" if slug else ""

rows.append({"Nombre": name, "Fecha": date, "Lugar": location, "URL": url})

  

df = pd.DataFrame(rows)

df = df.sort_values("Fecha", ascending=False).reset_index(drop=True)

df["Fecha"] = df["Fecha"].dt.strftime("%d/%m/%Y")

  

print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False, maxcolwidths=[60, 12, 50, 60]))
```