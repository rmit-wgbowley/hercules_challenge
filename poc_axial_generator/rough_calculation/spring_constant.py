"""
Filename: spring_constant.py

Description:
    Rough analytical model for the POC_AXIAL_GENERATOR using
    the expected shaking frequency & acceleration to tune it
    such that it resonants (FOR SPRINGS ONLY)
    
    NOTE:
    Simplistic model using analytical equations not geometric
    models.
"""

from math import pi
from pathlib import Path

from pyfea import Q, unit_validator, Hz, s, kg, mm, g, cm
from pyfea.domain.units import Parser
from pyfea.domain.materials.manager import MaterialManager

# Imports parameters from .uiv parameter file with units
BASE_DIR = Path(__file__).parent.parent
para_dir = BASE_DIR / "parameters.uiv"

parameters = Parser.open(para_dir)
manager = MaterialManager()

@unit_validator(kg/s ** 2)
def calculate_k_total(frequency: Q, mass: Q) -> Q:
    """ Calculates the total spring constant of the system """
    return mass * (frequency*2*pi) ** 2

# Magnet length & mass
material_name = parameters.armature_poles.material
length = parameters.armature_poles.axial_length
radius = parameters.armature_poles.radial_thickness

magnet_material = manager.use_material(material_name, grade=parameters.armature_poles.grade)

magnet_volume = pi * radius**2 * length
mass_per_magnet = magnet_volume * magnet_material.NdFeB.physical.density
 
number_poles = 2 * parameters.model.number_pairs
mass = mass_per_magnet * number_poles
print(f"Mass core: {mass:.3f} @ {number_poles}")

# Core housing length & mass
length = parameters.armature_poles.axial_length * number_poles + 10 * mm
radius = parameters.armature_poles.radial_thickness + 2 * mm

housing_volume = pi * radius ** 2 * length - magnet_volume
housing_mass = 1.24 * (g/cm**3) * housing_volume
mass = mass + housing_mass
print(f"Armature mass (housing+core): {mass:.3f} with housing: {housing_mass:.3f}")

for frequency in range(0,10):
    k_total = calculate_k_total(frequency * Hz, mass)
    print(f"k_total: 2 x {k_total/2:.3f} @ frequency: {frequency * Hz:.3f}")

    