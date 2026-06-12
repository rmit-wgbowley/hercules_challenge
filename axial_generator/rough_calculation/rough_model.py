"""
Filename: rough_model.py

Description:
    Rough analytical model for the POC_AXIAL_GENERATOR using
    potential energy & efficiency factor.
    
    This MODEL is based on energy converted over a displacement
    at a specific CONSTANT acceleration. It is a rough approximation.
    
    NOTE:
    Rebound dynamics may increase energy generated per shake but
    may not.
"""

from math import pi
from pathlib import Path

from pyfea import mm, m, s, joule
from pyfea.domain.units import Parser
from pyfea.domain.materials.manager import MaterialManager

# Imports parameters from .uiv parameter file with units
BASE_DIR = Path(__file__).parent.parent
para_dir = BASE_DIR / "parameters.uiv"

parameters = Parser.open(para_dir)
manager = MaterialManager()


# Magnet length & mass
material_name = parameters.armature_poles.material
number_poles = parameters.model.number_pairs

length = parameters.armature_poles.axial_length * parameters.model.number_pairs * 2
radius = parameters.armature_poles.radial_thickness

magnet_material = manager.use_material(material_name, grade=parameters.armature_poles.grade)

density = magnet_material.NdFeB.physical.density
volume = length * radius ** 2 * pi

mass = volume * density
print(f"Magnet core mass: {mass:3f} @ density: {density:3f}")


# Calculate potential energy @ different accelerations over 2 pole pairs
movement_length = 50 * mm
energy_required = 10 * joule
efficiency = parameters.model.cycling_efficiency
frequency = parameters.model.shaking_frequency

acceleration = 5 * (m / s**2)
print(f"Efficiency: {efficiency:.3f}, Movement_length: {movement_length:.3f}, frequency: {frequency:.3f}")

for i in range(0, 10):
    potential = acceleration * movement_length * mass
    usable_potential = potential * efficiency
    number_of_shakes = energy_required/usable_potential

    time = number_of_shakes / frequency

    print(f"Max: {potential:.3f}, Usable: {usable_potential:.3f} @ {acceleration:.3f}")
    # print(f"Number of shakes: {energy_required/usable_potential:.3f} for target: {energy_required:.3f}")
    # print(f'Time to fully operation: {time:.3f} @ {frequency}')
    print(f"Energy gain per second: {usable_potential * (frequency.stripped):.3f}")
    acceleration += 5 * (m / s**2)
