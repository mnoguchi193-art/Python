"""
EPR (拡張生産者責任 / Extended Producer Responsibility) settings management.

Dataclass-based settings with JSON persistence and validation.
Standard library only.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Default fee rates in JPY per kg of packaging material placed on the market.
DEFAULT_FEE_RATES = {
    "paper": 15.0,
    "plastic": 46.0,
    "glass": 6.0,
    "metal": 12.0,
}


@dataclass
class EprSettings:
    """Producer registration and fee settings for EPR reporting."""

    producer_name: str
    registration_number: str
    country: str = "JP"
    fiscal_year: int = 2026
    currency: str = "JPY"
    fee_rates: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_FEE_RATES))

    def validate(self) -> None:
        if not self.producer_name.strip():
            raise ValueError("producer_name must not be empty")
        if not self.registration_number.strip():
            raise ValueError("registration_number must not be empty")
        if self.fiscal_year < 2000:
            raise ValueError(f"fiscal_year looks invalid: {self.fiscal_year}")
        for material, rate in self.fee_rates.items():
            if rate < 0:
                raise ValueError(f"fee rate for {material!r} must be >= 0, got {rate}")


def default_settings() -> EprSettings:
    return EprSettings(producer_name="サンプル株式会社", registration_number="EPR-JP-000001")


def load_settings(path) -> EprSettings:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    settings = EprSettings(**data)
    settings.validate()
    return settings


def save_settings(path, settings: EprSettings) -> None:
    settings.validate()
    Path(path).write_text(
        json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    import tempfile

    settings = default_settings()
    print("Default settings:", settings)

    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / "epr_settings.json"
        save_settings(cfg, settings)
        print("Saved JSON:")
        print(cfg.read_text(encoding="utf-8"))

        loaded = load_settings(cfg)
        print("Round-trip OK:", loaded == settings)
