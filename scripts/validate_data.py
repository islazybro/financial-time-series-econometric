from __future__ import annotations

from pathlib import Path

from econometria_financiera.validation import validate_series


RAW_DIR = Path("data/raw")
EXPECTED_FILES = {
    "BBVA": RAW_DIR / "BBVA.csv",
    "Santander": RAW_DIR / "SAN.csv",
}


def main() -> None:
    print("Validando archivos en data/raw...\n")
    for name, path in EXPECTED_FILES.items():
        for message in validate_series(name, path):
            print(message)


if __name__ == "__main__":
    main()
