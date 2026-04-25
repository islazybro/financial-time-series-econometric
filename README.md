# Proyecto Final de Econometria en Python

Este repositorio rehace desde cero, en Python y con mejor estructura, un proyecto de series de tiempo financieras que originalmente fue desarrollado en R. El objetivo es que funcione tanto como evidencia tecnica para CV y GitHub como material de estudio para entender cada paso del analisis.

## Pregunta de investigacion

Se estudian las series de precios de cierre de **BBVA** y **Banco Santander** para responder cuatro preguntas:

1. Las series son estacionarias en niveles o requieren transformacion.
2. Que modelo describe mejor la dinamica de la media de cada serie.
3. Existe evidencia de volatilidad condicional en los rendimientos.
4. Hay interaccion dinamica entre ambas acciones mediante un modelo VAR.

## Metodologia

El flujo del proyecto sigue esta secuencia:

1. Carga y limpieza de datos.
2. Analisis exploratorio.
3. Pruebas ADF de raiz unitaria.
4. Modelado ARIMA para la media.
5. Pruebas ARCH y modelos GARCH para volatilidad.
6. Modelo VAR sobre rendimientos.
7. Causalidad de Granger, impulso-respuesta y pronosticos.

Para construirlo y revisarlo por etapas, consulta `docs/build-step-by-step.md`.

## Estructura del repositorio

```text
.
|-- README.md
|-- pyproject.toml
|-- data
|   |-- raw
|   |   |-- README.md
|   |   |-- BBVA.csv.example
|   |   `-- SAN.csv.example
|   `-- processed
|-- docs
|   |-- methodology.md
|   `-- project-overview.md
|-- outputs
|-- scripts
|   |-- generate_demo_data.py
|   `-- run_analysis.py
`-- src
    `-- econometria_financiera
        |-- __init__.py
        |-- data.py
        |-- multivariate.py
        |-- reporting.py
        |-- univariate.py
        `-- volatility.py
```

## Requisitos

Este proyecto usa Python 3.11+ y las bibliotecas:

- `pandas`
- `numpy`
- `statsmodels`
- `arch`
- `matplotlib`

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Datos

Coloca tus archivos en `data/raw/` con los nombres:

- `BBVA.csv`
- `SAN.csv`

El codigo acepta columnas con nombres como `Fecha`, `Date`, `Cierre`, `Close`, `Adj Close` o `Precio`.

Antes de ejecutar el analisis con datos reales, valida los archivos:

```bash
python scripts/validate_data.py
```

La guia completa de datos esta en `docs/data-step.md`.

Si todavia no tienes datos, puedes generar un ejemplo reproducible:

```bash
python scripts/generate_demo_data.py
```

## Ejecucion

```bash
python scripts/run_analysis.py
```

Los resultados se guardan en `outputs/`:

- `analysis_report.md`
- `univariate_summary.csv`
- `var_forecast.csv`
- `series_preview.csv`

## Valor para portafolio

Este proyecto busca mostrar:

- Capacidad para traducir analisis econometrico a codigo reproducible.
- Dominio conceptual de series de tiempo.
- Buenas practicas de documentacion y estructura.
- Comunicacion tecnica clara para GitHub.

## Habilidades que demuestra

- Python para analisis de datos.
- Series de tiempo financieras.
- Econometria aplicada.
- Modelado ARIMA, GARCH y VAR.
- Limpieza y preparacion de datos.
- Documentacion tecnica para proyectos reproducibles.

## Como contarlo en GitHub

Una forma clara de presentarlo es:

> Reimplementacion en Python de un proyecto de econometria financiera originalmente desarrollado en R. El repositorio analiza precios de BBVA y Santander mediante pruebas ADF, modelos ARIMA, GARCH y VAR, con una estructura reproducible, documentacion clara y enfoque en interpretacion economica.

Tambien puedes usar el archivo `docs/cv-project-entry.md` para adaptar la descripcion a tu CV o LinkedIn.

Si es tu primera vez subiendo un proyecto, empieza con `docs/github-first-steps.md`.

## Siguientes mejoras sugeridas

- Agregar notebook explicativo con visualizaciones.
- Incorporar pruebas unitarias.
- Descargar precios desde una API financiera.
- Publicar resultados y graficas con GitHub Pages.
