from __future__ import annotations
import pandas as pd


def validate_input_data(data: pd.DataFrame) -> list[str]:
    errors = []
    required = {"Alternative", "Criterion", "T", "I", "F", "μ"}
    missing = required.difference(data.columns)
    if missing:
        return ["Missing columns: " + ", ".join(sorted(missing))]
    if data.empty:
        return ["Input data cannot be empty."]

    alternatives = data["Alternative"].astype(str).str.strip()
    criteria = data["Criterion"].astype(str).str.strip()

    if alternatives.eq("").any():
        errors.append("Alternative names cannot be empty.")
    if criteria.eq("").any():
        errors.append("Criterion names cannot be empty.")

    pairs = pd.DataFrame({"Alternative": alternatives, "Criterion": criteria})
    if pairs.duplicated().any():
        errors.append("Each (Alternative, Criterion) pair must be unique.")

    for column in ["T", "I", "F", "μ"]:
        values = pd.to_numeric(data[column], errors="coerce")
        if values.isna().any() or ((values < 0) | (values > 1)).any():
            errors.append(f"{column} values must be numeric and in [0, 1].")

    criterion_sets = pairs.groupby("Alternative")["Criterion"].apply(frozenset)
    if len(criterion_sets) > 1:
        reference = criterion_sets.iloc[0]
        if not criterion_sets.apply(lambda value: value == reference).all():
            errors.append("All alternatives must use the same criterion set.")
    return errors


def validate_criterion_data(
    criterion_data: pd.DataFrame,
    expected_criteria: list[str],
) -> list[str]:
    errors = []
    required = {"Criterion", "E", "C"}
    missing = required.difference(criterion_data.columns)
    if missing:
        return ["Missing criterion columns: " + ", ".join(sorted(missing))]

    criteria = criterion_data["Criterion"].astype(str).str.strip()
    if criteria.duplicated().any():
        errors.append("Criterion names in weight table must be unique.")
    if set(criteria) != set(expected_criteria):
        errors.append("Weight table criteria must exactly match the SVNFS matrix criteria.")

    e_values = pd.to_numeric(criterion_data["E"], errors="coerce")
    c_values = pd.to_numeric(criterion_data["C"], errors="coerce")
    if e_values.isna().any() or ((e_values < 0) | (e_values > 1)).any():
        errors.append("E(c_j) values must be in [0, 1].")
    if c_values.isna().any() or (c_values < 0).any():
        errors.append("C(c_j) values must be non-negative.")
    return errors


def validate_parameters(alpha: float, beta: float, gamma: float) -> list[str]:
    errors = []
    if alpha <= 0 or beta <= 0 or gamma <= 0:
        errors.append("α, β and γ must be greater than 0.")
    if abs(alpha + beta + gamma - 1.0) > 1e-9:
        errors.append(f"α + β + γ must equal 1 (current: {alpha+beta+gamma:.4f}).")
    return errors
