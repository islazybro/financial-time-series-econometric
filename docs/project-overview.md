# Vision general del proyecto

## Contexto

El proyecto original fue elaborado en R como trabajo final de econometria. Esta version en Python no solo migra el analisis, sino que lo reorganiza como un repositorio reproducible y legible para GitHub.

## Objetivo general

Analizar econometricamente las series de tiempo financieras de BBVA y Santander para estudiar:

- estacionariedad,
- dinamica de la media,
- volatilidad condicional,
- relacion dinamica entre ambas series.

## Componentes metodologicos

- Precio ajustado (`Adj Close`) para el analisis descriptivo y las visualizaciones.
- **Log-precio** para la estacionariedad y el modelo ARIMA de la media.
- **Log-rendimiento** para volatilidad (ARCH-LM/GARCH) y analisis multivariado (VAR).
- Estacionariedad con **ADF + KPSS** (hipotesis nulas complementarias).
- ARIMA con `d` por ADF y `p`/`q` por AIC/BIC.
- GARCH condicional a la evidencia de efectos ARCH.
- VAR con diagnostico de estabilidad y residuos, Granger e impulso-respuesta Cholesky con intervalos al 95%.

## Aporte de esta version

La mejora principal no es solo el cambio de lenguaje. Tambien se corrigen problemas comunes de proyectos academicos:

- rutas dependientes de una computadora,
- codigo mezclado con interpretacion en un solo archivo,
- poca modularidad,
- baja reproducibilidad,
- explicacion econometrica insuficiente.

## Enfoque didactico

Esta version adopta una idea central util para aprender econometria: primero una aplicacion concreta y despues la teoria necesaria para entenderla. El repositorio no solo busca correr modelos, sino explicar por que cada prueba y cada especificacion tiene sentido dentro del problema financiero estudiado.

## Enfoque tecnico

El repositorio integra tres componentes principales:

1. Implementacion modular en Python.
2. Aplicacion econometrica justificada, no solo ejecucion de funciones.
3. Comunicacion clara del razonamiento y los resultados.
