"""
Filename: searcher.py

Description:
    Axial-shake generator random search optimization tool
    to optimize (v_rms)^2/resistance ratio 
    
    NOTE:
    Uses a simplified model for the generator from evaluator.py
"""

import random

from pathlib import Path
from pyfea.domain.units import Q, Parser
from pyfea import mm, watt

from evaluator import build_generator, simulate_resistance, simulate_rms_voltage

def evaluate_design(params: list[Q]) -> Q:
    """ Evaluates the new proposed design """
    model.update_parameters(params[0], params[1])
    
    # Attempt proposed design if fails returns 0 watts
    try:
        resistance = simulate_resistance(solver_folder, model, False)
        v_rms = simulate_rms_voltage(solver_folder, model, False)[0]
        return v_rms**2 / resistance

    except Exception:
        return 0 * watt


# Imports parameters from .uiv parameter file with units
BASE_DIR = Path(__file__).parent.parent
para_dir = BASE_DIR / "parameters.uiv"
solver_folder = BASE_DIR / "FEM/outputs"

# Imports the parameters (value:unit) into memory & builds model
parameters = Parser.open(para_dir)
model = build_generator(parameters)

"""  ====== SEARCH PARAMETERS ======  """
number_of_iterations = 100
step_size = 5 * mm
max_stalls = 10                
stall = 0

Convergence = 0.1 * mm

max_radius = 10 * mm 

wire_diameter = parameters.stator_slots.wire_diameter
max_radial_thickness = max_radius - model.slot_inner_radius

axial_bound = (wire_diameter, parameters.armature_poles.axial_length)
radial_bound = (wire_diameter, max_radial_thickness)

# Initial best design parameters
current_params = (parameters.stator_slots.axial_length, parameters.stator_slots.radial_thickness)

best_objective = evaluate_design(current_params)
for iteration in range(1, number_of_iterations):
    axial_nudge = random.uniform(-1, 1) * step_size
    radial_nudge = random.uniform(-1, 1) * step_size
    
    # Calculate proposed parameters
    new_axial = max(axial_bound[0], min(axial_bound[1], current_params[0] + axial_nudge))
    new_radial = max(radial_bound[0], min(radial_bound[1], current_params[1] + radial_nudge))
    
    new_params = (new_axial, new_radial)
    
    f_new = evaluate_design(new_params)
    stall += 1
    
    # Check if the new design is better -> just better than last
    if f_new > best_objective:
        best_objective = f_new
        current_params = new_params
        stall = 0
        print(f"Iteration {iteration}: Improvement found :0 Obj: {best_objective:.4f} | "
              f"Axial: {new_params[0]:.2f}, Radial: {new_params[1]:.2f}")
    
    # Check for stall condition -> stall (reduces size for better searching in that new space)
    if stall >= max_stalls:
        step_size /= 2
        stall = 0
        print(f"Iteration {iteration}: Stalled. Reducing step size to {step_size}")
        
    # Convergence criteria -> too small step size
    if step_size < 0.001 * mm:
        print("Convergence threshold reached. Ending search.")
        break