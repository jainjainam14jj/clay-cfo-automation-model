from __future__ import annotations

import pandas as pd


def run_qa(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []

    # Basic sanity
    if (df["customers"] < 0).any():
        issues.append("ERROR: Negative customers found.")

    if (df[["seat_revenue", "credit_revenue", "total_revenue"]] < 0).any().any():
        issues.append("ERROR: Negative revenue values found.")

    # Revenue identity
    rev_diff = (df["seat_revenue"] + df["credit_revenue"] - df["total_revenue"]).abs().max()
    if rev_diff > 1e-6:
        issues.append(f"ERROR: Revenue components do not sum to total (max diff {rev_diff}).")

    # GM bounds
    if ((df["gross_margin_pct"] < -0.05) | (df["gross_margin_pct"] > 1.05)).any():
        issues.append("WARN: Gross margin outside expected bounds (-5% to 105%).")

    # Month monotonic
    if not df["month"].is_monotonic_increasing:
        issues.append("ERROR: Months not sorted ascending.")

    if not issues:
        issues.append("OK: No issues found.")

    return issues
