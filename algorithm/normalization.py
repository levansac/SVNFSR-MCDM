from __future__ import annotations
import pandas as pd


def normalize_relation_reliability(
    relation_data: pd.DataFrame,
) -> pd.Series:
    """
    μ'_{ip} = μ_{ip} / Σ_q μ_{iq}

    Here p and q index criterion relations after Step 2.
    """
    reliability = pd.to_numeric(relation_data["μ"], errors="raise")
    denominator = reliability.groupby(
        relation_data["Alternative"]
    ).transform("sum")

    if (denominator <= 0).any():
        raise ValueError("Reliability sum must be greater than 0 for each alternative.")

    return reliability / denominator
