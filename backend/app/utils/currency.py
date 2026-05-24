"""
AGSPE Currency Conversion Utility
Handles INR/USD dual currency display with automatic conversion.
"""
from typing import Dict, Tuple


# Approximate exchange rate (updated periodically)
EXCHANGE_RATES = {
    "INR_TO_USD": 1 / 83.5,
    "USD_TO_INR": 83.5,
}


def inr_to_usd(amount_inr: float) -> float:
    """Convert INR to USD."""
    if amount_inr == 0:
        return 0.0
    return round(amount_inr * EXCHANGE_RATES["INR_TO_USD"], 2)


def usd_to_inr(amount_usd: float) -> float:
    """Convert USD to INR."""
    if amount_usd == 0:
        return 0.0
    return round(amount_usd * EXCHANGE_RATES["USD_TO_INR"], 2)


def format_dual_currency(amount_inr: float) -> Dict[str, str]:
    """Format an amount in both INR and USD with proper notation."""
    return {
        "inr": format_indian_currency(amount_inr),
        "usd": format_usd(inr_to_usd(amount_inr)),
    }


def format_indian_currency(amount: float) -> str:
    """Format amount in Indian currency notation (Lakh/Crore)."""
    if abs(amount) >= 1e12:
        return f"INR {amount / 1e12:.2f} Lakh Crore"
    elif abs(amount) >= 1e7:
        return f"INR {amount / 1e7:.2f} Cr"
    elif abs(amount) >= 1e5:
        return f"INR {amount / 1e5:.2f} L"
    elif abs(amount) >= 1e3:
        return f"INR {amount / 1e3:.2f}K"
    else:
        return f"INR {amount:.2f}"


def format_usd(amount: float) -> str:
    """Format amount in USD notation (Million/Billion)."""
    if abs(amount) >= 1e12:
        return f"USD {amount / 1e12:.2f}T"
    elif abs(amount) >= 1e9:
        return f"USD {amount / 1e9:.2f}B"
    elif abs(amount) >= 1e6:
        return f"USD {amount / 1e6:.2f}M"
    elif abs(amount) >= 1e3:
        return f"USD {amount / 1e3:.2f}K"
    else:
        return f"USD {amount:.2f}"


def get_exchange_rate() -> Dict[str, float]:
    """Return current exchange rates."""
    return EXCHANGE_RATES.copy()
