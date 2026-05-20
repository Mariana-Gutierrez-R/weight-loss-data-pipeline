"""Pipeline educativo de ingenieria de datos sobre obesidad y habitos.

El pipeline usa solo librerias de la biblioteca estandar de Python:
1. Extrae automaticamente el dataset publico de UCI.
2. Si no hay internet, usa una muestra local de respaldo para reproducibilidad.
3. Carga datos crudos a SQLite como zona staging.
4. Limpia, transforma y mueve datos a un warehouse SQLite.
5. Genera archivos mart para el dashboard.
"""

from __future__ import annotations

import csv
import io
import json
import math
import sqlite3
import statistics
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
MART_DIR = DATA_DIR / "mart"

SOURCE_URL = (
    "https://archive.ics.uci.edu/static/public/544/"
    "estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition.zip"
)
SOURCE_PAGE = "https://archive.ics.uci.edu/dataset/544/estimation+of+obesity"
RAW_CSV = RAW_DIR / "obesity_source.csv"
STAGING_DB = STAGING_DIR / "obesity_staging.db"
WAREHOUSE_DB = WAREHOUSE_DIR / "obesity_warehouse.db"
DASHBOARD_JSON = MART_DIR / "dashboard_data.json"
CURATED_CSV = MART_DIR / "obesity_curated.csv"
SCRAPING_CLEAN_TABLE_CSV = MART_DIR / "tabla_limpia_scraping.csv"
SCRAPING_CLEAN_TABLE_MD = MART_DIR / "tabla_limpia_scraping.md"
SUMMARY_JSON = MART_DIR / "pipeline_summary.json"


FALLBACK_ROWS = [
    ["Female", 21, 1.62, 64, "yes", "yes", 2, 3, "Sometimes", "no", 2, "no", 0, 1, "no", "Sometimes", "Public_Transportation", "Normal_Weight"],
    ["Female", 21, 1.52, 56, "yes", "yes", 3, 3, "Sometimes", "yes", 3, "yes", 3, 0, "yes", "Sometimes", "Public_Transportation", "Normal_Weight"],
    ["Male", 23, 1.80, 77, "yes", "yes", 2, 3, "Sometimes", "no", 2, "no", 2, 1, "no", "Frequently", "Public_Transportation", "Normal_Weight"],
    ["Male", 27, 1.80, 87, "no", "yes", 3, 3, "Sometimes", "no", 2, "no", 2, 0, "no", "Frequently", "Walking", "Overweight_Level_I"],
    ["Male", 22, 1.78, 89, "no", "yes", 2, 1, "Sometimes", "no", 2, "no", 0, 0, "no", "Sometimes", "Public_Transportation", "Overweight_Level_II"],
    ["Male", 29, 1.62, 53, "no", "yes", 2, 3, "Sometimes", "no", 2, "no", 0, 0, "no", "Sometimes", "Automobile", "Normal_Weight"],
    ["Female", 23, 1.50, 55, "yes", "yes", 3, 3, "Sometimes", "no", 2, "no", 1, 0, "no", "Sometimes", "Motorbike", "Normal_Weight"],
    ["Male", 22, 1.64, 53, "no", "yes", 2, 3, "Sometimes", "no", 2, "no", 3, 0, "no", "Sometimes", "Public_Transportation", "Normal_Weight"],
    ["Male", 24, 1.78, 64, "yes", "yes", 3, 3, "Sometimes", "no", 2, "no", 1, 1, "no", "Frequently", "Public_Transportation", "Normal_Weight"],
    ["Female", 22, 1.72, 68, "yes", "yes", 2, 3, "Sometimes", "no", 2, "no", 1, 1, "no", "Sometimes", "Public_Transportation", "Normal_Weight"],
    ["Male", 26, 1.85, 105, "yes", "yes", 2, 3, "Frequently", "no", 1, "no", 0, 2, "no", "Frequently", "Automobile", "Obesity_Type_I"],
    ["Female", 35, 1.60, 82, "yes", "yes", 2, 3, "Frequently", "no", 1, "no", 0, 2, "no", "Sometimes", "Automobile", "Obesity_Type_I"],
    ["Male", 31, 1.72, 98, "yes", "yes", 1, 3, "Always", "no", 1, "no", 0, 2, "no", "Frequently", "Automobile", "Obesity_Type_II"],
    ["Female", 26, 1.67, 112, "yes", "yes", 1, 3, "Frequently", "no", 1, "no", 0, 2, "no", "Sometimes", "Public_Transportation", "Obesity_Type_III"],
    ["Male", 18, 1.75, 58, "no", "no", 3, 3, "Sometimes", "no", 2, "no", 3, 0, "no", "no", "Walking", "Insufficient_Weight"],
    ["Female", 20, 1.70, 50, "no", "no", 3, 3, "Sometimes", "no", 2, "no", 2, 0, "no", "no", "Walking", "Insufficient_Weight"],
    ["Male", 40, 1.68, 92, "yes", "yes", 2, 3, "Frequently", "yes", 1, "no", 0, 2, "no", "Frequently", "Automobile", "Obesity_Type_I"],
    ["Female", 32, 1.58, 74, "yes", "yes", 2, 3, "Sometimes", "no", 2, "no", 1, 1, "no", "Sometimes", "Public_Transportation", "Overweight_Level_II"],
    ["Male", 24, 1.90, 86, "no", "yes", 3, 3, "Sometimes", "no", 3, "no", 2, 1, "no", "Sometimes", "Bike", "Normal_Weight"],
    ["Female", 28, 1.63, 69, "yes", "yes", 2, 3, "Sometimes", "no", 2, "no", 1, 1, "no", "Sometimes", "Public_Transportation", "Overweight_Level_I"],
]

HEADERS = [
    "Gender",
    "Age",
    "Height",
    "Weight",
    "family_history_with_overweight",
    "FAVC",
    "FCVC",
    "NCP",
    "CAEC",
    "SMOKE",
    "CH2O",
    "SCC",
    "FAF",
    "TUE",
    "CALC_BINARY",
    "CALC",
    "MTRANS",
    "NObeyesdad",
]


def ensure_dirs() -> None:
    for path in [RAW_DIR, STAGING_DIR, WAREHOUSE_DIR, MART_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def download_source() -> dict[str, str]:
    """Download the UCI zip and extract the CSV, with a reproducible fallback."""
    status = {
        "source_mode": "uci_download",
        "source_url": SOURCE_URL,
        "source_page": SOURCE_PAGE,
        "message": "Dataset descargado desde UCI.",
    }
    try:
        with urllib.request.urlopen(SOURCE_URL, timeout=20) as response:
            payload = response.read()
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            csv_name = next(name for name in archive.namelist() if name.lower().endswith(".csv"))
            RAW_CSV.write_bytes(archive.read(csv_name))
    except Exception as exc:  # pragma: no cover - depends on local network.
        status = {
            "source_mode": "fallback_sample",
            "source_url": SOURCE_URL,
            "source_page": SOURCE_PAGE,
            "message": f"No se pudo descargar UCI ({exc}). Se uso muestra local reproducible.",
        }
        with RAW_CSV.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS)
            writer.writerows(FALLBACK_ROWS)
    return status


def read_raw_csv() -> list[dict[str, str]]:
    with RAW_CSV.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        headers = next(reader)
        rows = []
        for values in reader:
            if len(values) == len(headers) + 1 and headers[-3:] == ["CALC", "MTRANS", "NObeyesdad"]:
                fixed_headers = headers[:14] + ["CALC_BINARY", "CALC", "MTRANS", "NObeyesdad"]
                rows.append(dict(zip(fixed_headers, values)))
            else:
                rows.append(dict(zip(headers, values)))
        return rows


def load_staging(rows: list[dict[str, str]]) -> None:
    with sqlite3.connect(STAGING_DB) as conn:
        conn.execute("DROP TABLE IF EXISTS raw_obesity")
        columns = ", ".join(f'"{name}" TEXT' for name in rows[0])
        conn.execute(f"CREATE TABLE raw_obesity ({columns})")
        placeholders = ", ".join("?" for _ in rows[0])
        quoted_cols = ", ".join(f'"{name}"' for name in rows[0])
        values = [[row.get(name, "") for name in rows[0]] for row in rows]
        conn.executemany(f"INSERT INTO raw_obesity ({quoted_cols}) VALUES ({placeholders})", values)


def as_float(value: str) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return math.nan


def normalize_yes_no(value: str) -> str:
    text = str(value).strip().lower()
    if text in {"yes", "si", "sí", "true", "1"}:
        return "Si"
    if text in {"no", "false", "0"}:
        return "No"
    return "No informado"


def age_group(age: float) -> str:
    if age < 20:
        return "Menor de 20"
    if age < 30:
        return "20-29"
    if age < 40:
        return "30-39"
    return "40+"


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Bajo peso"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Sobrepeso"
    return "Obesidad"


def frequency_score(value: str) -> float:
    mapping = {"no": 0, "sometimes": 1, "frequently": 2, "always": 3}
    return mapping.get(str(value).strip().lower(), 0)


def transform_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    curated = []
    for index, row in enumerate(rows, start=1):
        age = as_float(row.get("Age", ""))
        height = as_float(row.get("Height", ""))
        weight = as_float(row.get("Weight", ""))
        fcvc = as_float(row.get("FCVC", ""))
        ncp = as_float(row.get("NCP", ""))
        ch2o = as_float(row.get("CH2O", ""))
        faf = as_float(row.get("FAF", ""))
        tue = as_float(row.get("TUE", ""))
        bmi = weight / (height**2) if height and not math.isnan(height) else math.nan
        caloric_food = normalize_yes_no(row.get("FAVC", ""))
        family_history = normalize_yes_no(row.get("family_history_with_overweight", ""))
        caec_score = frequency_score(row.get("CAEC", ""))
        calc_score = frequency_score(row.get("CALC", ""))
        risk_score = round(
            (1 if caloric_food == "Si" else 0) * 2
            + caec_score
            + calc_score * 0.7
            + max(0, 3 - fcvc) * 0.8
            + max(0, 2 - ch2o) * 0.5
            + max(0, 2 - faf) * 0.9
            + max(0, tue - 1) * 0.3,
            2,
        )
        curated.append(
            {
                "person_id": index,
                "gender": row.get("Gender", "No informado"),
                "age": round(age, 2),
                "age_group": age_group(age),
                "height_m": round(height, 3),
                "weight_kg": round(weight, 2),
                "bmi": round(bmi, 2),
                "bmi_category": bmi_category(bmi),
                "family_history_overweight": family_history,
                "frequent_high_caloric_food": caloric_food,
                "vegetable_frequency": round(fcvc, 2),
                "main_meals": round(ncp, 2),
                "food_between_meals": row.get("CAEC", "No informado"),
                "smokes": normalize_yes_no(row.get("SMOKE", "")),
                "water_liters_score": round(ch2o, 2),
                "calorie_monitoring": normalize_yes_no(row.get("SCC", "")),
                "physical_activity_score": round(faf, 2),
                "technology_time_score": round(tue, 2),
                "alcohol_consumption": normalize_yes_no(row.get("CALC_BINARY", "")),
                "alcohol_frequency": row.get("CALC", "No informado"),
                "transportation": row.get("MTRANS", "No informado"),
                "obesity_level": row.get("NObeyesdad", row.get("NObesity", "No informado")),
                "habit_risk_score": risk_score,
            }
        )
    return curated


def load_warehouse(curated: list[dict[str, object]]) -> None:
    with sqlite3.connect(WAREHOUSE_DB) as conn:
        conn.execute("DROP TABLE IF EXISTS fact_obesity_habits")
        conn.execute(
            """
            CREATE TABLE fact_obesity_habits (
                person_id INTEGER PRIMARY KEY,
                gender TEXT,
                age REAL,
                age_group TEXT,
                height_m REAL,
                weight_kg REAL,
                bmi REAL,
                bmi_category TEXT,
                family_history_overweight TEXT,
                frequent_high_caloric_food TEXT,
                vegetable_frequency REAL,
                main_meals REAL,
                food_between_meals TEXT,
                smokes TEXT,
                water_liters_score REAL,
                calorie_monitoring TEXT,
                physical_activity_score REAL,
                technology_time_score REAL,
                alcohol_frequency TEXT,
                alcohol_consumption TEXT,
                transportation TEXT,
                obesity_level TEXT,
                habit_risk_score REAL
            )
            """
        )
        columns = list(curated[0].keys())
        placeholders = ", ".join("?" for _ in columns)
        conn.executemany(
            f"INSERT INTO fact_obesity_habits ({', '.join(columns)}) VALUES ({placeholders})",
            [[row[col] for col in columns] for row in curated],
        )


def average(values: list[float]) -> float:
    return round(sum(values) / len(values), 2) if values else 0


def grouped_average(rows: list[dict[str, object]], group_col: str, value_col: str) -> list[dict[str, object]]:
    groups: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        groups[str(row[group_col])].append(float(row[value_col]))
    return [{"label": key, "value": average(values)} for key, values in sorted(groups.items())]


def grouped_count(rows: list[dict[str, object]], col: str) -> list[dict[str, object]]:
    counts = Counter(str(row[col]) for row in rows)
    return [{"label": key, "value": value} for key, value in counts.most_common()]


def translate_value(value: object, mapping: dict[str, str]) -> str:
    text = str(value)
    return mapping.get(text, text.replace("_", " "))


GENDER_ES = {"Female": "Femenino", "Male": "Masculino"}
FREQUENCY_ES = {
    "no": "No",
    "Sometimes": "A veces",
    "Frequently": "Frecuentemente",
    "Always": "Siempre",
}
TRANSPORT_ES = {
    "Public_Transportation": "Transporte publico",
    "Automobile": "Automovil",
    "Walking": "Caminando",
    "Motorbike": "Motocicleta",
    "Bike": "Bicicleta",
}
OBESITY_LEVEL_ES = {
    "Insufficient_Weight": "Peso insuficiente",
    "Normal_Weight": "Peso normal",
    "Overweight_Level_I": "Sobrepeso nivel I",
    "Overweight_Level_II": "Sobrepeso nivel II",
    "Obesity_Type_I": "Obesidad tipo I",
    "Obesity_Type_II": "Obesidad tipo II",
    "Obesity_Type_III": "Obesidad tipo III",
}


def build_clean_scraping_table(curated: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return an easy-to-read table for the scraping/extraction deliverable."""
    return [
        {
            "id_persona": row["person_id"],
            "genero": translate_value(row["gender"], GENDER_ES),
            "edad": row["age"],
            "grupo_edad": row["age_group"],
            "estatura_m": row["height_m"],
            "peso_kg": row["weight_kg"],
            "imc": row["bmi"],
            "categoria_imc": row["bmi_category"],
            "antecedente_familiar_sobrepeso": row["family_history_overweight"],
            "consume_alimentos_altos_calorias": row["frequent_high_caloric_food"],
            "frecuencia_vegetales_1a3": row["vegetable_frequency"],
            "comidas_principales": row["main_meals"],
            "come_entre_comidas": translate_value(row["food_between_meals"], FREQUENCY_ES),
            "litros_agua_1a3": row["water_liters_score"],
            "monitorea_calorias": row["calorie_monitoring"],
            "actividad_fisica_0a3": row["physical_activity_score"],
            "tiempo_tecnologia_0a2": row["technology_time_score"],
            "frecuencia_alcohol": translate_value(row["alcohol_frequency"], FREQUENCY_ES),
            "transporte": translate_value(row["transportation"], TRANSPORT_ES),
            "nivel_obesidad_original": translate_value(row["obesity_level"], OBESITY_LEVEL_ES),
            "puntaje_riesgo_habitos": row["habit_risk_score"],
        }
        for row in curated
    ]


def write_markdown_preview(rows: list[dict[str, object]], limit: int = 30) -> None:
    preview = rows[:limit]
    headers = list(preview[0].keys())
    lines = [
        "# Tabla limpia obtenida del scraping",
        "",
        f"Vista previa de {len(preview)} filas. La tabla completa esta en `tabla_limpia_scraping.csv`.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in preview:
        values = [str(row[col]).replace("|", "/") for col in headers]
        lines.append("| " + " | ".join(values) + " |")
    SCRAPING_CLEAN_TABLE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_marts(curated: list[dict[str, object]], source_status: dict[str, str]) -> dict[str, object]:
    with CURATED_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(curated[0].keys()))
        writer.writeheader()
        writer.writerows(curated)

    clean_scraping_table = build_clean_scraping_table(curated)
    with SCRAPING_CLEAN_TABLE_CSV.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(clean_scraping_table[0].keys()))
        writer.writeheader()
        writer.writerows(clean_scraping_table)
    write_markdown_preview(clean_scraping_table)

    bmi_values = [float(row["bmi"]) for row in curated]
    risk_values = [float(row["habit_risk_score"]) for row in curated]
    dashboard = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_mode": source_status["source_mode"],
            "source_page": source_status["source_page"],
            "source_url": source_status["source_url"],
            "message": source_status["message"],
            "records": len(curated),
        },
        "kpis": {
            "records": len(curated),
            "avg_bmi": average(bmi_values),
            "avg_habit_risk_score": average(risk_values),
            "obesity_or_overweight_pct": round(
                sum(row["bmi_category"] in {"Sobrepeso", "Obesidad"} for row in curated) * 100 / len(curated),
                1,
            ),
            "avg_physical_activity": average([float(row["physical_activity_score"]) for row in curated]),
            "median_age": round(statistics.median(float(row["age"]) for row in curated), 1),
        },
        "charts": {
            "obesity_level": grouped_count(curated, "obesity_level"),
            "bmi_category": grouped_count(curated, "bmi_category"),
            "transportation": grouped_count(curated, "transportation"),
            "risk_by_age_group": grouped_average(curated, "age_group", "habit_risk_score"),
            "bmi_by_activity": grouped_average(curated, "physical_activity_score", "bmi"),
            "caloric_food": grouped_count(curated, "frequent_high_caloric_food"),
            "family_history": grouped_count(curated, "family_history_overweight"),
        },
        "sample": curated[:25],
    }
    DASHBOARD_JSON.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "pipeline_steps": [
            "Extraccion automatica desde UCI o muestra fallback.",
            "Carga a staging SQLite en raw_obesity.",
            "Limpieza de tipos, nulos, si/no, categorias e indicadores.",
            "Movimiento a warehouse SQLite en fact_obesity_habits.",
            "Publicacion de CSV curado y JSON para dashboard.",
        ],
        "outputs": {
            "raw_csv": str(RAW_CSV),
            "staging_db": str(STAGING_DB),
            "warehouse_db": str(WAREHOUSE_DB),
            "curated_csv": str(CURATED_CSV),
            "clean_scraping_table_csv": str(SCRAPING_CLEAN_TABLE_CSV),
            "clean_scraping_table_preview": str(SCRAPING_CLEAN_TABLE_MD),
            "dashboard_json": str(DASHBOARD_JSON),
        },
        "quality_checks": {
            "raw_rows": len(curated),
            "missing_bmi": sum(math.isnan(float(row["bmi"])) for row in curated),
            "duplicate_person_ids": len(curated) - len({row["person_id"] for row in curated}),
        },
        "source": source_status,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def run_pipeline() -> dict[str, object]:
    ensure_dirs()
    source_status = download_source()
    raw_rows = read_raw_csv()
    load_staging(raw_rows)
    curated = transform_rows(raw_rows)
    load_warehouse(curated)
    return write_marts(curated, source_status)


if __name__ == "__main__":
    result = run_pipeline()
    print(json.dumps(result, ensure_ascii=False, indent=2))
