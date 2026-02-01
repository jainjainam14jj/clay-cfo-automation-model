from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import pandas as pd


def render_memo(template_path: Path, out_path: Path, cfg: Dict[str, Any], df: pd.DataFrame) -> None:
    tpl = template_path.read_text(encoding="utf-8")

    end = df.iloc[-1]
    total_revenue = float(df["total_revenue"].sum())
    avg_gm = float(df["gross_margin_pct"].mean())

    seat_mix = df["seat_revenue"].sum() / max(df["total_revenue"].sum(), 1e-9)
    credit_mix = df["credit_revenue"].sum() / max(df["total_revenue"].sum(), 1e-9)

    filled = tpl.format(
        scenario=str(cfg.get("active_scenario", "base")),
        start_month=str(cfg.get("start_month")),
        end_month=str(cfg.get("end_month")),
        end_customers=float(end["customers"]),
        end_mrr=float(end["mrr"]),
        end_arr=float(end["arr"]),
        total_revenue=float(total_revenue),
        avg_gm_pct=float(avg_gm * 100.0),
        avg_seat_mix_pct=float(seat_mix * 100.0),
        avg_credit_mix_pct=float(credit_mix * 100.0),
        new_customers_per_month=float(cfg.get("new_customers_per_month")),
        logo_churn_rate_monthly=float(cfg.get("logo_churn_rate_monthly")),
        expansion_rate_monthly=float(cfg.get("expansion_rate_monthly")),
        seats_per_customer=float(cfg.get("seats_per_customer")),
        price_per_seat_monthly=float(cfg.get("price_per_seat_monthly")),
        credits_per_customer_monthly=float(cfg.get("credits_per_customer_monthly")),
        price_per_1000_credits=float(cfg.get("price_per_1000_credits")),
    )

    out_path.write_text(filled, encoding="utf-8")
