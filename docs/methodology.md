# Metodologia

## 1. Preparacion de datos

Se leen dos series de precios ajustados (`Adj Close`) desde los CSV definidos en `config/data_sources.json`. El pipeline estandariza nombres de columnas, convierte fechas, ordena cronologicamente, elimina duplicados y valida que los precios sean positivos y la muestra suficiente.

La separacion conceptual es:

```text
precio ajustado (Adj Close)  -> analisis descriptivo y visualizacion
log-precio = log(precio)     -> estacionariedad y modelo ARIMA de la media
log-rendimiento = dlog(precio) -> volatilidad y modelos VAR
```

## 2. Transformaciones

- `log-precio` (`r_t = log(P_t)`): se usa para pruebas de raiz unitaria y para el ARIMA de la media.
- `log-rendimiento` (`r_t = log(P_t / P_{t-1})`): se usa para volatilidad y analisis multivariado.

## 3. Estacionariedad: ADF y KPSS

Se aplican dos pruebas complementarias, con hipotesis nulas distintas:

- **ADF**: H0 = la serie tiene raiz unitaria (no estacionaria). Rechazar H0 sugiere estacionariedad.
- **KPSS**: H0 = la serie es estacionaria. Rechazar H0 sugiere no estacionariedad.

Se aplican a:

1. log-precio (niveles);
2. log-rendimientos (primera diferencia del log-precio).

ADF se usa para fijar el orden de integracion `d` (se diferencia hasta rechazar la raiz unitaria). Cuando ADF y KPSS discrepan, se reportan ambas evidencias sin forzar una clasificacion automatica.

## 4. Modelo ARIMA (sobre log-precio)

ARIMA modela la dinamica de la media mediante componentes autorregresivos (AR), integrados (I) y de medias moviles (MA).

- El orden de diferenciacion `d` se determina por ADF. No se elige por AIC porque el AIC no es comparable entre grados de diferenciacion (cambia el dato modelado).
- Con `d` fijo, `p` y `q` se seleccionan minimizando **AIC** en una grilla pequena; se reporta tambien **BIC**.
- Despues de estimar, se revisan los residuos con ACF y **Ljung-Box**.
- El pronostico se genera en log-precio y se transforma de nuevo a precio con `exp()`. No se comparan AIC entre representaciones distintas (precio bruto vs log-precio).

## 5. Comparativo de rendimientos

Se comparan los log-rendimientos mediante estadisticos descriptivos (media, volatilidad, minimo, maximo) y su correlacion contemporanea. Es un bloque descriptivo, previo al VAR.

## 6. Efectos ARCH y modelo GARCH

1. Se ajusta un modelo de media constante sobre log-rendimientos.
2. Se aplica **ARCH-LM** sobre los residuos de ese modelo de media (consistente con la media del GARCH).
3. Se estima **GARCH(1,1)** solo si el ARCH-LM rechaza homocedasticidad (p-valor < 0.05).

Ecuacion de volatilidad:

```text
sigma_t^2 = omega + alpha * e_{t-1}^2 + beta * sigma_{t-1}^2
```

Si no hay evidencia de efectos ARCH, no se estima GARCH (no se fuerza el modelo).

## 7. Modelo VAR

Sobre los log-rendimientos se estima un VAR:

- seleccion de rezagos por criterio de informacion (AIC; se reportan BIC, HQIC y FPE), sin imponer un minimo de rezagos;
- estabilidad mediante las raices del polinomio companion (todas deben quedar fuera del circulo unitario);
- diagnostico de residuos: Portmanteau (autocorrelacion), normalidad multivariante (Jarque-Bera, como diagnostico) y ARCH-LM por ecuacion;
- **causalidad de Granger**, reportando H0, estadistico y conclusion. Es causalidad predictiva, no causalidad economica;
- **funciones impulso-respuesta** con identificacion de Cholesky y bandas al 95%.

## 8. Identificacion de las impulso-respuesta

Las IRF se identifican con **Cholesky** (ortogonalizacion recursiva). El orden de las variables es **BBVA -> Santander**, que implica que BBVA puede afectar contemporaneamente a Santander pero no al reves. El orden importa: se realizo una verificacion de sensibilidad y la conclusion cualitativa (efectos pequenos y transitorios) se mantiene. Las bandas al 95% se obtienen del error estandar asintotico de las IRF.

## 9. Interpretacion

La meta no es solo obtener salidas del software, sino traducirlas a lenguaje economico:

- si el log-precio tiene raiz unitaria y el log-rendimiento es estacionario;
- si existe persistencia en la volatilidad (solo cuando hay evidencia ARCH);
- si un activo ayuda a predecir al otro (Granger, predictivo);
- y si los choques se transmiten de forma duradera o transitoria.
