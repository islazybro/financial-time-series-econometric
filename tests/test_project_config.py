from __future__ import annotations

from econometria_financiera.project_config import load_series_config


def test_load_series_config_reads_names_tickers_and_outputs(tmp_path):
    config_path = tmp_path / "data_sources.json"
    config_path.write_text(
        """
        {
          "series": [
            {"name": "Apple", "ticker": "AAPL", "output": "data/raw/AAPL.csv"},
            {"name": "Microsoft", "ticker": "MSFT", "output": "data/raw/MSFT.csv"}
          ]
        }
        """,
        encoding="utf-8",
    )

    first, second = load_series_config(config_path)

    assert first.name == "Apple"
    assert first.slug == "aapl"
    assert second.output.as_posix() == "data/raw/MSFT.csv"


def test_load_series_config_requires_two_series(tmp_path):
    config_path = tmp_path / "data_sources.json"
    config_path.write_text(
        """
        {
          "series": [
            {"name": "Only", "ticker": "ONLY", "output": "data/raw/ONLY.csv"}
          ]
        }
        """,
        encoding="utf-8",
    )

    try:
        load_series_config(config_path)
    except ValueError as exc:
        assert "exactamente dos series" in str(exc)
    else:
        raise AssertionError("Expected ValueError for one configured series")
