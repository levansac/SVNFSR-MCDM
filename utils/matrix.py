from __future__ import annotations
import re
import pandas as pd

CELL_PATTERN = re.compile(
    r"^\s*[\(\[]?\s*(\d*\.?\d+)\s*[,;]\s*(\d*\.?\d+)\s*[,;]\s*"
    r"(\d*\.?\d+)\s*[\)\]]?\s*[/|;]\s*(\d*\.?\d+)\s*$"
)


def format_svnfs_cell(t: float, i: float, f: float, mu: float) -> str:
    return f"({t:.2f}, {i:.2f}, {f:.2f}) / {mu:.2f}"


def create_default_matrix(n: int, m: int) -> pd.DataFrame:
    rows = []
    for i in range(n):
        row = {"Alternative": f"S{i+1}"}
        for j in range(m):
            row[f"C{j+1}"] = format_svnfs_cell(
                min(0.55 + i*0.04 + j*0.02, 0.95),
                max(0.25 - i*0.01 + j*0.01, 0.05),
                max(0.25 - i*0.02 + j*0.01, 0.05),
                min(0.70 + i*0.03 + j*0.02, 0.98),
            )
        rows.append(row)
    return pd.DataFrame(rows)


def parse_svnfs_cell(value: object) -> tuple[float, float, float, float]:
    match = CELL_PATTERN.match(str(value).strip())
    if not match:
        raise ValueError("Use format '(0.70, 0.40, 0.60) / 0.94'.")
    values = tuple(float(item) for item in match.groups())
    if any(item < 0 or item > 1 for item in values):
        raise ValueError("T, I, F and μ must be in [0, 1].")
    return values


def matrix_to_long(matrix: pd.DataFrame) -> pd.DataFrame:
    if "Alternative" not in matrix.columns:
        raise ValueError("Matrix must contain Alternative column.")
    criteria = [c for c in matrix.columns if c != "Alternative"]
    rows = []
    for row_index, row in matrix.iterrows():
        alternative = str(row["Alternative"]).strip()
        if not alternative:
            raise ValueError(f"Alternative at row {row_index+1} is empty.")
        for criterion in criteria:
            try:
                t, i, f, mu = parse_svnfs_cell(row[criterion])
            except ValueError as error:
                raise ValueError(f"Cell {alternative}-{criterion}: {error}") from error
            rows.append({
                "Alternative": alternative,
                "Criterion": str(criterion),
                "T": t, "I": i, "F": f, "μ": mu,
            })
    return pd.DataFrame(rows)
