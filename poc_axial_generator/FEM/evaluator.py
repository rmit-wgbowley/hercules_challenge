"""
Filename: evaluator.py

Description:
    Axial-shake generator using pyfea for magnetics and lumped 
    parameter model for electro and mechanical domains.
    
    NOTE:
    Uses a simplified model for the shaking from the human to 
    reduce numerical complexity.
"""

from math import pi
from pathlib import Path
from pyfea.domain.units import Parser
from pyfea import Q, unit_validator, ampere, ohm, volt, second, meter, nullset

from pyfea.domain.units import DynamicLoader
from pyfea.solver.femm.domains.magnetostatic.solver import FEMMMagnetostaticSolver
from pyfea.solver.solver_outputs import SolverOutputs, CircuitOptions

from model.generator import AxialShakeGenerator


def build_generator(parameters: DynamicLoader) -> AxialShakeGenerator:
    """ Builds the generator based on the parameter file"""
    travel = 2 * parameters.armature_poles.axial_length
    model = AxialShakeGenerator(parameters, travel)
    
    return model


@unit_validator(ohm)
def simulate_resistance(folder: Path, model: AxialShakeGenerator, verbose: bool = False) -> Q:
    """ Simulate the resistance of the generator using a test current """
    magnetic = FEMMMagnetostaticSolver(folder, verbose=verbose)

    # Builds magnetic domain & translates it into solver
    domain, _ = model.construct_domain(magnetic)
    magnetic.setup(domain)
    model.PHASE.current = 0.1 * ampere
    magnetic.update_current(model.PHASE)

    # Selecting outputs (induced = -d(Flux linkage)/dt)
    outputs = SolverOutputs()
    outputs.add_circuit(model.PHASE, CircuitOptions.resistance)

    # Initial flux_linkage
    results = magnetic.solve(outputs)
    resistance = results[model.PHASE].resistance

    model.PHASE.current = 0.0 * ampere
    return resistance


def simulate_rms_voltage(
    folder: Path, model: AxialShakeGenerator, verbose: bool = False
) -> tuple[Q, list]:
    """ Simulates the v_rms of the generator using co-simulation"""
    parameters = model.params
    magnetic = FEMMMagnetostaticSolver(folder, verbose=verbose)
    
    # Builds magnetic domain & translates it into solver
    domain, armature = model.construct_domain(magnetic)
    magnetic.setup(domain)
    
    outputs = SolverOutputs()
    outputs.add_circuit(model.PHASE, CircuitOptions.flux_linkage)

    results = magnetic.solve(outputs)
    old_flux_linkage = results[model.PHASE].flux_linkage

    # Simulation Loop
    time_step = parameters.numerical.time_step
    t, z = 0 * second, 0 * meter
    
    t_set = []
    v_set = []

    # Simulates for two periods
    iteration = 0 
    while t < 1/parameters.model.shaking_frequency:
        if iteration % 10 == 0 and verbose == True:
            print(f"UPDATED | Time: {t:.3f}, Pos: {z:.3f}")
    
        # Moves elements within the simulation & gets new linkage
        new_z_axial_position = - model.travel * (2*pi*parameters.model.shaking_frequency*t).sin()
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
    
    # Calculates the rms_voltage
    squared_voltages = [v**2 for v in v_set]
    mean_squared = sum(squared_voltages) / len(v_set)
    v_rms = mean_squared ** 0.5

    return (v_rms * volt, [v_set, t_set])


if __name__ == "__main__":
    # Imports parameters from .uiv parameter file with units
    BASE_DIR = Path(__file__).parent.parent
    para_dir = BASE_DIR / "parameters.uiv"
    solver_folder = BASE_DIR / "FEM/outputs"

    # Imports the parameters (value:unit) into memory
    parameters = Parser.open(para_dir)

    model = build_generator(parameters)
    print(simulate_resistance(solver_folder, model, True))
    print(simulate_rms_voltage(solver_folder, model, True)[0])
    