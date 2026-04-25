# Primeros pasos con GitHub

Esta guia es para avanzar sin enredarnos. GitHub tiene dos partes:

- **Git**: el programa que vive en tu computadora y registra cambios.
- **GitHub**: la pagina web donde se publica el repositorio.

Ahora mismo tu computadora no reconoce `git`, asi que el primer paso es instalarlo.

## Paso 1. Instalar Git

1. Entra a: https://git-scm.com/download/win
2. Descarga la version para Windows.
3. Instala con las opciones por defecto.
4. Cierra y vuelve a abrir PowerShell o la terminal.
5. Ejecuta:

```bash
git --version
```

Si aparece algo como `git version 2.x.x`, ya quedo instalado.

## Paso 2. Crear cuenta o iniciar sesion en GitHub

1. Entra a: https://github.com
2. Crea una cuenta o inicia sesion.
3. Elige un nombre de usuario profesional, si todavia no tienes cuenta.

## Paso 3. Crear el repositorio en GitHub

En GitHub:

1. Presiona `New repository`.
2. Nombre sugerido:

```text
financial-time-series-econometrics
```

3. Descripcion sugerida:

```text
Proyecto de econometria financiera en Python para analizar series de tiempo de BBVA y Santander mediante ADF, ARIMA, GARCH y VAR.
```

4. Selecciona `Public`.
5. No marques `Add a README file`, porque este proyecto ya tiene uno.
6. Crea el repositorio.

## Paso 4. Conectar esta carpeta con GitHub

Cuando Git ya este instalado, desde esta carpeta ejecutaremos:

```bash
git init
git add .
git commit -m "Initial Python econometrics project"
git branch -M main
git remote add origin URL_DEL_REPOSITORIO
git push -u origin main
```

La parte `URL_DEL_REPOSITORIO` se reemplaza por la URL que GitHub te muestre.

## Paso 5. Que no se debe subir

Este proyecto ya incluye un `.gitignore` para evitar subir:

- carpetas de entorno virtual;
- archivos temporales de Python;
- resultados generados;
- datos reales en CSV.

Esto es importante porque en GitHub conviene subir codigo, documentacion y ejemplos, pero no datos sensibles o archivos generados.

## Donde estamos ahora

Estado actual:

- Proyecto estructurado: listo.
- Codigo base: listo.
- Documentacion inicial: lista.
- Git instalado: listo.
- Repositorio publicado: listo.

Siguiente accion: continuar con los ciclos de trabajo: editar, validar, hacer commit y subir cambios.
