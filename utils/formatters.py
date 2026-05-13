# utils/formatters.py
"""Number, currency, and date formatting utilities."""
from datetime import datetime
from typing import Union
import math


def format_currency(value: float, currency: str = "USD", compact: bool = False) -> str:
    """Format number as currency string."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"

    if compact:
        if abs(value) >= 1_000_000_000:
            return f"${value/1_000_000_000:.1f}B"
        elif abs(value) >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"${value/1_000:.1f}K"

    return f"${value:,.2f}"


def format_number(value: float, compact: bool = True) -> str:
    """Format number with compact suffix."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"

    if compact:
        if abs(value) >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value/1_000:.1f}K"

    return f"{value:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format as percentage."""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_change(current: float, previous: float) -> dict:
    """Calculate and format change between two values."""
    if previous == 0:
        return {"value": 0, "pct": 0, "direction": "neutral", "label": "N/A"}

    change = current - previous
    pct_change = (change / abs(previous)) * 100
    direction = "up" if change > 0 else "down" if change < 0 else "neutral"

    return {
        "value": change,
        "pct": round(pct_change, 2),
        "direction": direction,
        "label": f"{'+' if change > 0 else ''}{format_number(change)} ({'+' if pct_change > 0 else ''}{pct_change:.1f}%)",
    }


def format_date(dt: Union[datetime, str], fmt: str = "%b %d, %Y") -> str:
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime(fmt)


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
