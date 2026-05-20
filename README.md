# Pipeline de datos: hábitos alimenticios y peso

Este proyecto entrega una simulación completa de ingeniería de datos para analizar cómo los hábitos alimenticios, la actividad física y otras variables se relacionan con el peso y los niveles de obesidad.

Fuente principal: dataset público de UCI Machine Learning Repository, **Estimation of Obesity Levels Based On Eating Habits and Physical Condition**. La página de UCI indica que contiene 2.111 registros, 17 atributos y personas de México, Perú y Colombia.

## Entregables

- `notebooks/cuaderno_trabajo.ipynb`: cuaderno detallado en español.
- `dashboard/`: dashboard web local con actualización automática del pipeline.
- `scripts/run_pipeline.py`: extracción, staging, limpieza, transformación, warehouse y marts.
- `data/mart/tabla_limpia_scraping.csv`: tabla limpia final obtenida desde la extracción/scraping.
- `data/mart/tabla_limpia_scraping.md`: vista previa de la tabla limpia para revisar rápido.
- `TUTORIAL.md`: guía paso a paso para ejecutar y explicar el proyecto.

## Ejecución rápida

```powershell
python scripts/run_pipeline.py
python dashboard/server.py
```

Luego abre:

```text
http://127.0.0.1:8000
```

El servidor intenta descargar automáticamente el dataset desde UCI. Si el equipo no tiene internet, usa una muestra local de respaldo para que la actividad pueda revisarse de todas formas.
