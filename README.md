# Weight Loss Data Pipeline

Pipeline de ingeniería de datos enfocado en el análisis de hábitos alimenticios, actividad física y variables relacionadas con el peso corporal y los niveles de obesidad.

El proyecto implementa un proceso ETL completo (**Extract, Transform, Load**), incluyendo extracción de datos, limpieza, transformación, almacenamiento en SQLite y visualización mediante un dashboard web interactivo.

---

## Objetivo del proyecto

Analizar cómo los hábitos alimenticios, la actividad física y otras variables influyen en el peso corporal y los niveles de obesidad utilizando un pipeline de ingeniería de datos.

El proyecto busca simular un entorno real de procesamiento de datos, aplicando técnicas de:

- extracción,
- limpieza,
- transformación,
- almacenamiento,
- análisis,
- y visualización de datos.

---

## Fuente de datos

Dataset público obtenido desde:

- https://archive.ics.uci.edu

Dataset utilizado:

**Estimation of Obesity Levels Based On Eating Habits and Physical Condition**

Características del dataset:

- 2.111 registros
- 17 atributos originales
- Datos de personas de Colombia, Perú y México
- Variables relacionadas con alimentación, actividad física, hábitos diarios y obesidad

---

## Variables analizadas

Algunas variables utilizadas en el proyecto:

- Edad
- Género
- Peso
- Altura
- Frecuencia de actividad física
- Consumo de agua
- Consumo de alimentos altos en calorías
- Uso de tecnología
- Número de comidas diarias
- Consumo de alcohol
- Medio de transporte
- Nivel de obesidad

---

## Tecnologías utilizadas

- Python
- SQLite
- CSV
- JSON
- HTML
- CSS
- JavaScript
- Git
- GitHub
- GitHub Pages

El pipeline está construido con librerías estándar de Python, por lo que no requiere instalar Pandas, NumPy, Streamlit ni Dash para ejecutarse.

---

## Arquitectura del pipeline

El pipeline implementa las siguientes etapas:

1. Extracción de datos desde UCI
2. Carga cruda en zona `raw`
3. Staging en SQLite
4. Limpieza de datos
5. Transformación de variables
6. Carga al warehouse SQLite
7. Generación de data marts
8. Visualización en dashboard

Flujo general:

```text
UCI ZIP/CSV -> data/raw -> SQLite staging -> SQLite warehouse -> data/mart -> dashboard
```

---

## Estructura del proyecto

```bash
├── dashboard/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── server.py
├── data/
│   ├── raw/
│   ├── staging/
│   ├── warehouse/
│   └── mart/
├── notebooks/
├── scripts/
│   └── run_pipeline.py
├── index.html
├── TUTORIAL.md
├── README.md
└── LICENSE
```

---

## Entregables

### `notebooks/cuaderno_trabajo.ipynb`

Cuaderno principal con:

- explicación del tema,
- origen de los datos,
- proceso de limpieza,
- transformación de datos,
- movimiento entre capas,
- resultados,
- y reflexión del pipeline.

### `dashboard/`

Dashboard web interactivo con:

- métricas principales,
- gráficos,
- indicadores,
- tabla de muestra,
- y análisis visual de resultados.

### `scripts/run_pipeline.py`

Script principal encargado de ejecutar automáticamente:

- extracción,
- staging,
- limpieza,
- transformación,
- carga al warehouse,
- y generación de data marts.

### `data/mart/tabla_limpia_scraping.csv`

Tabla final limpia y transformada, lista para análisis.

### `data/mart/tabla_limpia_scraping.md`

Vista previa rápida de la tabla procesada.

### `TUTORIAL.md`

Guía paso a paso para:

- ejecutar el proyecto,
- entender el pipeline,
- y explicar la actividad.

---

## Proceso ETL

### Extracción (Extract)

Los datos se descargan automáticamente desde UCI Machine Learning Repository.

El sistema también cuenta con una muestra local de respaldo en caso de no tener conexión a internet.

### Limpieza (Transform - Cleaning)

Durante la limpieza se realizaron procesos como:

- corrección de formatos,
- conversión de variables numéricas,
- normalización de variables `yes/no`,
- validación de registros,
- cálculo de IMC,
- generación de categorías,
- y estandarización de columnas para la tabla limpia.

### Transformación (Transform)

Se realizaron transformaciones para facilitar el análisis:

- cálculo del IMC,
- clasificación en categorías de IMC,
- agrupación por rangos de edad,
- generación de estadísticas,
- creación del puntaje `habit_risk_score`,
- traducción de categorías para la tabla limpia,
- y generación de datos agregados para el dashboard.

Ejemplo de fórmula utilizada:

```text
IMC = peso / altura²
```

### Carga (Load)

Los datos procesados se almacenan en:

- archivos CSV,
- base SQLite de staging,
- base SQLite de warehouse,
- archivos JSON para visualización,
- y data marts listos para análisis.

---

## Dashboard

Dashboard disponible en:

https://mariana-gutierrez-r.github.io/weight-loss-data-pipeline/dashboard/

El dashboard permite visualizar:

- distribución de obesidad,
- categorías de IMC,
- riesgo promedio por grupo de edad,
- medio de transporte,
- métricas generales,
- y muestra de datos transformados.

---

## Ejecución rápida

### Ejecutar pipeline

```bash
python scripts/run_pipeline.py
```

### Ejecutar dashboard local

```bash
python dashboard/server.py
```

Luego abrir en el navegador:

```text
http://127.0.0.1:8000
```

---

## Resultados obtenidos

El análisis permitió identificar relaciones importantes entre:

- hábitos alimenticios,
- actividad física,
- consumo de agua,
- tiempo de uso de tecnología,
- medio de transporte,
- y niveles de obesidad.

También se observó que las personas con mejores hábitos saludables tienden a presentar menores niveles de riesgo en los indicadores calculados.

---

## Aprendizajes obtenidos

Durante el desarrollo del proyecto se aprendió:

- cómo construir un pipeline ETL,
- cómo limpiar y transformar datos,
- cómo automatizar procesos,
- cómo organizar datos por capas,
- cómo cargar datos en SQLite,
- cómo generar data marts,
- y cómo visualizar resultados mediante dashboards.

Además, se comprendió la importancia de la calidad de los datos para obtener análisis confiables.

---

## Funcionamiento sin internet

Si el sistema no tiene conexión a internet, el proyecto utiliza automáticamente una muestra local de respaldo para garantizar el funcionamiento completo del pipeline.

---

## Autor

Mariana Gutierrez Restrepo

Proyecto académico de Ingeniería de Datos.
