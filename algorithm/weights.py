from __future__ import annotations
import pandas as pd


def calculate_criterion_weights(
    criterion_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    w_j = [1 - E(c_j) + C(c_j)] /
          Σ_j [1 - E(c_j) + C(c_j)]
    """
    required = {"Criterion", "E", "C"}
    missing = required.difference(criterion_data.columns)
    if missing:
        raise ValueError("Missing criterion columns: " + ", ".join(sorted(missing)))

    result = criterion_data.copy()
    result["Criterion"] = result["Criterion"].astype(str).str.strip()
    result["E"] = pd.to_numeric(result["E"], errors="raise")
    result["C"] = pd.to_numeric(result["C"], errors="raise")

    if result["Criterion"].eq("").any():
        raise ValueError("Criterion names cannot be empty.")
    if result["Criterion"].duplicated().any():
        raise ValueError("Criterion names must be unique.")
    if ((result["E"] < 0) | (result["E"] > 1)).any():
        raise ValueError("E(c_j) values must be in [0, 1].")
    if (result["C"] < 0).any():
        raise ValueError("C(c_j) values must be non-negative.")

    result["Weight Numerator"] = 1.0 - result["E"] + result["C"]
    denominator = float(result["Weight Numerator"].sum())

    if denominator <= 0:
        raise ValueError("The criterion-weight denominator must be greater than 0.")

    result["Weight"] = result["Weight Numerator"] / denominator
    return result
