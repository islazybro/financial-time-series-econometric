# Pruebas y checks

El proyecto incluye pruebas basicas para verificar que la carga de datos y la validacion funcionen correctamente.

## Instalar dependencias de desarrollo

```bash
pip install -e ".[dev]"
```

## Ejecutar pruebas

```bash
pytest
```

## GitHub Actions

El repositorio incluye un workflow en:

```text
.github/workflows/tests.yml
```

Cada `push` y cada `pull request` ejecuta:

```bash
python -m pip install -e ".[dev]"
pytest
```

Si las pruebas pasan, GitHub muestra el estado correcto en la pestana `Actions` y en el badge del README.

## Que cubren las pruebas

- Lectura de CSV con columnas en espanol.
- Lectura de CSV con columnas en ingles.
- Calculo de rendimientos logaritmicos.
- Alineacion de fechas entre series.
- Validacion de archivos limpios.
- Deteccion de filas no numericas o encabezados extra.

Estas pruebas no buscan validar toda la teoria econometrica. Su objetivo es proteger las piezas de preparacion de datos, que son la base del resto del analisis.
