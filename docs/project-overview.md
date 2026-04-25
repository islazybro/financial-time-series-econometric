# Vision general del proyecto

## Contexto

El proyecto original fue elaborado en R como trabajo final de econometria. Esta nueva version en Python no solo migra el analisis, sino que lo reorganiza como un repositorio reproducible y legible para GitHub.

## Objetivo general

Analizar econometricamente las series de tiempo financieras de BBVA y Santander para estudiar:

- estacionariedad,
- dinamica de corto plazo,
- volatilidad condicional,
- relacion dinamica entre ambas series.

## Aporte de esta version

La mejora principal no es solo el cambio de lenguaje. Tambien se corrigen problemas comunes de proyectos academicos:

- rutas absolutas dependientes de una computadora,
- codigo mezclado con interpretacion en un solo archivo,
- poca modularidad,
- baja reproducibilidad,
- explicacion econometrica insuficiente.

## Enfoque didactico

Esta version adopta una idea central muy util para aprender econometria: primero una aplicacion concreta y despues la teoria necesaria para entenderla. En otras palabras, el repositorio no solo busca correr modelos, sino explicar por que cada prueba y cada especificacion tiene sentido dentro del problema financiero estudiado.

## Enfoque tecnico

Este repositorio integra tres componentes principales:

1. Implementacion modular en Python.
2. Aplicacion econometrica justificada, no solo ejecucion de funciones.
3. Comunicacion clara del razonamiento y los resultados.
