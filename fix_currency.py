import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\swarnabh\Desktop\Github_Projects\offline_converter\gui\currency_tab.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

replacements_made = 0

for i, line in enumerate(lines):
    # Fix 1: Replace hardcoded $ with currency symbol variable
    if '${value' in line and 'Result:' in line:
        old = line.strip()
        # This is the problematic line — needs a full rewrite
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + '''            self.result_label.configure(
                text_color="#6c63ff",
                text="Result: " + symbol_from + str(value) + " " + from_ccy + " => " + to_sym + str(result)
            )
'''
        replacements_made += 1
    # Fix 2: Replace all arrow chars with safe ASCII
    elif chr(0x2192) in line:
        lines[i] = line.replace(chr(0x2192), ' => ')
        replacements_made += 1

print(f"Replacements made: {replacements_made}")

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Now also fix the _convert method to use proper symbols and formatting
path2 = r'C:\Users\swarnabh\Desktop\Github_Projects\offline_converter\gui\currency_tab.py'
with open(path2, 'r', encoding='utf-8') as f:
    content = f.read()

# Show the current state around result display
idx = content.find('CURRENCY_SYMBOLS')
if idx == -1:
    print("No CURRENCY_SYMBOLS block found — will add one")
else:
    print("CURRENCY_SYMBOLS block already exists")
