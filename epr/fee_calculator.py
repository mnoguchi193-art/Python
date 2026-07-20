"""
EPR fee calculator — computes recycling fees from packaging weights
using the rates defined in EprSettings.
"""

from settings import EprSettings, default_settings


def calculate_fees(settings: EprSettings, weights_kg: dict[str, float]) -> dict[str, float]:
    """Return the fee per material. Raises KeyError for materials without a rate."""
    fees = {}
    for material, weight in weights_kg.items():
        if weight < 0:
            raise ValueError(f"weight for {material!r} must be >= 0, got {weight}")
        if material not in settings.fee_rates:
            raise KeyError(f"no fee rate configured for material {material!r}")
        fees[material] = round(weight * settings.fee_rates[material], 2)
    return fees


def total_fee(settings: EprSettings, weights_kg: dict[str, float]) -> float:
    return round(sum(calculate_fees(settings, weights_kg).values()), 2)


if __name__ == "__main__":
    settings = default_settings()
    weights = {"paper": 1200.5, "plastic": 830.0, "glass": 4100.0}

    print(f"Producer : {settings.producer_name} ({settings.registration_number})")
    print(f"Year     : FY{settings.fiscal_year}  Currency: {settings.currency}")
    print("-" * 40)
    for material, fee in calculate_fees(settings, weights).items():
        rate = settings.fee_rates[material]
        print(f"{material:<8} {weights[material]:>8.1f} kg x {rate:>5.1f} = {fee:>12,.2f}")
    print("-" * 40)
    print(f"Total    {total_fee(settings, weights):>31,.2f} {settings.currency}")
