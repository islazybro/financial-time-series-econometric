from __future__ import annotations

import pandas as pd

from econometria_financiera.io import write_csv


def test_write_csv_creates_parent_directory(tmp_path):
    output_path = tmp_path / "nested" / "data.csv"
    frame = pd.DataFrame({"value": [1, 2, 3]})

    write_csv(frame, output_path)

    assert output_path.exists()
    assert pd.read_csv(output_path)["value"].tolist() == [1, 2, 3]
