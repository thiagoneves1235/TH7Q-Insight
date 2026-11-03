from __future__ import annotations

import numpy as np
import pandas as pd


def create_sample_data(rows: int = 120, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-01", periods=rows, freq="h")
    production = rng.normal(1000, 90, rows).clip(500)
    loss = rng.normal(32, 8, rows).clip(2)
    downtime = rng.normal(25, 10, rows).clip(0)
    outliers = rng.choice(rows, size=max(1, rows // 20), replace=False)
    production[outliers] *= 0.45
    loss[outliers] *= 2.5
    return pd.DataFrame(
        {
            "data_hora": dates,
            "linha": rng.choice(["Linha A", "Linha B", "Linha C"], rows),
            "producao_unidades": production.round(0),
            "perdas_unidades": loss.round(0),
            "parada_minutos": downtime.round(1),
            "temperatura_c": rng.normal(72, 3, rows).round(1),
        }
    )
