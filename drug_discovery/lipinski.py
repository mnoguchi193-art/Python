"""
Drug-likeness — Lipinski's Rule of Five / リピンスキーのルール・オブ・ファイブ

A fast first filter in drug design. A molecule is likely to be orally
bioavailable when it satisfies (at most one violation of):

    molecular weight <= 500
    logP             <= 5     (lipophilicity)
    H-bond donors    <= 5
    H-bond acceptors <= 10

Molecular weight is computed from the chemical formula. Standard library only.
"""

import re
from dataclasses import dataclass

# Standard atomic weights (g/mol) for common drug elements.
ATOMIC_WEIGHTS = {
    "H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998,
    "P": 30.974, "S": 32.06, "Cl": 35.45, "Br": 79.904, "I": 126.904,
    "Na": 22.990, "K": 39.098,
}


def molecular_weight(formula: str) -> float:
    """Parse a formula like 'C9H8O4' and return its molecular weight."""
    total = 0.0
    matched = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
    if not any(sym for sym, _ in matched):
        raise ValueError(f"could not parse formula: {formula!r}")
    for symbol, count in matched:
        if not symbol:
            continue
        if symbol not in ATOMIC_WEIGHTS:
            raise ValueError(f"unknown element: {symbol!r}")
        total += ATOMIC_WEIGHTS[symbol] * (int(count) if count else 1)
    return total


@dataclass
class Molecule:
    name: str
    formula: str
    logp: float           # lipophilicity (octanol-water partition)
    h_donors: int         # H-bond donors
    h_acceptors: int      # H-bond acceptors

    @property
    def mw(self) -> float:
        return molecular_weight(self.formula)

    def violations(self) -> list[str]:
        v = []
        if self.mw > 500:
            v.append(f"MW {self.mw:.1f} > 500")
        if self.logp > 5:
            v.append(f"logP {self.logp} > 5")
        if self.h_donors > 5:
            v.append(f"HBD {self.h_donors} > 5")
        if self.h_acceptors > 10:
            v.append(f"HBA {self.h_acceptors} > 10")
        return v

    def is_drug_like(self) -> bool:
        """Rule of Five: poor absorption likely with 2+ violations."""
        return len(self.violations()) <= 1


if __name__ == "__main__":
    molecules = [
        Molecule("Aspirin", "C9H8O4", logp=1.2, h_donors=1, h_acceptors=4),
        Molecule("Caffeine", "C8H10N4O2", logp=-0.07, h_donors=0, h_acceptors=6),
        Molecule("Atorvastatin", "C33H35FN2O5", logp=5.7, h_donors=4, h_acceptors=7),
    ]
    for m in molecules:
        status = "drug-like" if m.is_drug_like() else "FAILS"
        print(f"{m.name:14s} MW={m.mw:6.1f}  {status}")
        for v in m.violations():
            print(f"    violation: {v}")
