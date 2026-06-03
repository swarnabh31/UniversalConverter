"""Base converter interface."""

from abc import ABC, abstractmethod


class ConverterBase(ABC):
    """Abstract base class for all converters."""

    @abstractmethod
    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert a value from one unit to another.

        Args:
            value: The numeric value to convert.
            from_unit: Source unit/currency code.
            to_unit: Target unit/currency code.

        Returns:
            Converted value as float.

        Raises:
            ValueError: If units are unknown or value is invalid.
        """
        ...

    @abstractmethod
    def get_units(self) -> list[str]:
        """Return list of supported units/currencies."""
        ...
