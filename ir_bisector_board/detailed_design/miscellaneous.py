"""
Filename: miscellaneous.py

Description:
    Calculates the values for random components on the IR bi-sector
    boards.
    
    NOTE:
    - A03401 has a 10kOhm pull-up resistor.
"""

from picounits import VOLTAGE, RESISTANCE, POWER, MILLI, KILO

# System variables
vcc = 3.3 * VOLTAGE
r2 = 4.7 * KILO * RESISTANCE
mos_rds = 75 * MILLI * RESISTANCE

print(f"System Variables | vcc: {vcc:.3f}, mos_rds: {mos_rds:.3f}, r2_basis: {r2:.3f}")

# Arbitrary power restriction of 25mW 
max_power = 20 * MILLI * POWER
power_per_led = max_power / 3

print(f"Power per led: {power_per_led:.3f} | max @ {max_power:.3f}")

# Resistance to ensure that power per led
r1 = (vcc) ** 2 / power_per_led
print(f"Resistance per led {r1:.3f}")

# Calculates the resistance losses from the led resistor 
# and the basis resistor on the phototransistor
r1_loss = vcc ** 2 / r1
r2_loss = vcc ** 2 / r2

print(f"Per sensor losses | r1: {r1_loss:.3f}, r2: {r2_loss:.3f}")

# Calculates the resistance losses from the mosfet r_ds(on)
current_per_led = vcc / r1
total_load_current = current_per_led * 3

m1_loss = (total_load_current**2) * mos_rds

per_sensor = r1_loss + r2_loss
total_losses = per_sensor * 3 + m1_loss

print(f"Total bi-sector losses: {total_losses:.3f} | mosfet losses: {m1_loss:.3f}")