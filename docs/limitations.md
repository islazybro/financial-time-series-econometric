# Limitaciones y alcance

Este proyecto tiene fines academicos y educativos. No constituye recomendacion de inversion ni asesoria financiera.

## Alcance del analisis

El objetivo es mostrar un flujo econometrico reproducible aplicado a series financieras:

- descarga y validacion de datos;
- pruebas de estacionariedad;
- modelado ARIMA;
- modelado GARCH;
- modelo VAR;
- causalidad de Granger;
- impulso-respuesta;
- visualizaciones e interpretacion.

## Limitaciones metodologicas

- La frecuencia mensual reduce ruido, pero tambien elimina informacion diaria relevante.
- La muestra contiene 84 observaciones, suficiente para un ejercicio aplicado, pero limitada para conclusiones fuertes.
- Los modelos ARIMA, GARCH y VAR son sensibles a especificacion, rezagos, periodo muestral y transformaciones.
- La ausencia de causalidad de Granger no implica ausencia de relacion economica entre empresas.
- Los resultados pueden cambiar si se modifica el periodo, la frecuencia, los tickers o la fuente de datos.
- El analisis no incorpora variables macroeconomicas, fundamentales financieros ni eventos corporativos.

## Limitaciones de datos

Los precios se descargan desde Yahoo Finance mediante `yfinance`. Esto facilita la reproducibilidad, pero depende de la disponibilidad y consistencia de la fuente externa.

Por esa razon, el proyecto incluye:

- archivo de configuracion de tickers;
- script de validacion de datos;
- documentacion sobre seleccion de mercado;
- advertencias sobre archivos con filas descartadas.

## Uso correcto de los resultados

Los resultados deben interpretarse como evidencia estadistica dentro de una especificacion concreta. No deben usarse para decidir compras o ventas de activos financieros.

La contribucion principal del proyecto es demostrar un proceso ordenado de analisis econometrico y comunicacion tecnica.
