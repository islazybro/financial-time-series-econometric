# Interpretacion inicial de resultados

Este documento resume la primera lectura econometrica del analisis generado por `scripts/run_analysis.py`.

> Nota: esta interpretacion corresponde a la ejecucion anterior con `BBVA.MX` y `SAN.MC`. El proyecto ya fue ajustado para usar `BBVA.MC` y `SAN.MC`; por lo tanto, este documento debe actualizarse despues de volver a descargar datos y correr el analisis.

## Datos analizados

La ejecucion actual usa precios mensuales descargados desde Yahoo Finance segun `config/data_sources.json`.

Configuracion de la ejecucion interpretada:

- BBVA: `BBVA.MX`
- Santander: `SAN.MC`
- periodo: 2019-01-01 a 2026-01-01
- frecuencia: mensual

Antes de cerrar conclusiones, conviene regenerar resultados con la configuracion actual documentada en `docs/market-selection.md`.

## Estacionariedad

La prueba ADF en niveles arroja p-valores cercanos a 1.0000 para ambas series. Esto indica que no se rechaza la hipotesis nula de raiz unitaria, por lo que los precios en niveles no parecen estacionarios.

En cambio, los rendimientos logaritmicos tienen p-valores practicamente iguales a cero. Esto sugiere que los rendimientos si son estacionarios y que son una transformacion adecuada para modelos de volatilidad y VAR.

Lectura economica:

- Los precios financieros suelen moverse con tendencias y choques persistentes.
- Los rendimientos suelen tener media mas estable, por eso son preferibles para modelar relaciones dinamicas.

## Modelo ARIMA

El modelo seleccionado por AIC para ambas series fue:

```text
ARIMA(0, 2, 1)
```

Esto sugiere que, dentro de la grilla probada, la dinamica de la media se describe mejor con una serie integrada de segundo orden y un componente de media movil.

Lectura para el proyecto:

- El resultado confirma que trabajar directamente con precios requiere diferenciar.
- La seleccion por AIC favorece una especificacion relativamente parsimoniosa.
- Para una version final, puede compararse este resultado con un modelo sobre log-precios o rendimientos.

## Heterocedasticidad y GARCH

Los p-valores ARCH-LM fueron mayores a 0.05:

- BBVA: 0.3285
- Santander: 0.3945

Con esta evidencia no se rechaza la hipotesis de ausencia de efectos ARCH remanentes en los residuos del ARIMA.

El modelo GARCH(1,1) muestra parametros beta cercanos a 1:

- BBVA beta(1): 0.9924
- Santander beta(1): 0.9881

Lectura economica:

- La volatilidad estimada muestra alta persistencia.
- Los choques de volatilidad tienden a disiparse lentamente.
- Aun asi, la prueba ARCH-LM no muestra evidencia fuerte de heterocedasticidad remanente bajo esta especificacion.

## Modelo VAR

El VAR selecciono un rezago:

```text
VAR(1)
```

Los pronosticos de rendimientos convergen hacia valores relativamente estables. Esto es consistente con series de rendimientos estacionarias, donde el modelo no proyecta tendencias explosivas.

## Causalidad de Granger

Los p-valores de causalidad de Granger fueron:

- BBVA -> Santander: 0.7197
- Santander -> BBVA: 0.6271

Como ambos p-valores son mayores a 0.05, no se encuentra evidencia estadistica de causalidad de Granger entre las series.

Interpretacion correcta:

- No significa que las empresas no esten relacionadas.
- Significa que, con estos datos, frecuencia y rezagos, los valores pasados de una serie no agregan informacion predictiva estadisticamente significativa sobre la otra.

## Impulso-respuesta

Las funciones impulso-respuesta muestran efectos que se reducen rapidamente hacia cero. Esto sugiere que los choques tienen impacto transitorio dentro del sistema VAR.

Lectura economica:

- El sistema parece estable.
- Los choques no generan efectos persistentes de largo plazo en los rendimientos.
- La interaccion dinamica existe en magnitud pequena, pero no alcanza evidencia fuerte mediante Granger.

## Conclusion preliminar

El analisis muestra un patron comun en series financieras:

- precios no estacionarios;
- rendimientos estacionarios;
- volatilidad persistente;
- ausencia de causalidad de Granger significativa;
- choques con efectos transitorios.

Para fortalecer el proyecto final, la configuracion fue ajustada a `BBVA.MC` y `SAN.MC`. El siguiente paso es regenerar resultados con esos tickers y actualizar esta interpretacion con la nueva salida.
