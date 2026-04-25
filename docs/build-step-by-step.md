# Construccion paso a paso

Este archivo sirve como mapa de trabajo para construir el proyecto sin perdernos. La idea es avanzar por etapas pequenas, comprobar que cada una funciona y corregir los problemas en el momento en que aparezcan.

## Paso 1. Estructura del repositorio

Objetivo: que el proyecto tenga forma profesional antes de crecer.

Archivos principales:

- `README.md`: portada del proyecto.
- `pyproject.toml`: dependencias y configuracion instalable.
- `src/econometria_financiera/`: codigo reutilizable.
- `scripts/`: comandos para ejecutar el analisis.
- `docs/`: explicaciones para GitHub, CV y metodologia.
- `data/raw/`: datos originales.
- `outputs/`: resultados generados.

Estado: completado.

## Paso 2. Entorno de Python

Objetivo: instalar librerias y verificar que el proyecto corre.

Comandos:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Verificacion:

```bash
python scripts/generate_demo_data.py
python scripts/run_analysis.py
```

Estado: probado con datos demo.

## Paso 3. Datos

Objetivo: reemplazar datos demo por datos reales.

Archivos esperados:

- `data/raw/BBVA.csv`
- `data/raw/SAN.csv`

Columnas aceptadas:

- Fecha: `Fecha` o `Date`
- Cierre: `Cierre`, `Close`, `Adj Close` o `Precio`

Estado: pendiente de conectar los CSV reales.

Guia detallada:

- `docs/data-step.md`

Comando de validacion:

```bash
python scripts/validate_data.py
```

## Paso 4. Analisis univariado

Objetivo: estudiar cada activo por separado.

Componentes:

- prueba ADF en niveles;
- prueba ADF en rendimientos;
- seleccion ARIMA por AIC;
- prueba ARCH sobre residuos.

Archivo principal:

- `src/econometria_financiera/univariate.py`

Estado: completado.

## Paso 5. Volatilidad

Objetivo: modelar la varianza condicional de los rendimientos.

Modelo base:

- GARCH(1,1)

Archivo principal:

- `src/econometria_financiera/volatility.py`

Estado: completado.

## Paso 6. Analisis multivariado

Objetivo: estudiar la relacion dinamica entre BBVA y Santander.

Componentes:

- VAR;
- seleccion de rezagos;
- pronostico;
- causalidad de Granger;
- impulso-respuesta.

Archivo principal:

- `src/econometria_financiera/multivariate.py`

Estado: completado.

## Paso 7. Reporte

Objetivo: convertir salidas tecnicas en una explicacion entendible.

Salida principal:

- `outputs/analysis_report.md`

Estado: completado con datos demo.

## Paso 8. Pulido para portafolio

Objetivo: que el repositorio sea claro para una persona que lo vea en GitHub.

Documentos utiles:

- `docs/project-overview.md`
- `docs/methodology.md`
- `docs/github-showcase.md`
- `docs/cv-project-entry.md`
- `docs/references.md`

Estado: iniciado.

## Siguiente bloque recomendado

El siguiente paso natural es reemplazar los datos demo por los CSV reales y revisar si cambian los resultados. Si aparece un error, se resuelve en esta secuencia:

1. confirmar nombres de columnas;
2. confirmar formato de fechas;
3. confirmar que no haya precios vacios o texto en la columna de cierre;
4. ejecutar `scripts/run_analysis.py`;
5. revisar `outputs/analysis_report.md`.
