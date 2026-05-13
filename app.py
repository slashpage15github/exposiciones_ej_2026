import sqlite3
from functools import lru_cache
from pathlib import Path

from flask import Flask, abort, jsonify, render_template

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "db" / "drug_seizures.db"

EXAMPLES = [
    {
        "slug": "leaflet-world",
        "title": "Leaflet + OpenStreetMap",
        "library": "Leaflet",
        "summary": "Un localizador mundial ligero con teselas raster de OpenStreetMap y marcadores por país.",
        "template": "leaflet_world.html",
        "highlights": ["Sin API key", "Configuración rápida", "Ideal para mapas con marcadores"],
    },
    {
        "slug": "openlayers-world",
        "title": "Vista Global con OpenLayers",
        "library": "OpenLayers",
        "summary": "Un ejemplo más orientado a SIG con entidades vectoriales sobre una vista mundial.",
        "template": "openlayers_world.html",
        "highlights": ["Soporte de proyecciones", "Capas vectoriales", "Buen enfoque SIG"],
    },
    {
        "slug": "maplibre-world",
        "title": "Demo Mundial con MapLibre",
        "library": "MapLibre",
        "summary": "Un mapa mundial interactivo y moderno con una librería WebGL de código abierto.",
        "template": "maplibre_world.html",
        "highlights": ["Renderizado WebGL", "Mapas guiados por estilo", "Escala bien"],
    },
]


@lru_cache(maxsize=1)
def load_seizure_records():
    query = """
        SELECT
            Region AS region,
            SubRegion AS subregion,
            Country AS country,
            DrugName AS drug_name,
            msCode AS country_code,
            ROUND(
                SUM(
                    CASE
                        WHEN TRIM(COALESCE("Kilograms", '')) = '' THEN 0
                        ELSE CAST(REPLACE("Kilograms", ',', '') AS REAL)
                    END
                ),
                2
            ) AS kilograms
        FROM drug_seizures
        WHERE TRIM(COALESCE(msCode, '')) <> ''
        GROUP BY Region, SubRegion, Country, DrugName, msCode
        HAVING kilograms > 0
        ORDER BY kilograms DESC, Country ASC, DrugName ASC
    """

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query).fetchall()

    return [
        {
            "region": row["region"],
            "subregion": row["subregion"],
            "country": row["country"],
            "drugName": row["drug_name"],
            "countryCode": row["country_code"],
            "kilograms": row["kilograms"],
        }
        for row in rows
    ]


@app.route("/")
def index():
    return render_template("home.html", examples=EXAMPLES)


@app.route("/examples/<slug>")
def example_page(slug):
    example = next((item for item in EXAMPLES if item["slug"] == slug), None)
    if example is None:
        abort(404)
    return render_template(example["template"], example=example, examples=EXAMPLES)


@app.route("/api/seizures")
def seizure_data():
    return jsonify({"records": load_seizure_records()})


app.config["DEBUG"] = True


if __name__ == "__main__":
    app.run()
