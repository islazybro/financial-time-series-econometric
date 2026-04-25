from __future__ import annotations

from econometria_financiera.project_config import load_series_config
from econometria_financiera.validation import validate_series


def main() -> None:
    print("Validando archivos en data/raw...\n")
    for item in load_series_config():
        for message in validate_series(item.name, item.output):
            print(message)


if __name__ == "__main__":
    main()
