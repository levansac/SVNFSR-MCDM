from __future__ import annotations

import math
import pandas as pd


def _s1(a: tuple[float, float, float, float],
        b: tuple[float, float, float, float]) -> float:
    """
    Similarity s1 from the source paper.

    Components are represented as (T, I, F, μ).  The paper defines
    Δ0=Δμ, Δ1=ΔT, Δ2=ΔI, Δ3=ΔF; the summation is order-independent.

    s1(A,B) = ((sqrt(2)+1)/4) *
              [sqrt(2) * Σ_{l=0..3} cos(|Δ_l|π/4) - 4]
    """
    deltas = [abs(float(x) - float(y)) for x, y in zip(a, b)]
    cosine_sum = sum(math.cos(delta * math.pi / 4.0) for delta in deltas)
    return ((math.sqrt(2.0) + 1.0) / 4.0) * (
        math.sqrt(2.0) * cosine_sum - 4.0
    )


def _complement(a: tuple[float, float, float, float]
                ) -> tuple[float, float, float, float]:
    """
    Complement used by the AUTHORS' reference implementation for e1.

    IMPORTANT:
    The published source code (im.py -> e() and nfs.py -> ecj()) creates
    the complement component-wise as 1 - x for ALL four components.

    The application stores a value in the order (T, I, F, μ), therefore:
        (T, I, F, μ)^c = (1-T, 1-I, 1-F, 1-μ)

    We intentionally follow the authors' executable implementation here,
    because the experimental Step-2 weights in the paper were generated
    from that implementation.
    """
    T, I, F, mu = a
    return 1.0 - T, 1.0 - I, 1.0 - F, 1.0 - mu


def _tuple_from_row(row: pd.Series) -> tuple[float, float, float, float]:
    return (
        float(row["T"]),
        float(row["I"]),
        float(row["F"]),
        float(row["μ"]),
    )


def calculate_criterion_weights(data: pd.DataFrame) -> pd.DataFrame:
    """
    Automatically calculate criterion weights from the SVNFS matrix
    using the similarity-based information measures s1, e1 and c1.

    Eq. (23):
        E(c_j) = (1/n) Σ_i e1(nf_ij)
        e1(A) = s1(A, complement(A))

    Eq. (25), then Eq. (24):
        c1(nf_ij) = (1/(n-1)) Σ_{k!=i} c1(nf_ij,nf_kj)
        c1(A,B) = 1 - s1(A,B)
        C(c_j) = (1/n) Σ_i c1(nf_ij)

    Eq. (28):
        w_j = [1-E(c_j)+C(c_j)] /
              Σ_q [1-E(c_q)+C(c_q)]
    """
    required = {"Alternative", "Criterion", "T", "I", "F", "μ"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(
            "Missing SVNFS columns: " + ", ".join(sorted(missing))
        )

    working = data.copy()
    for column in ["T", "I", "F", "μ"]:
        working[column] = pd.to_numeric(working[column], errors="raise")
        if ((working[column] < 0) | (working[column] > 1)).any():
            raise ValueError(f"{column} values must be in [0, 1].")

    rows = []
    for criterion, group in working.groupby("Criterion", sort=False):
        group = group.reset_index(drop=True)
        values = [_tuple_from_row(row) for _, row in group.iterrows()]
        n = len(values)

        if n < 2:
            raise ValueError(
                f"Criterion {criterion} needs at least two alternatives "
                "to calculate cross-entropy."
            )

        entropy_values = [
            _s1(value, _complement(value))
            for value in values
        ]
        E = sum(entropy_values) / n

        alternative_cross_entropies = []
        for i, value_i in enumerate(values):
            pairwise = [
                1.0 - _s1(value_i, value_k)
                for k, value_k in enumerate(values)
                if k != i
            ]
            alternative_cross_entropies.append(
                sum(pairwise) / (n - 1)
            )

        C = sum(alternative_cross_entropies) / n

        rows.append(
            {
                "Criterion": str(criterion),
                "E": E,
                "C": C,
                "Weight Numerator": 1.0 - E + C,
            }
        )

    result = pd.DataFrame(rows)
    denominator = float(result["Weight Numerator"].sum())
    if denominator <= 0:
        raise ValueError("The criterion-weight denominator must be greater than 0.")

    result["Weight"] = result["Weight Numerator"] / denominator
    return result
