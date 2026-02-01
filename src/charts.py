from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def save_charts(df: pd.DataFrame, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    # 1) MRR + ARR
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(df["month"], df["mrr"], label="MRR", linewidth=2)
    ax1.set_title("MRR over time")
    ax1.set_ylabel("MRR ($)")
    ax1.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    p = out_dir / "mrr.png"
    fig.tight_layout()
    fig.savefig(p, dpi=200)
    plt.close(fig)
    paths.append(p)

    fig, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(df["month"], df["arr"], label="ARR", linewidth=2, color="#2a6fdb")
    ax2.set_title("ARR over time")
    ax2.set_ylabel("ARR ($)")
    ax2.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    p = out_dir / "arr.png"
    fig.tight_layout()
    fig.savefig(p, dpi=200)
    plt.close(fig)
    paths.append(p)

    # 2) Revenue mix
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.stackplot(
        df["month"],
        df["seat_revenue"],
        df["credit_revenue"],
        labels=["Seats", "Credits"],
        alpha=0.9,
    )
    ax.set_title("Revenue mix (Seats vs Credits)")
    ax.set_ylabel("Revenue ($)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.2)
    fig.autofmt_xdate()
    p = out_dir / "revenue_mix.png"
    fig.tight_layout()
    fig.savefig(p, dpi=200)
    plt.close(fig)
    paths.append(p)

    # 3) Gross margin %
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["month"], df["gross_margin_pct"] * 100.0, linewidth=2, color="#1b9e77")
    ax.set_title("Gross margin %")
    ax.set_ylabel("GM (%)")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    p = out_dir / "gross_margin.png"
    fig.tight_layout()
    fig.savefig(p, dpi=200)
    plt.close(fig)
    paths.append(p)

    return paths
