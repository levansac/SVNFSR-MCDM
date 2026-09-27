from __future__ import annotations
from typing import Any
import pandas as pd

from algorithm.weights import calculate_criterion_weights
from algorithm.scalar_weighting import apply_criterion_weights
from algorithm.relation import build_relation_matrix
from algorithm.normalization import normalize_relation_reliability
from algorithm.scoring import calculate_relation_scores
from algorithm.dominance import calculate_dominance_index
from algorithm.ranking import calculate_overall_scores


def run_svnfsr(
    data: pd.DataFrame,
    alpha: float,
    beta: float,
    gamma: float,
    provided_weights: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """
    Full SVNFSR-MCDM pipeline.

    Step 1:
      calculate E(cj), C(cj) and wj automatically with s1/e1/c1,
      then apply criterion weights to the SVNFS matrix.
    Step 2:
      construct relation R.
    Step 3:
      normalize reliability, calculate V, dominance δ and S(u).
    """
    parameter_sum = alpha + beta + gamma
    if alpha <= 0 or beta <= 0 or gamma <= 0:
        raise ValueError("α, β and γ must be greater than 0.")
    if abs(parameter_sum - 1.0) > 1e-9:
        raise ValueError(
            f"α + β + γ must equal 1; current sum is {parameter_sum:.6f}."
        )

    # Luôn tính E, C để có thể hiển thị/kiểm tra. Nếu workbook có sheet
    # Weights thì chỉ thay cột Weight bằng trọng số được cung cấp.
    calculated_weights = calculate_criterion_weights(data)

    if provided_weights is None:
        weights = calculated_weights.copy()
        weights["Weight Source"] = "Tự động từ E và C"
    else:
        supplied = provided_weights[["Criterion", "Weight"]].copy()
        supplied["Criterion"] = supplied["Criterion"].astype(str).str.strip()

        expected = calculated_weights["Criterion"].astype(str).tolist()
        supplied_names = supplied["Criterion"].tolist()
        missing = sorted(set(expected) - set(supplied_names))
        extra = sorted(set(supplied_names) - set(expected))
        if missing or extra:
            messages = []
            if missing:
                messages.append("thiếu: " + ", ".join(missing))
            if extra:
                messages.append("không tồn tại trong Matrix: " + ", ".join(extra))
            raise ValueError("Trang Weights không khớp Matrix (" + "; ".join(messages) + ").")

        weights = calculated_weights.drop(columns=["Weight"]).merge(
            supplied, on="Criterion", how="left", validate="one_to_one"
        )
        weights["Weight Source"] = "Cung cấp từ sheet Weights"

    weighted_matrix = apply_criterion_weights(data, weights)
    relation_matrix = build_relation_matrix(weighted_matrix)

    detail = relation_matrix.copy()
    detail["Normalized μ"] = normalize_relation_reliability(detail)
    detail["V"] = calculate_relation_scores(detail, alpha, beta, gamma)
    detail["δ"] = calculate_dominance_index(detail)
    detail["Dominant Score"] = detail["δ"] * detail["V"]

    ranking = calculate_overall_scores(detail)
    best_score = float(ranking.iloc[0]["Overall Score"])
    best_alternatives = ranking.loc[
        ranking["Overall Score"].sub(best_score).abs() <= 1e-12,
        "Alternative",
    ].astype(str).tolist()

    return {
        "weights": weights,
        "weighted_matrix": weighted_matrix,
        "relation_matrix": relation_matrix,
        "detail": detail,
        "ranking": ranking,
        "best_score": best_score,
        "best_alternatives": best_alternatives,
    }


run_svnfsr_demo = run_svnfsr
