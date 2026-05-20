# Tutorial del pipeline de ingeniería de datos

## 1. Tema elegido

El tema es el análisis de hábitos alimenticios, actividad física y niveles de peso. Se eligió porque permite simular un flujo real de ingeniería de datos: extracción desde una fuente pública, limpieza, carga en base de datos, transformación, generación de indicadores y publicación en un dashboard.

La fuente principal es UCI Machine Learning Repository: `Estimation of Obesity Levels Based On Eating Habits and Physical Condition`.

## 2. Cómo obtener los datos

Ejecuta:

```powershell
python scripts/run_pipeline.py
```

El script descarga automáticamente un archivo ZIP desde UCI, extrae el CSV y lo guarda en:

```text
data/raw/obesity_source.csv
```

Si no hay conexión a internet, el script crea una muestra local documentada. Esto permite demostrar el pipeline sin depender de la red.

## 3. Limpieza y organización

El pipeline realiza estas acciones:

- Convierte edad, estatura, peso, consumo de vegetales, agua, actividad física y uso de tecnología a valores numéricos.
- Normaliza variables de texto como `yes/no` a `Si/No`.
- Calcula el IMC usando `peso / estatura^2`.
- Crea categorías de IMC: bajo peso, normal, sobrepeso y obesidad.
- Agrupa edades en rangos.
- Calcula un indicador educativo llamado `habit_risk_score`, que resume señales de hábitos de mayor riesgo.
- Genera una tabla limpia en español para entregar el resultado del scraping.

La tabla limpia queda en:

```text
data/mart/tabla_limpia_scraping.csv
```

También se genera una vista previa en Markdown:

```text
data/mart/tabla_limpia_scraping.md
```

## 4. Movimiento entre sistemas

El flujo mueve datos por tres capas:

```text
CSV crudo -> SQLite staging -> SQLite warehouse -> JSON/CSV para dashboard
```

Archivos principales:

- `data/staging/obesity_staging.db`: tabla `raw_obesity`.
- `data/warehouse/obesity_warehouse.db`: tabla `fact_obesity_habits`.
- `data/mart/dashboard_data.json`: datos agregados para visualización.
- `data/mart/obesity_curated.csv`: dataset limpio y transformado.
- `data/mart/tabla_limpia_scraping.csv`: tabla limpia con nombres de columnas en español.

## 5. Transformaciones realizadas

Las transformaciones agregan columnas útiles para análisis:

- `bmi`: índice de masa corporal.
- `bmi_category`: categoría calculada de IMC.
- `age_group`: rango de edad.
- `habit_risk_score`: puntaje de hábitos alimenticios y estilo de vida.
- Variables normalizadas de consumo calórico, antecedentes familiares, tabaquismo y monitoreo de calorías.

## 6. Desplegar el dashboard

Ejecuta:

```powershell
python dashboard/server.py
```

Abre en el navegador:

```text
http://127.0.0.1:8000
```

El dashboard muestra:

- Total de registros.
- IMC promedio.
- Porcentaje de personas con sobrepeso u obesidad.
- Riesgo promedio de hábitos.
- Distribución por nivel de obesidad.
- Categorías de IMC calculado.
- Riesgo promedio por grupo de edad.
- Medio de transporte.
- Muestra de datos transformados.

El botón `Actualizar datos` vuelve a ejecutar el pipeline, intenta descargar otra vez el dataset y actualiza las visualizaciones.

## 7. Qué se aprendió

Este proyecto muestra que un pipeline no es solo leer un archivo. Es necesario separar capas, documentar la fuente, controlar errores de descarga, limpiar tipos de datos, transformar variables para análisis, mover datos entre sistemas y publicar resultados comprensibles para usuarios finales.
