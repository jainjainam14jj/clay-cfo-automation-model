from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd
import numpy as np


def month_range(start_month: str, end_month: str) -> pd.DatetimeIndex:
    start = pd.to_datetime(start_month + "-01")
    end = pd.to_datetime(end_month + "-01")
    return pd.date_range(start=start, end=end, freq="MS")


@dataclass
class Scenario:
    name: str
    new_customers_mult: float
    churn_mult: float
    expansion_mult: float


def build_model(cfg: Dict[str, Any], scenario_name: str | None = None) -> pd.DataFrame:
    months = month_range(cfg["start_month"], cfg["end_month"])

    scenario_name = scenario_name or cfg.get("active_scenario", "base")
    sc = cfg.get("scenarios", {}).get(scenario_name, {})
    scenario = Scenario(
        name=str(scenario_name),
        new_customers_mult=float(sc.get("new_customers_mult", 1.0)),
        churn_mult=float(sc.get("churn_mult", 1.0)),
        expansion_mult=float(sc.get("expansion_mult", 1.0)),
    )

    # Inputs
    new_cust = float(cfg["new_customers_per_month"]) * scenario.new_customers_mult
    churn = float(cfg["logo_churn_rate_monthly"]) * scenario.churn_mult
    expansion = float(cfg["expansion_rate_monthly"]) * scenario.expansion_mult

    seats_per_cust = float(cfg["seats_per_customer"])  # baseline
    price_seat = float(cfg["price_per_seat_monthly"])  # $/seat/mo

    credits_per_cust = float(cfg["credits_per_customer_monthly"])  # baseline
    price_per_1k = float(cfg["price_per_1000_credits"])  # $ per 1k

    cogs_pct = float(cfg["cogs_percent_of_revenue"])
    ai_cost_per_1k = float(cfg.get("ai_cost_per_1000_credits", 0.0))

    opex = cfg.get("opex_monthly", {})
    opex_rnd = float(opex.get("rnd", 0.0))
    opex_sm = float(opex.get("s_and_m", 0.0))
    opex_ga = float(opex.get("g_and_a", 0.0))

    # Arrays
    n = len(months)
    customers = np.zeros(n)
    churned = np.zeros(n)
    new = np.zeros(n)

    # Monetization per customer (applies expansion monthly)
    seats_per = np.zeros(n)
    credits_per = np.zeros(n)

    customers[0] = float(cfg["starting_customers"])
    seats_per[0] = seats_per_cust
    credits_per[0] = credits_per_cust

    for i in range(n):
        if i > 0:
            # carry forward customers then apply churn + new
            churned[i] = customers[i - 1] * churn
            new[i] = new_cust
            customers[i] = max(customers[i - 1] - churned[i] + new[i], 0.0)

            # expansion increases monetization on existing base
            seats_per[i] = seats_per[i - 1] * (1.0 + expansion)
            credits_per[i] = credits_per[i - 1] * (1.0 + expansion)
        else:
            churned[i] = customers[i] * 0.0
            new[i] = new_cust  # shown for month 1 in reporting

    seat_revenue = customers * seats_per * price_seat
    credit_revenue = customers * (credits_per / 1000.0) * price_per_1k
    total_revenue = seat_revenue + credit_revenue

    # COGS: percent of revenue + variable AI cost tied to credits delivered
    ai_cogs = customers * (credits_per / 1000.0) * ai_cost_per_1k
    cogs = total_revenue * cogs_pct + ai_cogs

    gross_profit = total_revenue - cogs
    gm_pct = np.where(total_revenue > 0, gross_profit / total_revenue, 0.0)

    total_opex = opex_rnd + opex_sm + opex_ga
    ebitda = gross_profit - total_opex
    ebitda_margin = np.where(total_revenue > 0, ebitda / total_revenue, 0.0)

    df = pd.DataFrame(
        {
            "month": months,
            "scenario": scenario.name,
            "customers": customers,
            "new_customers": new,
            "churned_customers": churned,
            "seats_per_customer": seats_per,
            "credits_per_customer": credits_per,
            "seat_revenue": seat_revenue,
            "credit_revenue": credit_revenue,
            "total_revenue": total_revenue,
            "cogs": cogs,
            "ai_cogs": ai_cogs,
            "gross_profit": gross_profit,
            "gross_margin_pct": gm_pct,
            "opex_rnd": opex_rnd,
            "opex_s_and_m": opex_sm,
            "opex_g_and_a": opex_ga,
            "opex_total": total_opex,
            "ebitda": ebitda,
            "ebitda_margin_pct": ebitda_margin,
            "mrr": total_revenue,
            "arr": total_revenue * 12.0,
        }
    )

    return df
