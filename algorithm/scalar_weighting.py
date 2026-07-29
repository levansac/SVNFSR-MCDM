from __future__ import annotations
import numpy as np
import pandas as pd


def _weighted_component(values: pd.Series, weights: pd.Series) -> pd.Series:
    values_array = values.to_numpy(dtype=float)
    weights_array = weights.to_numpy(dtype=float)
    return pd.Series(
        1.0 - np.power(1.0 - values_array, weights_array),
        index=values.index,
    )


def apply_criterion_weights(
    data: pd.DataFrame,
    weights: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply λ = w_j to each SVNFS value:

      x^(w_j) = (
          1-(1-T)^w_j,
          1-(1-I)^w_j,
          1-(1-F)^w_j,
          1-(1-μ)^w_j
      )
    """
    result = data.merge(
        weights[["Criterion", "Weight"]],
        on="Criterion",
        how="left",
        validate="many_to_one",
    )

    if result["Weight"].isna().any():
        missing = result.loc[result["Weight"].isna(), "Criterion"].unique().tolist()
        raise ValueError(f"Missing weights for criteria: {missing}")

    for source, target in [
        ("T", "Weighted T"),
        ("I", "Weighted I"),
        ("F", "Weighted F"),
        ("μ", "Weighted μ"),
    ]:
        result[target] = _weighted_component(result[source], result["Weight"])

    return result
