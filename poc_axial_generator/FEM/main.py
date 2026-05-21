"""
Filename: main.py

Description:
    Axial-shake generator using pyfea for magnetics and lumped 
    parameter model for electro and mechanical domains.
"""

from pathlib import Path
from pyfea.domain.units import Parser

from model.generator import AxialShakeGenerator
from pyfea.solver.femm.domains.magnetostatic.solver import FEMMMagnetostaticSolver
from pyfea.solver.solver_outputs import SolverOutputs, CircuitOptions

# Imports parameters from .uiv parameter file with units
BASE_DIR = Path(__file__).parent.parent
para_dir = BASE_DIR / "parameters.uiv"
solver_folder = BASE_DIR / "FEM/Outputs"

# Imports the parameters (value:unit) into memory
parameters = Parser.open(para_dir)

# Initializes model & magnetic solver
model = AxialShakeGenerator(parameters)
magnetic = FEMMMagnetostaticSolver(solver_folder)

# Builds magnetic domain & translates it into solver
domain = model.construct_domain(magnetic)
magnetic.setup(domain)

# Selecting outputs (induced = -d(Flux linkage)/dt)
outputs = SolverOutputs()
outputs.add_circuit(model.PHASE, CircuitOptions.flux_linkage)

results = magnetic.solve(outputs)