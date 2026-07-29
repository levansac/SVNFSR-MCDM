from __future__ import annotations
import pandas as pd


def calculate_overall_scores(detail: pd.DataFrame) -> pd.DataFrame:
    """
    S(u_i) = Σ_p δ_ip V_ip
    """
    working = detail.copy()
    working["Dominant Score"] = working["δ"] * working["V"]

    ranking = (
        working.groupby("Alternative", as_index=False)
        .agg(
            **{
                "Overall Score": ("Dominant Score", "sum"),
                "Dominant Relations": ("δ", "sum"),
            }
        )
        .sort_values(
            ["Overall Score", "Dominant Relations", "Alternative"],
            ascending=[False, False, True],
        )
        .reset_index(drop=True)
    )
    ranking.insert(
        0,
        "Rank",
        ranking["Overall Score"].rank(method="min", ascending=False).astype(int),
    )
    return ranking
