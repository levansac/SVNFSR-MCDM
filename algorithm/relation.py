from __future__ import annotations
from itertools import combinations
import pandas as pd


def build_relation_matrix(weighted_data: pd.DataFrame) -> pd.DataFrame:
    """
    For every unordered criterion pair (c_j, c_k) and alternative u_i:

      T_R = min(T_j, T_k)
      I_R = max(I_j, I_k)
      F_R = min(F_j, F_k)
      μ_R = min(μ_j, μ_k)
    """
    rows: list[dict[str, object]] = []

    for alternative, group in weighted_data.groupby("Alternative", sort=False):
        group = group.set_index("Criterion")
        criteria = list(group.index)

        for criterion_j, criterion_k in combinations(criteria, 2):
            left = group.loc[criterion_j]
            right = group.loc[criterion_k]

            rows.append(
                {
                    "Alternative": alternative,
                    "Criterion 1": criterion_j,
                    "Criterion 2": criterion_k,
                    "Relation": f"({criterion_j}, {criterion_k})",
                    "T": min(float(left["Weighted T"]), float(right["Weighted T"])),
                    "I": max(float(left["Weighted I"]), float(right["Weighted I"])),
                    "F": min(float(left["Weighted F"]), float(right["Weighted F"])),
                    "μ": min(float(left["Weighted μ"]), float(right["Weighted μ"])),
                }
            )

    relation = pd.DataFrame(rows)
    if relation.empty:
        raise ValueError("At least two criteria are required to build relation R.")
    return relation
