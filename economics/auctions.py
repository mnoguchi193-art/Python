"""
Auction Theory — sealed-bid mechanisms and truthful bidding

Auction design won the 2020 Nobel Prize (Milgrom & Wilson). The central insight
is the *Vickrey (second-price)* auction: the winner pays the second-highest bid,
which makes bidding your true value a dominant strategy — no need to guess what
others will do.

A bidder is (name, private_value). A strategy maps a value to a bid.
"""

from __future__ import annotations


Bid = tuple[str, float]
Outcome = tuple[str, float]  # (winner, price paid)


def first_price(bids: list[Bid]) -> Outcome:
    """Highest bidder wins and pays their own bid."""
    winner, amount = max(bids, key=lambda b: b[1])
    return winner, amount


def second_price(bids: list[Bid]) -> Outcome:
    """Vickrey: highest bidder wins but pays the second-highest bid."""
    ranked = sorted(bids, key=lambda b: b[1], reverse=True)
    winner = ranked[0][0]
    price = ranked[1][1] if len(ranked) > 1 else ranked[0][1]
    return winner, price


def surplus(values: dict[str, float], outcome: Outcome) -> float:
    """Winner's payoff = their true value minus the price they paid."""
    winner, price = outcome
    return values[winner] - price


def vickrey_surplus(my_value: float, my_bid: float, highest_rival: float) -> float:
    """My payoff in a second-price auction (ties broken in my favor)."""
    if my_bid >= highest_rival:          # I win, paying the rival's bid
        return my_value - highest_rival
    return 0.0                            # I lose, payoff 0


def truthful_is_dominant(my_value: float, alt_bids: list[float],
                         rival_bids: list[float]) -> bool:
    """Verify bidding your value weakly dominates every alternative bid.

    No matter what the highest rival bids, truthful bidding never earns less
    than any other bid you could have submitted.
    """
    for rival in rival_bids:
        truthful = vickrey_surplus(my_value, my_value, rival)
        if any(vickrey_surplus(my_value, alt, rival) > truthful
               for alt in alt_bids):
            return False
    return True


if __name__ == "__main__":
    values = {"Alice": 100.0, "Bob": 80.0, "Carol": 60.0}
    truthful_bids = [(name, v) for name, v in values.items()]

    fp = first_price(truthful_bids)
    sp = second_price(truthful_bids)
    print("Truthful bids:", values, "\n")
    print(f"First-price : {fp[0]} wins, pays {fp[1]:.0f}, "
          f"surplus {surplus(values, fp):.0f}")
    print(f"Second-price: {sp[0]} wins, pays {sp[1]:.0f}, "
          f"surplus {surplus(values, sp):.0f}")

    # Why truthfulness pays in a second-price auction (Alice's value = 100):
    print("\nAlice (value 100) facing different highest rival bids:")
    print(f"  rival 80  -> underbid 70 wins nothing (0) vs truthful "
          f"{vickrey_surplus(100, 100, 80):.0f}")
    print(f"  rival 120 -> overbid 130 wins at a loss "
          f"({vickrey_surplus(100, 130, 120):.0f}) vs truthful "
          f"{vickrey_surplus(100, 100, 120):.0f}")

    alt_bids = [float(x) for x in range(0, 151, 5)]
    rival_bids = [float(x) for x in range(0, 201, 5)]
    dominant = truthful_is_dominant(100.0, alt_bids, rival_bids)
    print(f"\nTruthful bidding weakly dominates all alternatives? {dominant}")
    print("=> honesty is a dominant strategy (the Vickrey result).")
