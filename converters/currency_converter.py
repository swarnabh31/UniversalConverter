"""Currency converter with online rate fetching and offline caching."""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from converters.base import ConverterBase


# Free exchange rate APIs (no API key required)
RATE_APIS: list[tuple[str, str]] = [
    ("https://api.exchangerate-api.com/v4/latest/USD", "exchangerate-api"),
    ("https://open.er-api.com/v6/latest/USD", "open-er-api"),
]


class CurrencyConverter(ConverterBase):
    """Converts between currencies using cached or fetched exchange rates."""

    def __init__(self, cache_dir: str | Path = None) -> None:
        self._rates: dict[str, float] = {}
        self._loaded_at: float = 0.0
        self._expired: bool = False
        self._source: str = ""
        self._manual_overrides: dict[str, float] = {}

        # Determine cache path
        if cache_dir is None:
            self._cache_path = Path(__file__).resolve().parent.parent / "data" / "rates_cache.json"
        else:
            self._cache_path = Path(cache_dir) / "rates_cache.json"
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Load cached rates on init
        self._load_cache()

    @property
    def is_expired(self) -> bool:
        """Whether the current cached rates have expired."""
        return self._expired

    @property
    def source(self) -> str:
        """Source of the currently loaded rates."""
        return self._source

    @property
    def fetched_at(self) -> datetime | None:
        """When rates were last fetched/loaded."""
        if self._loaded_at == 0.0:
            return None
        return datetime.fromtimestamp(self._loaded_at, tz=timezone.utc)

    def get_units(self) -> list[str]:
        """Return supported currencies."""
        units = list(self._rates.keys())
        # Ensure base currency (USD) is always first
        if "USD" not in units:
            units.insert(0, "USD")
        return units

    def convert(self, amount: float, from_ccy: str, to_ccy: str) -> float:
        """Convert amount from one currency to another.

        Uses USD as the base intermediate currency.

        Args:
            amount: Amount to convert.
            from_ccy: Source currency code (e.g., "USD").
            to_ccy: Target currency code (e.g., "EUR").

        Returns:
            Converted amount as float, rounded to 4 decimal places.

        Raises:
            ValueError: If rate data is unavailable or currencies are unknown.
        """
        if from_ccy == to_ccy:
            return round(amount, 4)

        if not self._rates:
            raise ValueError("No rate data available. Fetch rates first or use the app online.")

        if from_ccy not in self._rates and from_ccy != "USD":
            raise ValueError(f"Unknown currency: '{from_ccy}'. Supported: {list(self._rates.keys())}")
        if to_ccy not in self._rates and to_ccy != "USD":
            raise ValueError(f"Unknown currency: '{to_ccy}'. Supported: {list(self._rates.keys())}")

        # Convert via USD base
        if from_ccy == "USD":
            from_rate = 1.0
        else:
            # rates store how much of each currency per 1 USD
            from_rate = 1.0 / self._rates[from_ccy]

        to_rate = self._rates[to_ccy] if to_ccy in self._rates else None
        if to_rate is None and to_ccy == "USD":
            to_rate = 1.0
        elif to_rate is None:
            raise ValueError(f"Unknown target currency: '{to_ccy}'")

        result = amount * from_rate * to_rate
        return round(result, 4)

    def get_rate(self, ccy: str) -> float | None:
        """Get the rate of a currency against USD.

        Args:
            ccy: Currency code (e.g., "EUR").

        Returns:
            Rate as float or None if not found.
        """
        if ccy == "USD":
            return 1.0
        # Check manual overrides first
        if ccy in self._manual_overrides:
            return self._manual_overrides[ccy]
        return self._rates.get(ccy)

    def manual_rate(self, ccy: str, rate: float) -> None:
        """Set a manual exchange rate override for a currency.

        Args:
            ccy: Currency code to override.
            rate: Custom rate per 1 USD.
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")
        self._manual_overrides[ccy] = rate

    def remove_manual_rate(self, ccy: str) -> None:
        """Remove a manual override for a currency."""
        self._manual_overrides.pop(ccy, None)

    def fetch_rates(self) -> dict[str, float]:
        """Fetch fresh exchange rates from online API.

        Tries configured APIs in order. Falls back through the list on failure.

        Returns:
            Dictionary of currency codes to rates (per 1 USD).

        Raises:
            ConnectionError: If all rate sources are unavailable.
        """
        import requests  # type: ignore[import-untyped]  # requests is a declared dependency

        for url, api_name in RATE_APIS:
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()

                # Parse rates from API response (handles different response formats)
                rates = data.get("rates", {})
                if not rates:
                    # Some APIs wrap rates under a different key
                    base_key = list(data.keys())[0] if data else None
                    if base_key and isinstance(data[base_key], dict):
                        rates = data[base_key].get("rates", data[base_key])

                if not rates:
                    continue

                # Normalize rates (all should be per 1 USD)
                self._rates = {k: float(v) for k, v in rates.items() if isinstance(v, (int, float))}
                self._loaded_at = time.time()
                self._expired = False
                self._source = api_name

                # Save to cache file
                self._save_cache()

                return dict(self._rates)

            except (requests.RequestException, json.JSONDecodeError, KeyError, ValueError):
                continue  # Try next API

        raise ConnectionError(
            "All rate sources unavailable. Using cached rates instead. "
            "Check your internet connection and try again."
        )

    def _load_cache(self) -> None:
        """Load exchange rates from the local cache file."""
        if not self._cache_path.exists():
            return

        try:
            with open(self._cache_path, "r") as f:
                data = json.load(f)

            expires_at_str = data.get("expires_at", "")
            if expires_at_str:
                # Parse the stored expiry timestamp
                expires_ts = datetime.fromisoformat(expires_at_str).timestamp()
                # Load with expiry flag; will be refreshed on next conversion attempt
                self._rates = {k: float(v) for k, v in data.get("rates", {}).items()}
                if self._rates:
                    self._expired = time.time() > expires_ts
                    self._source = data.get("source", "unknown")

        except (json.JSONDecodeError, OSError):
            # Corrupted cache — ignore silently
            pass

    def _save_cache(self) -> None:
        """Save current rates to the local cache file with expiry timestamp."""
        if not self._rates:
            return

        try:
            from config.settings_loader import get_settings
            settings = get_settings()
            expiry_hours = settings.get("rate_expiry_hours", 24)
        except (ImportError, KeyError):
            expiry_hours = 24

        data = {
            "rates": {k: float(v) for k, v in self._rates.items()},
            "expires_at": datetime.fromtimestamp(
                time.time() + (expiry_hours * 3600), tz=timezone.utc
            ).isoformat(),
            "source": self._source,
        }

        with open(self._cache_path, "w") as f:
            json.dump(data, f, indent=4)


# Singleton instance for app-wide use
_converter_instance: CurrencyConverter | None = None


def get_currency_converter() -> CurrencyConverter:
    """Get or create the singleton currency converter instance."""
    global _converter_instance
    if _converter_instance is None:
        _converter_instance = CurrencyConverter()
    return _converter_instance
