"""Universal unit converter — Area, Volume, Speed, Time, Digital Storage, Pressure, Energy, Power, Force, Angle, Fuel Economy, Data Transfer, Frequency, Torque, Density.

All conversion logic uses base-unit multiplicative routing except Temperature and Fuel Economy which require special-case handling."""

import math

from converters.base import ConverterBase


# ---------------------------------------------------------------------------
# LENGTH — base = meter (m)
# ---------------------------------------------------------------------------
LENGTH_UNITS: dict[str, float] = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1_000.0,
    "inch": 0.0254,
    "foot": 0.3048,
    "yard": 0.9144,
    "mile": 1_609.344,
}

# ---------------------------------------------------------------------------
# WEIGHT — base = gram (g)
# ---------------------------------------------------------------------------
WEIGHT_UNITS: dict[str, float] = {
    "mg": 0.001,
    "g": 1.0,
    "kg": 1_000.0,
    "oz": 28.3495,
    "lb": 453.592,
    "ton": 907_184.74,
}

# ---------------------------------------------------------------------------
# AREA — base = square meter (m²)
# ---------------------------------------------------------------------------
AREA_UNITS: dict[str, float] = {
    # Metric
    "sq_mm": 1e-6,
    "sq_cm": 1e-4,
    "sq_m": 1.0,
    "sq_km": 1_000_000.0,
    # Imperial / US customary
    "sq_in": 0.00064516,
    "sq_ft": 0.09290304,
    "sq_yd": 0.83612736,
    "sq_mi": 2_589_988.110336,
    # Land / large-area
    "acre": 4046.8564224,
    "hectare": 10_000.0,
}

# ---------------------------------------------------------------------------
# VOLUME — base = cubic meter (m³)
# ---------------------------------------------------------------------------
VOLUME_UNITS: dict[str, float] = {
    # Metric
    "ml": 1e-6,
    "cl": 1e-5,
    "dl": 1e-4,
    "l": 0.001,
    "hl": 0.1,
    "m3": 1.0,
    # US liquid
    "cup_us": 0.0002365882365,
    "tbsp_us": 0.00001478676478,
    "tsp_us": 0.000004928921593,
    "fl_oz_us": 0.00002957352956,
    "pt_us": 0.000473176473,
    "qt_us": 0.000946352946,
    "gal_us": 0.003785411784,
    # UK (Imperial) liquid
    "cup_uk": 0.000284130625,
    "tbsp_uk": 0.00001775816406,
    "tsp_uk": 0.00000591938802,
    "fl_oz_uk": 0.0000284130625,
    "pt_uk": 0.00056826125,
    "gal_uk": 0.00454609,
    # US dry
    "cup_dry_us": 0.000220009178,
    "pt_dry_us": 0.00055057683,
    "qt_dry_us": 0.0011011544,
    # SI / metric volume for solids
    "cc": 1e-6,
}

# ---------------------------------------------------------------------------
# SPEED — base = meters per second (m/s)
# ---------------------------------------------------------------------------
SPEED_UNITS: dict[str, float] = {
    "ms": 1.0,
    "kmh": 0.277777778,
    "mph": 0.44704,
    "knots": 0.514444444,
    "fts": 0.3048,
    "mach": 343.0,          # at sea level, 20 °C (approx)
}

# ---------------------------------------------------------------------------
# TIME — base = second (s)
# ---------------------------------------------------------------------------
TIME_UNITS: dict[str, float] = {
    "ms": 0.001,
    "s": 1.0,
    "min": 60.0,
    "hr": 3600.0,
    "day": 86_400.0,
    "week": 604_800.0,
    "month": 2_629_746.0,   # average (365.25/12 days)
    "year": 31_556_952.0,   # Julian year (365.25 days)
}

# ---------------------------------------------------------------------------
# DIGITAL STORAGE — two parallel tables: SI (decimal) and IEC (binary)
# ---------------------------------------------------------------------------
DIGITAL_SI_UNITS: dict[str, float] = {
    "bit": 1 / 8,            # base = byte (SI defines 1 byte = 8 bits)
    "B": 1.0,
    "KB": 1_000.0,
    "MB": 1_000_000.0,
    "GB": 1_000_000_000.0,
    "TB": 1_000_000_000_000.0,
    "PB": 1_000_000_000_000_000.0,
}

DIGITAL_IEC_UNITS: dict[str, float] = {
    "bit": 1 / 8,
    "B": 1.0,
    "Kib": 1_024.0,
    "Mib": 1_048_576.0,
    "Gib": 1_073_741_824.0,
    "Tib": 1_099_511_627_776.0,
    "Pib": 1_125_899_906_842_624.0,
}

DIGITAL_ALL_UNITS: dict[str, tuple] = {
    **{u: ("si", v) for u, v in DIGITAL_SI_UNITS.items()},
    **{u: ("iec", v) for u, v in DIGITAL_IEC_UNITS.items() if u not in ("bit", "B")},  # bit/B already in SI
}

DIGITAL_DISPLAY: dict[str, str] = {
    "bit": "Bit (b)",
    "B": "Byte (B)",
    "KB": "Kilobyte (KB, 1e3 B)",
    "MB": "Megabyte (MB, 1e6 B)",
    "GB": "Gigabyte (GB, 1e9 B)",
    "TB": "Terabyte (TB, 1e12 B)",
    "PB": "Petabyte (PB, 1e15 B)",
    "Kib": "Kibibyte (KiB, 2¹⁰ B)",
    "Mib": "Mebibyte (MiB, 2²⁰ B)",
    "Gib": "Gibibyte (GiB, 2³⁰ B)",
    "Tib": "Tebibyte (TiB, 2⁴⁰ B)",
    "Pib": "Pebibyte (PiB, 2⁵⁰ B)",
}

# ---------------------------------------------------------------------------
# PRESSURE — base = pascal (Pa)
# ---------------------------------------------------------------------------
PRESSURE_UNITS: dict[str, float] = {
    "Pa": 1.0,
    "kPa": 1_000.0,
    "MPa": 1_000_000.0,
    "bar": 100_000.0,
    "mbar": 100.0,
    "atm": 101_325.0,
    "psi": 6894.757293168,
    "torr": 133.322368421,
    "mmhg": 133.322368421,   # same as torr
    "inhg": 3386.388675909,
}

# ---------------------------------------------------------------------------
# ENERGY / WORK — base = joule (J)
# ---------------------------------------------------------------------------
ENERGY_UNITS: dict[str, float] = {
    "j": 1.0,
    "kj": 1_000.0,
    "cal": 4.184,             # thermochemical calorie
    "kcal": 4_184.0,          # nutritional Calorie (capital C in nutrition = kcal)
    "wh": 3600.0,
    "kwh": 3_600_000.0,
    "btu": 1055.05585262,     # international table BTU
    "ftlbf": 1.3558179483314, # foot-pound force
    "ev": 1.602_176_634e-19,  # electronvolt (physics)
}

# ---------------------------------------------------------------------------
# POWER — base = watt (W)
# ---------------------------------------------------------------------------
POWER_UNITS: dict[str, float] = {
    "w": 1.0,
    "mw": 1_000_000.0,
    "kw": 1_000.0,
    "hp": 745.69987158227022,     # mechanical horsepower
    "btu_hr": 0.293071070172,      # BTU per hour
    "ftlbf_min": 0.022596965805,   # foot-pound force per minute
    "cal_s": 4.184,                # calories per second
}

# ---------------------------------------------------------------------------
# FORCE — base = newton (N)
# ---------------------------------------------------------------------------
FORCE_UNITS: dict[str, float] = {
    "n": 1.0,
    "kn": 1_000.0,
    "lbf": 4.4482216152605,        # pound-force
    "dyne": 1e-5,                  # CGS unit
    "kgf": 9.80665,                # kilogram-force (standard gravity)
    "gf": 0.00980665,              # gram-force
}

# ---------------------------------------------------------------------------
# ANGLE — base = degree (°)
# ---------------------------------------------------------------------------
ANGLE_UNITS: dict[str, float] = {
    "deg": 1.0,
    "rad": 57.29577951308232,      # 180 / pi
    "grad": 0.9,                    # 400 grads = 360 deg
    "arcmin": 1 / 60,              # arcminute
    "arcsec": 1 / 3600,            # arcsecond
    "turn": 360.0,                 # full rotation
}

# ---------------------------------------------------------------------------
# FUEL ECONOMY — special case: inverses of each other
#   Conversions via MPG (US) as the pivot, then to L/100km
#   MPG(US) = distance(miles) / fuel(gallons_US)
#   L/100km = 235.214583 / MPG(US)
# ---------------------------------------------------------------------------
FUEL_ECONOMY_UNITS: list[str] = [
    "mpg_us", "mpg_uk", "l100km", "km_l",
]

# Conversion factors to L/100km as the normalised pivot (lower = more efficient)
# Actually we use MPG_US as pivot since it's the most common
_FUEL_TO_MPG: dict[str, float] = {
    "mpg_us": 1.0,
    "mpg_uk": 1.20095,            # 1 UK gallon ≈ 1.20095 US gallons → higher MPG number
    "l100km": None,               # special inverse formula below
    "km_l": None,                 # km per liter → convert to MPG via factor
}

_FUEL_KML_TO_MPG = 2.35214583   # km/L × 2.352... ≈ MPG(US)


def _fuel_to_mpg(unit: str, value: float) -> float:
    """Convert fuel economy unit to US MPG as pivot."""
    if unit == "mpg_us":
        return value
    if unit == "mpg_uk":
        # UK gallon is 4.54609 L vs US gallon 3.78541 L → 1 mpg_uk = 1.20095 mpg_us
        return value * _FUEL_TO_MPG["mpg_uk"]
    if unit == "l100km":
        # MPG = 235.214583 / (L/100km)
        if value <= 0:
            raise ValueError("Fuel consumption must be positive for L/100km conversion")
        return 235.214583 / value
    if unit == "km_l":
        # km/L to MPG(US): multiply by 2.35214583
        return value * _FUEL_KML_TO_MPG
    raise ValueError(f"Unknown fuel economy unit: '{unit}'")


def _mpg_to_fuel(mpg: float, target_unit: str) -> float:
    """Convert US MPG to target fuel economy unit."""
    if target_unit == "mpg_us":
        return mpg
    if target_unit == "mpg_uk":
        return mpg / _FUEL_TO_MPG["mpg_uk"]
    if target_unit == "l100km":
        # L/100km = 235.214583 / MPG(US)
        if mpg <= 0:
            raise ValueError("Fuel efficiency must be positive")
        return round(235.214583 / mpg, 4)
    if target_unit == "km_l":
        # km/L = MPG(US) / 2.35214583
        if mpg <= 0:
            raise ValueError("Fuel efficiency must be positive")
        return round(mpg / _FUEL_KML_TO_MPG, 4)
    raise ValueError(f"Unknown fuel economy unit: '{target_unit}'")


# ---------------------------------------------------------------------------
# DATA TRANSFER RATE — base = bits per second (bps)
# ---------------------------------------------------------------------------
DATA_TRANSFER_UNITS: dict[str, float] = {
    "bps": 1.0,
    "kbps": 1_000.0,
    "mbps": 1_000_000.0,
    "gbps": 1_000_000_000.0,
    "tbps": 1_000_000_000_000.0,
    "kibps": 1_024.0,     # kibibits per second
    "mibps": 1_048_576.0,  # mebibits per second
}

# ---------------------------------------------------------------------------
# FREQUENCY — base = hertz (Hz)
# ---------------------------------------------------------------------------
FREQUENCY_UNITS: dict[str, float] = {
    "hz": 1.0,
    "khz": 1_000.0,
    "mhz": 1_000_000.0,
    "ghz": 1_000_000_000.0,
    "rpm": 1 / 60.0,      # revolutions per minute → Hz (rev/s)
}

# ---------------------------------------------------------------------------
# TORQUE — base = newton-meter (N·m)
# ---------------------------------------------------------------------------
TORQUE_UNITS: dict[str, float] = {
    "nm": 1.0,
    "knm": 1_000.0,
    "lbf_ft": 1.3558179483314,   # pound-force foot
    "kgf_m": 9.80665,            # kilogram-force meter
    "oz_in": 0.007061551818,     # ounce-inch
}

# ---------------------------------------------------------------------------
# DENSITY — base = kg per cubic meter (kg/m³)
# ---------------------------------------------------------------------------
DENSITY_UNITS: dict[str, float] = {
    "kgm3": 1.0,
    "gcm3": 1_000.0,            # g/cm³ → 1e3 kg/m³
    "lbft3": 16.01846337,       # lb/ft³ → kg/m³
    "lbgal_us": 0.119826427,    # lb/gal (US) → kg/m³
}


# ---------------------------------------------------------------------------
# Unit converter display name maps
# ---------------------------------------------------------------------------
DISPLAY_MAP: dict[str, str] = {}

def _populate_display():
    """Build a comprehensive display name map for all unit codes."""
    global DISPLAY_MAP
    # Area
    AREA_DISPLAY = {
        "sq_mm": "Square Millimeter (mm²)",
        "sq_cm": "Square Centimeter (cm²)",
        "sq_m": "Square Meter (m²)",
        "sq_km": "Square Kilometer (km²)",
        "sq_in": "Square Inch (in²)",
        "sq_ft": "Square Foot (ft²)",
        "sq_yd": "Square Yard (yd²)",
        "sq_mi": "Square Mile (mi²)",
        "acre": "Acre",
        "hectare": "Hectare (ha)",
    }
    DISPLAY_MAP.update(AREA_DISPLAY)

    # Volume
    VOL_DISPLAY = {
        "ml": "Milliliter (mL)",
        "cl": "Centiliter (cL)",
        "dl": "Deciliter (dL)",
        "l": "Liter (L)",
        "hl": "Hectoliter (hL)",
        "m3": "Cubic Meter (m³)",
        "cup_us": "US Cup",
        "tbsp_us": "US Tablespoon",
        "tsp_us": "US Teaspoon",
        "fl_oz_us": "US Fluid Ounce (fl oz)",
        "pt_us": "US Pint (pt)",
        "qt_us": "US Quart (qt)",
        "gal_us": "US Gallon",
        "cup_uk": "UK Cup",
        "tbsp_uk": "UK Tablespoon",
        "tsp_uk": "UK Teaspoon",
        "fl_oz_uk": "UK Fluid Ounce (fl oz)",
        "pt_uk": "UK Pint (pt)",
        "gal_uk": "UK Gallon",
        "cup_dry_us": "US Dry Cup",
        "pt_dry_us": "US Dry Pint (pt dry)",
        "qt_dry_us": "US Dry Quart (qt dry)",
        "cc": "Cubic Centimeter / cc (mL)",
    }
    DISPLAY_MAP.update(VOL_DISPLAY)

    # Speed
    SPD_DISPLAY = {
        "ms": "Meters per Second (m/s)",
        "kmh": "Kilometers per Hour (km/h)",
        "mph": "Miles per Hour (mph)",
        "knots": "Knots (kn)",
        "fts": "Feet per Second (ft/s)",
        "mach": "Mach",
    }
    DISPLAY_MAP.update(SPD_DISPLAY)

    # Time
    TIM_DISPLAY = {
        "ms": "Millisecond (ms)",
        "s": "Second (s)",
        "min": "Minute (min)",
        "hr": "Hour (hr)",
        "day": "Day",
        "week": "Week",
        "month": "Month (avg, 30.44 days)",
        "year": "Year (365.25 days)",
    }
    DISPLAY_MAP.update(TIM_DISPLAY)

    # Digital Storage
    DISPLAY_MAP.update(DIGITAL_DISPLAY)

    # Pressure
    PRES_DISPLAY = {
        "Pa": "Pascal (Pa)",
        "kPa": "Kilopascal (kPa)",
        "MPa": "Megapascal (MPa)",
        "bar": "Bar",
        "mbar": "Millibar (mbar)",
        "atm": "Atmosphere (atm)",
        "psi": "Pounds per Square Inch (psi)",
        "torr": "Torr / mmHg",
        "mmhg": "Millimeter of Mercury (mmHg)",
        "inhg": "Inch of Mercury (inHg)",
    }
    DISPLAY_MAP.update(PRES_DISPLAY)

    # Energy
    ENG_DISPLAY = {
        "j": "Joule (J)",
        "kj": "Kilojoule (kJ)",
        "cal": "Calorie (cal, thermochemical)",
        "kcal": "Kilocalorie / Calorie (kcal, nutritional)",
        "wh": "Watt-hour (Wh)",
        "kwh": "Kilowatt-hour (kWh)",
        "btu": "BTU (international table)",
        "ftlbf": "Foot-Pound Force (ft·lbf)",
        "ev": "Electronvolt (eV)",
    }
    DISPLAY_MAP.update(ENG_DISPLAY)

    # Power
    PWR_DISPLAY = {
        "w": "Watt (W)",
        "kw": "Kilowatt (kW)",
        "mw": "Megawatt (MW)",
        "hp": "Horsepower (mechanical, hp)",
        "btu_hr": "BTU per Hour (BTU/hr)",
        "ftlbf_min": "Foot-Pound Force / Minute",
        "cal_s": "Calorie per Second (cal/s)",
    }
    DISPLAY_MAP.update(PWR_DISPLAY)

    # Force
    FOR_DISPLAY = {
        "n": "Newton (N)",
        "kn": "Kilonewton (kN)",
        "lbf": "Pound-Force (lbf)",
        "dyne": "Dyne (dyn, CGS)",
        "kgf": "Kilogram-Force (kgf)",
        "gf": "Gram-Force (gf)",
    }
    DISPLAY_MAP.update(FOR_DISPLAY)

    # Angle
    ANG_DISPLAY = {
        "deg": "Degree (°)",
        "rad": "Radian (rad)",
        "grad": "Gradian / Gon (gon)",
        "arcmin": "Arcminute (′)",
        "arcsec": "Arcsecond (″)",
        "turn": "Turn (full rotation, 360°)",
    }
    DISPLAY_MAP.update(ANG_DISPLAY)

    # Fuel Economy
    FUEL_DISPLAY = {
        "mpg_us": "MPG (US, miles per gallon)",
        "mpg_uk": "MPG (UK, imperial gallons)",
        "l100km": "L/100km (Liters per 100 km)",
        "km_l": "km/L (kilometers per liter)",
    }
    DISPLAY_MAP.update(FUEL_DISPLAY)

    # Data Transfer
    DAT_DISPLAY = {
        "bps": "Bits per Second (bps)",
        "kbps": "Kilobits per Second (Kbps)",
        "mbps": "Megabits per Second (Mbps)",
        "gbps": "Gigabits per Second (Gbps)",
        "tbps": "Terabits per Second (Tbps)",
        "kibps": "Kibibits per Second",
        "mibps": "Mebibits per Second",
    }
    DISPLAY_MAP.update(DAT_DISPLAY)

    # Frequency
    FREQ_DISPLAY = {
        "hz": "Hertz (Hz)",
        "khz": "Kilohertz (kHz)",
        "mhz": "Megahertz (MHz)",
        "ghz": "Gigahertz (GHz)",
        "rpm": "Revolutions per Minute (RPM)",
    }
    DISPLAY_MAP.update(FREQ_DISPLAY)

    # Torque
    TOR_DISPLAY = {
        "nm": "Newton-Meter (N·m)",
        "knm": "Kilonewton-Meter (kN·m)",
        "lbf_ft": "Pound-Force Foot (lb·ft)",
        "kgf_m": "Kilogram-Force Meter (kgf·m)",
        "oz_in": "Ounce-Inch (oz·in)",
    }
    DISPLAY_MAP.update(TOR_DISPLAY)

    # Density
    DEN_DISPLAY = {
        "kgm3": "Kilograms per Cubic Meter (kg/m³)",
        "gcm3": "Grams per Cubic Centimeter (g/cm³)",
        "lbft3": "Pounds per Cubic Foot (lb/ft³)",
        "lbgal_us": "Pounds per US Gallon (lb/gal)",
    }
    DISPLAY_MAP.update(DEN_DISPLAY)


_populate_display()


def _convert_via_base(units: dict[str, float], value: float, from_u: str, to_u: str) -> float:
    """Convert via base unit for multiplicative categories."""
    if from_u not in units:
        raise ValueError(f"Unknown unit: '{from_u}'.")
    if to_u not in units:
        raise ValueError(f"Unknown unit: '{to_u}'.")

    base_value = value * units[from_u]
    return base_value / units[to_u]


def _convert_temperature(value: float, from_u: str, to_u: str) -> float:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin."""
    if from_u == "Celsius":
        celsius = value
    elif from_u == "Fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_u == "Kelvin":
        celsius = value - 273.15
    else:
        raise ValueError(f"Unknown temperature unit: '{from_u}'")

    if to_u == "Celsius":
        return celsius
    elif to_u == "Fahrenheit":
        return celsius * 9 / 5 + 32
    elif to_u == "Kelvin":
        return celsius + 273.15
    else:
        raise ValueError(f"Unknown temperature unit: '{to_u}'")


def _convert_fuel_economy(value: float, from_u: str, to_u: str) -> float:
    """Convert fuel economy with inverse-unit handling."""
    if from_u == to_u:
        return round(value, 4)
    mpg = _fuel_to_mpg(from_u, value)
    return _mpg_to_fuel(mpg, to_u)


def _convert_digital_storage(value: float, from_u: str, to_u: str) -> float:
    """Convert digital storage between SI (decimal) and IEC (binary) prefixes."""
    if from_u == to_u:
        return round(value, 4)

    from_info = DIGITAL_ALL_UNITS.get(from_u)
    to_info = DIGITAL_ALL_UNITS.get(to_u)

    if not from_info or not to_info:
        raise ValueError(f"Unknown digital storage unit.")

    from_system, from_factor = from_info   # ('si'/'iec', factor_in_bytes)
    to_system, to_factor = to_info

    # Both are relative to byte as base — direct multiplicative conversion
    return value * (from_factor / to_factor)


class UnitConverter(ConverterBase):
    """Universal unit converter supporting 18+ categories."""

    CATEGORIES: dict[str, list[str]] = {
        "Length": list(LENGTH_UNITS.keys()),
        "Weight": list(WEIGHT_UNITS.keys()),
        "Temperature": ["Celsius", "Fahrenheit", "Kelvin"],
        "Area": list(AREA_UNITS.keys()),
        "Volume": list(VOLUME_UNITS.keys()),
        "Speed": list(SPEED_UNITS.keys()),
        "Time": list(TIME_UNITS.keys()),
        "Digital Storage": list(DIGITAL_ALL_UNITS.keys()),
        "Pressure": list(PRESSURE_UNITS.keys()),
        "Energy / Work": list(ENERGY_UNITS.keys()),
        "Power": list(POWER_UNITS.keys()),
        "Force": list(FORCE_UNITS.keys()),
        "Angle": list(ANGLE_UNITS.keys()),
        "Fuel Economy": list(FUEL_ECONOMY_UNITS),
        "Data Transfer Rate": list(DATA_TRANSFER_UNITS.keys()),
        "Frequency": list(FREQUENCY_UNITS.keys()),
        "Torque": list(TORQUE_UNITS.keys()),
        "Density": list(DENSITY_UNITS.keys()),
    }

    _CATEGORY_MAP: dict[str, str] = {}

    def __init__(self) -> None:
        self._category_map: dict[str, str] = {}
        for category, units in self.CATEGORIES.items():
            for unit in units:
                self._category_map[unit] = category
        super().__init__()

    def get_units(self, category: str | None = None) -> list[str]:
        """Return supported units, optionally filtered by category."""
        if category is None:
            return list(self.CATEGORIES.keys())
        return self.CATEGORIES.get(category, [])

    def get_all_units(self) -> dict[str, list[str]]:
        """Return all categories with their units."""
        return dict(self.CATEGORIES)

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert a value between two units of the same category.

        Args:
            value: The numeric value to convert.
            from_unit: Source unit code or name.
            to_unit: Target unit code or name.

        Returns:
            Converted value as float, rounded to 4 decimal places.

        Raises:
            ValueError: If units differ in category or are unknown.
        """
        if from_unit == to_unit:
            return round(value, 4)

        # Ensure both units belong to the same category
        from_category = self._category_map.get(from_unit)
        to_category = self._category_map.get(to_unit)

        if from_category is None:
            raise ValueError(f"Unknown unit: '{from_unit}'. Supported categories: {list(self.CATEGORIES.keys())}")
        if to_category is None:
            raise ValueError(f"Unknown unit: '{to_unit}'. Supported categories: {list(self.CATEGORIES.keys())}")
        if from_category != to_category:
            raise ValueError(
                f"Incompatible units: '{from_unit}' ({from_category}) vs "
                f"'{to_unit}' ({to_category}). Convert within the same category."
            )

        # Route to appropriate converter
        if from_category == "Temperature":
            result = _convert_temperature(value, from_unit, to_unit)
        elif from_category == "Fuel Economy":
            result = _convert_fuel_economy(value, from_unit, to_unit)
        elif from_category == "Digital Storage":
            result = _convert_digital_storage(value, from_unit, to_unit)
        else:
            units_map = self._get_units_map(from_category)
            if units_map is None:
                raise ValueError(f"No conversion table for category '{from_category}'")
            result = _convert_via_base(units_map, value, from_unit, to_unit)

        return round(result, 4)

    def _get_units_map(self, category: str) -> dict[str, float] | None:
        """Return the base-unit mapping for a given category."""
        if category == "Length":
            return LENGTH_UNITS
        if category == "Weight":
            return WEIGHT_UNITS
        if category == "Area":
            return AREA_UNITS
        if category == "Volume":
            return VOLUME_UNITS
        if category == "Speed":
            return SPEED_UNITS
        if category == "Time":
            return TIME_UNITS
        if category == "Pressure":
            return PRESSURE_UNITS
        if category == "Energy / Work":
            return ENERGY_UNITS
        if category == "Power":
            return POWER_UNITS
        if category == "Force":
            return FORCE_UNITS
        if category == "Angle":
            return ANGLE_UNITS
        if category == "Data Transfer Rate":
            return DATA_TRANSFER_UNITS
        if category == "Frequency":
            return FREQUENCY_UNITS
        if category == "Torque":
            return TORQUE_UNITS
        if category == "Density":
            return DENSITY_UNITS
        return None

    def get_category_for_unit(self, unit: str) -> str | None:
        """Get the category a unit belongs to."""
        return self._category_map.get(unit)

    def get_unit_code_display(self, unit: str) -> str:
        """Get display-friendly label for a unit."""
        return DISPLAY_MAP.get(unit, unit)
