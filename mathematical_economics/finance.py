"""
Financial mathematics — time value of money / 金融数理

Present value, future value, net present value (NPV), and internal rate of
return (IRR, solved by bisection). Standard library only.
"""


def future_value(present: float, rate: float, periods: int) -> float:
    """FV = PV * (1 + r)**n."""
    return present * (1 + rate) ** periods


def present_value(future: float, rate: float, periods: int) -> float:
    """PV = FV / (1 + r)**n."""
    return future / (1 + rate) ** periods


def net_present_value(rate: float, cashflows: list[float]) -> float:
    """NPV with cashflows[0] occurring at t = 0."""
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))


def annuity_present_value(payment: float, rate: float, periods: int) -> float:
    """PV of a level annuity paid at the end of each period."""
    if rate == 0:
        return payment * periods
    return payment * (1 - (1 + rate) ** -periods) / rate


def internal_rate_of_return(
    cashflows: list[float],
    low: float = -0.9999,
    high: float = 10.0,
    tol: float = 1e-8,
    max_iter: int = 200,
) -> float:
    """Solve NPV(r) == 0 by bisection.

    Requires NPV to change sign across [low, high].
    """
    f_low = net_present_value(low, cashflows)
    f_high = net_present_value(high, cashflows)
    if f_low * f_high > 0:
        raise ValueError("IRR not bracketed by the given interval")

    for _ in range(max_iter):
        mid = (low + high) / 2
        f_mid = net_present_value(mid, cashflows)
        if abs(f_mid) < tol:
            return mid
        if f_low * f_mid < 0:
            high = mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


if __name__ == "__main__":
    print(f"FV of 1000 at 5% for 10y: {future_value(1000, 0.05, 10):.2f}")
    print(f"PV of 1000 at 5% in 10y:  {present_value(1000, 0.05, 10):.2f}")

    flows = [-1000, 300, 400, 500, 600]
    print(f"NPV at 8%: {net_present_value(0.08, flows):.2f}")
    print(f"IRR:       {internal_rate_of_return(flows) * 100:.3f}%")
    print(f"Annuity PV (100/yr, 5%, 20y): {annuity_present_value(100, 0.05, 20):.2f}")
