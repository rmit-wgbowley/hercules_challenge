"""
Filename: evaluator.py

Description:
    Axial-shake generator using PyFEA for magnetics and a lumped 
    parameter model for the electro and mechanical domains.
    
    NOTE:
    Uses a simplified model for the shaking from the user to 
    reduce numerical complexity. Hence, efficiency cannot be quantified.
"""

import matplotlib.pyplot as plt

from math import pi
from pathlib import Path
from pyfea.domain.units import Parser
from pyfea import Q, unit_validator, ampere, ohm, volt, second, meter, nullset

from pyfea.domain.units import DynamicLoader
from pyfea.solver.femm.domains.magnetostatic.solver import FEMMMagnetostaticSolver
from pyfea.solver.solver_outputs import SolverOutputs, CircuitOptions, ImageOptions

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
    t, z, v = 0 * second, 0 * meter, 0 * volt
    
    t_set = []
    v_set = []
    z_set = []
    
    slew_rate_pos = []
    slew_rate_neg = []
    
    # Simulates for two periods
    iteration = 0 
    while t < 2/parameters.model.shaking_frequency:
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
        
        # Calculates the slew rate within the phase
        dv = induced - v
        slew_rate = dv/time_step
        
        if slew_rate < 0 * (volt/second):
            slew_rate_neg.append(slew_rate.stripped)
        else:
            slew_rate_pos.append(slew_rate.stripped)
        
        t_set.append(t.value)
        v_set.append(induced.value)
        z_set.append(new_z_axial_position.value)

        old_flux_linkage = new_flux_linkage 
        z = new_z_axial_position
        v = induced
        t += time_step
        
        iteration += 1       
    
    # Calculates the rms_voltage
    squared_voltages = [v**2 for v in v_set]
    mean_squared = sum(squared_voltages) / len(v_set)
    v_rms = mean_squared ** 0.5

    # Calculates the slew rate
    avg_pos = sum(slew_rate_pos) / len(slew_rate_pos)
    avg_neg = sum(slew_rate_neg) / len(slew_rate_neg)
    
    return (v_rms * volt, avg_pos * (volt/second), avg_neg * (volt/second), [v_set, t_set, z_set])

if __name__ == "__main__":
    # Imports parameters from .uiv parameter file with units
    BASE_DIR = Path(__file__).parent.parent
    para_dir = BASE_DIR / "01_simple_motion/parameters.uiv"
    solver_folder = BASE_DIR / "01_simple_motion/outputs"

    # Imports the parameters (value:unit) into memory
    parameters = Parser.open(para_dir)
    model = build_generator(parameters)

    resistance = simulate_resistance(solver_folder, model)
    v_rms, slew_pos, slew_neg, [v_set, t_set, z_set] = simulate_rms_voltage(solver_folder, model, True)
    
    # Calculations
    peak_voltage = max(abs(v) for v in v_set) * volt
    power = (v_rms ** 2) / resistance

    # Print Results
    print("-" * 30)
    print(f"Resistance:     {resistance:.3f}")
    print(f"RMS Voltage:    {v_rms:.3f}")
    print(f"Peak Voltage:   {peak_voltage:.3f}")
    print(f"Power:          {power:.3f}")
    print(f"Slew Rates:     ({slew_pos:.2f}, {slew_neg:.2f}")
    print("-" * 30)
    
    print(f"Simulation Complete. Time_step: {parameters.numerical.time_step}, Total steps: {len(t_set)}") 
    fig, (ax1, ax2,) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

    # Plot 1: Induced Voltage
    ax1.plot(t_set, v_set, color='#1f77b4', linewidth=1.5, label='Phase Induced Voltage')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('Axial-Shake Generator Simulation Dynamics')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper right')

    # Plot 2: Displacement Position
    ax2.plot(t_set, z_set, color='#2ca02c', linewidth=1.5, label='Axial Position z(t)')
    ax2.set_ylabel('Position (m)')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(loc='upper right')
    plt.tight_layout()
    
    output_path = solver_folder / "simulation_dynamics.png"
    plt.savefig(output_path, dpi=150)
    print(f"Plot saved to: {output_path}")
    plt.show()