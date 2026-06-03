import sys
sys.path.insert(0, '.')
from converters.unit_converter import UnitConverter

c = UnitConverter()
tests = [
    ("Length", 100, "km", "mile", 62.1371, 0.01),
    ("Area", 1, "sq_km", "acre", 247.1054, 0.01),
    ("Speed", 60, "mph", "knots", 52.1386, 0.01),
    ("Fuel Economy", 30, "mpg_us", "l100km", 7.8405, 0.01),
    ("Digital Storage", 1, "GB", "Gib", 0.931322, 0.0001),
    ("Temperature", 37, "Celsius", "Fahrenheit", 98.6, 0.01),
    ("Torque", 2, "kgf_m", "nm", 19.6133, 0.01),
    ("Angle", 180, "deg", "rad", 3.141593, 0.0001),
    ("Energy / Work", 1, "kwh", "kcal", 860.42065, 0.01),
    ("Force", 1, "lbf", "n", 4.44822, 0.001),
    ("Pressure", 1, "atm", "psi", 14.6959, 0.001),
    ("Frequency", 1, "ghz", "mhz", 1000.0, 0.01),
    ("Volume", 100, "gal_us", "l", 378.5412, 0.01),
    ("Power", 1, "hp", "kw", 0.7457, 0.0001),
]

pass_count = 0
fail_count = 0
for cat, val, fu, tu, expected, tol in tests:
    result = c.convert(val, fu, tu)
    status = "OK" if abs(result - expected) < tol else "FAIL"
    if status == "OK":
        pass_count += 1
    else:
        fail_count += 1
    print(f"[{status}] {cat}: {val} {fu} -> {result} (expected ~{expected})")

print(f"\nResults: {pass_count}/{len(tests)} passed, {fail_count} failed")
