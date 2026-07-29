from __future__ import annotations
import pandas as pd


def calculate_relation_scores(
    relation_data: pd.DataFrame,
    alpha: float,
    beta: float,
    gamma: float,
) -> pd.Series:
    """
    V_ip = μ'_ip [αT_ip + β(1-I_ip) + γ(1-F_ip)]
    """
    return relation_data["Normalized μ"] * (
        alpha * relation_data["T"]
        + beta * (1.0 - relation_data["I"])
        + gamma * (1.0 - relation_data["F"])
    )
