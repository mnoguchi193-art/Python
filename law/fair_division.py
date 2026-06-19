"""
Fair Division — the Adjusted Winner procedure (Brams & Taylor)

How should a court split contested assets in a divorce, inheritance, or treaty?
Each party distributes 100 points over the items to reveal how much they value
each. Adjusted Winner produces a settlement that is provably:

  envy-free   — neither party prefers the other's share,
  equitable   — both end up with the same point total in their own eyes, and
  efficient   — no other split makes one better off without hurting the other.

At most one item ends up shared (split) between the parties.
"""

from __future__ import annotations


Valuation = dict[str, float]


def adjusted_winner(a: Valuation, b: Valuation) -> dict:
    """Run Adjusted Winner for two parties 'A' and 'B'.

    Returns the allocation, the (equal) point totals, and which item, if any,
    had to be split and in what fraction.
    """
    items = list(a)
    # Phase 1: each item provisionally goes to whoever values it more.
    holder = {it: ("A" if a[it] >= b[it] else "B") for it in items}

    def totals(holder, split=None):
        # The split item is counted fractionally for each party by their own
        # valuation, so it is excluded from the whole-item base sums.
        split_item = split[0] if split else None
        ta = sum(a[it] for it in items if holder[it] == "A" and it != split_item)
        tb = sum(b[it] for it in items if holder[it] == "B" and it != split_item)
        if split:
            it, frac_to_a = split
            ta += frac_to_a * a[it]
            tb += (1 - frac_to_a) * b[it]
        return ta, tb

    ta, tb = totals(holder)

    # Phase 2: move items from the richer party to the poorer one, cheapest
    # first (smallest gain-to-loss ratio), until the totals meet.
    ahead, behind = ("A", "B") if ta >= tb else ("B", "A")
    val_ahead, val_behind = (a, b) if ahead == "A" else (b, a)
    transferable = sorted(
        (it for it in items if holder[it] == ahead),
        key=lambda it: val_ahead[it] / val_behind[it],
    )

    split = None
    for it in transferable:
        ta, tb = totals(holder)
        lead = (ta - tb) if ahead == "A" else (tb - ta)
        if lead <= 1e-12:
            break
        # Fraction t of this item to move so the totals equalize.
        t = lead / (val_ahead[it] + val_behind[it])
        if t < 1.0:
            frac_to_a = (1 - t) if ahead == "A" else t
            split = (it, frac_to_a)
            break
        holder[it] = behind  # move the whole item, keep going

    final_a, final_b = totals(holder, split)
    return {
        "allocation": holder,
        "split": split,
        "points_A": round(final_a, 2),
        "points_B": round(final_b, 2),
    }


if __name__ == "__main__":
    # Divorce settlement: husband (A) vs wife (B), each rating assets out of 100.
    husband = {"House": 30, "Business": 40, "Car": 10, "Pension": 15, "Art": 5}
    wife =    {"House": 40, "Business": 10, "Car": 5,  "Pension": 25, "Art": 20}

    result = adjusted_winner(husband, wife)
    split_item = result["split"][0] if result["split"] else None
    print("Adjusted Winner divorce settlement (points out of 100):\n")
    for item, owner in result["allocation"].items():
        if item == split_item:
            continue
        tag = "Husband" if owner == "A" else "Wife"
        print(f"  {item:<9} -> {tag}")

    if result["split"]:
        item, frac = result["split"]
        print(f"  {item:<9} -> shared: {frac:.0%} Husband / {1 - frac:.0%} Wife")

    print(f"\n  Husband's points: {result['points_A']}")
    print(f"  Wife's points:    {result['points_B']}")
    print("  (equal totals => an equitable, envy-free settlement)")
