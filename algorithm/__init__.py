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
    criterion_data: pd.DataFrame,
    alpha: float,
    beta: float,
    gamma: float,
) -> dict[str, Any]:
    """
    Full pipeline:
      Step 1: criterion weights + weighted SVNFS matrix
      Step 2: relation R
      Step 3: reliability normalization, V, δ, S(u)
    """
    parameter_sum = alpha + beta + gamma
    if alpha <= 0 or beta <= 0 or gamma <= 0:
        raise ValueError("α, β and γ must be greater than 0.")
    if abs(parameter_sum - 1.0) > 1e-9:
        raise ValueError(f"α + β + γ must equal 1; current sum is {parameter_sum:.6f}.")

    weights = calculate_criterion_weights(criterion_data)
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
