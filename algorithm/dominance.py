from __future__ import annotations
import numpy as np
import pandas as pd


def calculate_dominance_index(
    detail: pd.DataFrame,
    tolerance: float = 1e-12,
) -> pd.Series:
    """
    δ_ip = 1 if V_ip = max_r V_rp; otherwise 0.
    Ties all receive 1.
    """
    maxima = detail.groupby("Relation")["V"].transform("max")
    return pd.Series(
        np.isclose(
            detail["V"].to_numpy(float),
            maxima.to_numpy(float),
            atol=tolerance,
            rtol=0.0,
        ).astype(int),
        index=detail.index,
        name="δ",
    )
