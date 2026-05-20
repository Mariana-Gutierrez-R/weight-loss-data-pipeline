# Pipeline de datos: habitos alimenticios y peso

Este proyecto entrega una simulacion completa de ingenieria de datos para analizar como los habitos alimenticios, la actividad fisica y otras variables se relacionan con el peso y los niveles de obesidad.

Fuente principal: dataset publico de UCI Machine Learning Repository, **Estimation of Obesity Levels Based On Eating Habits and Physical Condition**. La pagina de UCI indica que contiene 2.111 registros, 17 atributos y personas de Mexico, Peru y Colombia.

## Entregables

- `notebooks/cuaderno_trabajo.ipynb`: cuaderno detallado en espanol.
- `dashboard/`: dashboard web local con actualizacion automatica del pipeline.
- `scripts/run_pipeline.py`: extraccion, staging, limpieza, transformacion, warehouse y marts.
- `data/mart/tabla_limpia_scraping.csv`: tabla limpia final obtenida desde la extraccion/scraping.
- `data/mart/tabla_limpia_scraping.md`: vista previa de la tabla limpia para revisar rapido.
- `TUTORIAL.md`: guia paso a paso para ejecutar y explicar el proyecto.

## Ejecucion rapida

```powershell
python scripts/run_pipeline.py
python dashboard/server.py
```

Luego abre:

```text
http://127.0.0.1:8000
```

El servidor intenta descargar automaticamente el dataset desde UCI. Si el equipo no tiene internet, usa una muestra local de respaldo para que la actividad pueda revisarse de todas formas.
