"""
Filename: main.py

Description:
    Axial-shake generator using pyfea for magnetics and lumped 
    parameter model for electro and mechanical domains.
    
    NOTE:
    Uses a simplified model for the shaking of the human to 
    reduce numerical complexity.
"""

import matplotlib.pyplot as plt

from math import pi
from pathlib import Path
from pyfea import Q, s, m, nullset, millisecond
from pyfea.domain.units import Parser
from pyfea.solver.femm.domains.magnetostatic.solver import FEMMMagnetostaticSolver
from pyfea.solver.solver_outputs import SolverOutputs, CircuitOptions

from model.generator import AxialShakeGenerator


# Imports parameters from .uiv parameter file with units
BASE_DIR = Path(__file__).parent.parent
para_dir = BASE_DIR / "parameters.uiv"
solver_folder = BASE_DIR / "FEM/outputs"

# Imports the parameters (value:unit) into memory
parameters = Parser.open(para_dir)

# Initializes model & magnetic solver
model = AxialShakeGenerator(parameters)
magnetic = FEMMMagnetostaticSolver(solver_folder, verbose=False)

# Builds magnetic domain & translates it into solver
domain, armature = model.construct_domain(magnetic)
magnetic.setup(domain)

# Selecting outputs (induced = -d(Flux linkage)/dt)
outputs = SolverOutputs()
outputs.add_circuit(model.PHASE, CircuitOptions.flux_linkage)

# Initial flux_linkage
results = magnetic.solve(outputs)
old_flux_linkage = results[model.PHASE].flux_linkage

# Human shake (simplified z(t) motion)
max_acceleration = parameters.model.acceleration_max
frequency = parameters.model.shaking_frequency

def z_axial_position(t: Q) -> Q:
    """ Assumes that the initial position equals z=0 """
    return - max_acceleration / (2*pi*frequency) ** 2 * (2*frequency*t).sin()

# Simulation Loop
time_step = parameters.numerical.time_step
t, z = 0 * s, 0 * m

t_set = []
v_set = []

iteration = 0 

while t < 500 * millisecond:
    if iteration % 10 == 0:
        print(f"UPDATED | Time: {t:.3f}, Pos: {z:.3f}")
    
    # Moves elements within the simulation & gets new linkage
    new_z_axial_position = z_axial_position(t)
    z_delta = new_z_axial_position - z
    
    magnetic.move_element(armature[0], z_delta, 90 * nullset)
    results = magnetic.solve(outputs)
    new_flux_linkage = results[model.PHASE].flux_linkage
    
    # Calculates the induced voltage within the phase
    dF = new_flux_linkage - old_flux_linkage
    induced = - dF/time_step
    
    t_set.append(t.value)
    v_set.append(induced.value)
    
    old_flux_linkage = new_flux_linkage 
    z = new_z_axial_position
    t += time_step
    
    iteration += 1

print(f"Simulation Complete. Total steps: {len(t_set)}") 

plt.figure(figsize=(9, 5))
plt.plot(t_set, v_set, color='#1f77b4', linewidth=2, label='Phase Induced Voltage')

plt.title(
    'Axial-Shake Generator Simulation: Induced Voltage vs Time', 
    fontsize=12, fontweight='bold', pad=15
)
plt.xlabel('Time (s)', fontsize=10)
plt.ylabel('Induced Voltage (V)', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper right')

plt.tight_layout()
plt.savefig(solver_folder / "induced_voltage_plot.png", dpi=150)
plt.show()