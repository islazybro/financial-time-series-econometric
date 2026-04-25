from __future__ import annotations

import pandas as pd

from econometria_financiera.validation import validate_series


def test_validate_series_reports_clean_file(tmp_path):
    csv_path = tmp_path / "valid.csv"
    pd.DataFrame(
        {
            "Fecha": pd.date_range("2020-01-01", periods=40, freq="MS"),
            "Cierre": range(100, 140),
        }
    ).to_csv(csv_path, index=False)

    messages = validate_series("Demo", csv_path)

    assert len(messages) == 1
    assert messages[0].startswith("Demo: OK.")


def test_validate_series_reports_non_numeric_rows(tmp_path):
    csv_path = tmp_path / "dirty.csv"
    frame = pd.DataFrame(
        {
            "Fecha": ["", *pd.date_range("2020-01-01", periods=40, freq="MS").astype(str)],
            "Cierre": ["TICKER", *range(100, 140)],
        }
    )
    frame.to_csv(csv_path, index=False)

    messages = validate_series("Demo", csv_path)

    assert any("se descartaron 1 filas" in message for message in messages)
