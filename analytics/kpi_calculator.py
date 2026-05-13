# analytics/kpi_calculator.py
"""KPI calculation engine for business analytics."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from utils.formatters import format_currency, format_percentage, format_change


def calculate_revenue_kpis(df: pd.DataFrame, revenue_col: str, date_col: Optional[str] = None) -> Dict[str, Any]:
    """Calculate comprehensive revenue KPIs."""
    kpis = {}
    revenue = df[revenue_col].dropna()

    kpis["total_revenue"] = float(revenue.sum())
    kpis["avg_revenue"] = float(revenue.mean())
    kpis["max_revenue"] = float(revenue.max())
    kpis["min_revenue"] = float(revenue.min())
    kpis["revenue_std"] = float(revenue.std())

    if date_col and date_col in df.columns:
        df_sorted = df.copy()
        df_sorted[date_col] = pd.to_datetime(df_sorted[date_col], errors="coerce")
        df_sorted = df_sorted.dropna(subset=[date_col]).sort_values(date_col)

        # Monthly breakdown
        df_sorted["month"] = df_sorted[date_col].dt.to_period("M")
        monthly = df_sorted.groupby("month")[revenue_col].sum()

        if len(monthly) >= 2:
            current_month = float(monthly.iloc[-1])
            prev_month = float(monthly.iloc[-2])
            kpis["current_month_revenue"] = current_month
            kpis["prev_month_revenue"] = prev_month
            kpis["mom_change"] = format_change(current_month, prev_month)

        if len(monthly) >= 12:
            current_year = float(monthly.iloc[-12:].sum())
            prev_year = float(monthly.iloc[-24:-12].sum()) if len(monthly) >= 24 else None
            kpis["ytd_revenue"] = current_year
            if prev_year:
                kpis["yoy_change"] = format_change(current_year, prev_year)

        kpis["monthly_trend"] = [
            {"period": str(p), "revenue": float(v)}
            for p, v in monthly.items()
        ]

    return kpis


def calculate_sales_kpis(df: pd.DataFrame, quantity_col: str, revenue_col: str) -> Dict[str, Any]:
    """Calculate sales volume KPIs."""
    kpis = {
        "total_orders": len(df),
        "total_quantity": int(df[quantity_col].sum()) if quantity_col in df.columns else None,
        "avg_order_value": float(df[revenue_col].mean()),
        "median_order_value": float(df[revenue_col].median()),
    }
    return kpis


def calculate_product_kpis(df: pd.DataFrame, product_col: str, revenue_col: str, qty_col: Optional[str] = None) -> List[Dict]:
    """Calculate per-product KPIs."""
    group_cols = {revenue_col: "sum"}
    if qty_col and qty_col in df.columns:
        group_cols[qty_col] = "sum"

    product_stats = df.groupby(product_col).agg(group_cols).reset_index()
    product_stats.columns = [product_col, "revenue"] + (["quantity"] if qty_col else [])
    product_stats["revenue_share"] = product_stats["revenue"] / product_stats["revenue"].sum() * 100
    product_stats = product_stats.sort_values("revenue", ascending=False)

    return product_stats.head(20).to_dict(orient="records")


def calculate_regional_kpis(df: pd.DataFrame, region_col: str, revenue_col: str) -> List[Dict]:
    """Calculate per-region KPIs."""
    regional = df.groupby(region_col)[revenue_col].agg(["sum", "mean", "count"]).reset_index()
    regional.columns = [region_col, "total_revenue", "avg_revenue", "transaction_count"]
    regional["revenue_share"] = regional["total_revenue"] / regional["total_revenue"].sum() * 100
    regional = regional.sort_values("total_revenue", ascending=False)
    return regional.head(20).to_dict(orient="records")


def calculate_growth_rate(values: List[float]) -> float:
    """Calculate compound monthly growth rate (CMGR)."""
    if len(values) < 2 or values[0] == 0:
        return 0.0
    n = len(values) - 1
    return ((values[-1] / values[0]) ** (1 / n) - 1) * 100


def calculate_customer_kpis(df: pd.DataFrame, customer_col: str, revenue_col: str) -> Dict[str, Any]:
    """Customer-level KPIs."""
    customer_stats = df.groupby(customer_col)[revenue_col].agg(["sum", "count"]).reset_index()
    customer_stats.columns = [customer_col, "total_spend", "order_count"]

    return {
        "total_customers": len(customer_stats),
        "avg_customer_value": float(customer_stats["total_spend"].mean()),
        "top_customers": customer_stats.nlargest(10, "total_spend").to_dict(orient="records"),
        "repeat_customers": int((customer_stats["order_count"] > 1).sum()),
        "repeat_rate": float((customer_stats["order_count"] > 1).mean() * 100),
    }
