# Metodologia

## 1. Preparacion de datos

Se leen dos series de precios de cierre, una para BBVA y otra para Santander. El pipeline estandariza nombres de columnas, convierte fechas y ordena las observaciones cronologicamente.

## 2. Transformaciones

Se trabaja con dos representaciones:

- precios en niveles, utiles para diagnostico inicial y modelado ARIMA;
- rendimientos logaritmicos, utiles para estacionariedad, volatilidad y VAR.

La formula usada es:

```text
r_t = log(P_t / P_{t-1})
```

## 3. Estacionariedad

La prueba ADF evalua la hipotesis nula de raiz unitaria.

- Si no se rechaza la hipotesis nula en niveles, la serie se considera no estacionaria.
- Si se rechaza en rendimientos o diferencias, la transformacion logra estacionariedad.

## 4. Modelo ARIMA

ARIMA modela la dinamica de la media mediante componentes:

- autorregresivos (AR),
- integrados (I),
- de medias moviles (MA).

En este proyecto se prueba una pequena grilla de modelos y se selecciona el de menor AIC entre los candidatos estables y estimables.

## 5. Efectos ARCH y modelo GARCH

Las series financieras suelen mostrar volatilidad agrupada. Para evaluar esto:

1. se ajusta un modelo para la media;
2. se aplican pruebas ARCH sobre los residuos;
3. se estima un modelo GARCH(1,1) para la varianza condicional.

La ecuacion de volatilidad tiene la forma:

```text
sigma_t^2 = omega + alpha * e_{t-1}^2 + beta * sigma_{t-1}^2
```

## 6. Modelo VAR

Sobre los rendimientos de ambas acciones se estima un VAR para capturar interdependencia dinamica. A partir de este modelo se obtienen:

- seleccion de rezagos,
- pronosticos multivariados,
- pruebas de causalidad de Granger,
- funciones impulso-respuesta.

## 7. Interpretacion

La meta no es solo obtener salidas del software, sino traducirlas a lenguaje economico:

- si una serie tiene raiz unitaria,
- si existe persistencia en la volatilidad,
- si un activo ayuda a predecir al otro,
- y si los choques se transmiten de forma duradera o transitoria.
