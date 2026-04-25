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

## Que cubren las pruebas

- Lectura de CSV con columnas en espanol.
- Lectura de CSV con columnas en ingles.
- Calculo de rendimientos logaritmicos.
- Alineacion de fechas entre series.
- Validacion de archivos limpios.
- Deteccion de filas no numericas o encabezados extra.

Estas pruebas no buscan validar toda la teoria econometrica. Su objetivo es proteger las piezas de preparacion de datos, que son la base del resto del analisis.
