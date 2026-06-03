# Offline Unit & Currency Converter

A desktop GUI application that converts **18 categories of physical units** and currency exchange rates. Works fully offline with optional online rate updates via free APIs.

## Features

- **Universal Unit Conversion — 18 Categories:**
  - **Length:** mm, cm, m, km, inch, foot, yard, mile (8 units)
  - **Weight:** mg, g, kg, oz, lb, ton (6 units)
  - **Temperature:** Celsius, Fahrenheit, Kelvin (3 units)
  - **Area:** sq mm, sq cm, sq m, sq km, sq ft, sq yard, acre, hectare, sq mile (9 units)
  - **Volume:** mL, L, cup/tbsp/tsp/fl oz/pt/qt/gal (US + UK), cc, cubic meter, cubic foot, US dry cup/pint/quart (24 units)
  - **Speed:** m/s, km/h, mph, knots, ft/s, mach (6 units)
  - **Time:** ms, s, min, hr, day, week, month, year (8 units)
  - **Digital Storage:** bit, byte, KB/MB/GB/TB/PB (SI decimal), Kib/Mib/Gib/Tib/Pib (IEC binary) (12 units)
  - **Pressure:** Pa, kPa, MPa, bar, mbar, atm, psi, torr/mmHg, inHg (10 units)
  - **Energy/Work:** J, kJ, cal, kcal, Wh, kWh, BTU, ft-lbf, eV (9 units)
  - **Power:** W, kW, MW, hp, BTU/hr, ft-lbf/min, cal/s (7 units)
  - **Force:** N, kN, lbf, dyne, kgf, gf (6 units)
  - **Angle:** deg, rad, grad, arcmin, arcsec, turn (6 units)
  - **Fuel Economy:** MPG (US), MPG (UK), L/100km, km/L (4 units — inverse conversion)
  - **Data Transfer Rate:** bps, Kbps, Mbps, Gbps, Tbps, Kibps, Mibps (7 units)
  - **Frequency:** Hz, kHz, MHz, GHz, RPM (5 units)
  - **Torque:** N·m, kN·m, lb·ft, kgf·m, oz·in (5 units)
  - **Density:** kg/m³, g/cm³, lb/ft³, lb/gal (4 units)
- **Currency Conversion:** 8 major currencies — real-time conversion with offline caching
- **Offline-First:** Cached exchange rates persist locally (24h expiry) — works anywhere without internet
- **Online Refresh:** Auto-detects connectivity; fetches fresh rates when connected
- **Dark Theme:** Modern CustomTkinter dark UI with dual-tab interface
- **Cross-Platform:** Windows, macOS, Linux

## Requirements

- Python 3.10+
- pip install requests customtkinter

## Installation

```bash
pip install requests customtkinter
```

## Usage

```bash
python main.py
```

Two tabs:
1. **Unit Converter** — Select from 18 categories via segmented button, choose from/to units, type amount for real-time conversion
2. **Currency Converter** — Select from/to currencies, enter amount. Shows live rates with online/offline status indicator

## Architecture

```
offline_converter/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/
│   ├── settings.json       # App configuration
│   └── settings_loader.py  # Settings loader with fallback defaults
├── converters/
│   ├── base.py                    # ABC interface contract
│   ├── unit_converter.py          # Universal converter: 18 categories, ~450+ units total
│   └── currency_converter.py      # Rate fetching + caching
├── gui/
│   ├── theme.py            # Dark theme config
│   ├── unit_tab.py         # Unit converter GUI tab
│   └── currency_tab.py     # Currency converter GUI tab
├── data/
│   └── rates_cache.json    # Persisted exchange rate cache (auto-created)
└── utils/
    ├── clipboard_helper.py  # Cross-platform copy to clipboard
    └── network_check.py     # Connectivity checker
```

## License

MIT
