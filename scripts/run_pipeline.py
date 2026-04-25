from __future__ import annotations

import argparse

import download_prices
import generate_figures
import run_analysis
import validate_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline completo del proyecto.")
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Usa los CSV existentes en data/raw y evita descargar precios.",
    )
    parser.add_argument(
        "--skip-figures",
        action="store_true",
        help="Ejecuta el analisis sin regenerar graficas.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.skip_download:
        print("Paso 1/4: descarga omitida. Usando archivos existentes en data/raw/.")
    else:
        print("Paso 1/4: descargando precios...")
        download_prices.main()

    print("Paso 2/4: validando datos...")
    validate_data.main()

    print("Paso 3/4: ejecutando analisis econometrico...")
    run_analysis.main()

    if args.skip_figures:
        print("Paso 4/4: generacion de figuras omitida.")
    else:
        print("Paso 4/4: generando figuras...")
        generate_figures.main()

    print("Pipeline completado.")


if __name__ == "__main__":
    main()
