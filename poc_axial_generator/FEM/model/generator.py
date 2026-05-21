"""
Filename: generator.py

Description:
    Magnetic model of a axial_shake generator for usage
    in FEM simulation.
"""

from math import ceil

from pyfea import nullset, ampere, mm
from pyfea.domain.units import DynamicLoader

from pyfea.domain.materials.manager import MaterialManager
from pyfea.domain.geometry.definitions import CoordinateSystem
from pyfea.domain.geometry.builder import Builder, VectorGeometry
from pyfea.domain.geometry.elements.vectors import CSGNode
from pyfea.domain.geometry.domain import Domain, BoundaryType

from pyfea.solver.solver_interface import BaseSolver, MagneticSolver
from pyfea.domain.circuits.builder import StaticCircuit, Configuration as CircuitConfig
from pyfea.domain.geometry.elements.metadata import MagneticData

class ModelError(Exception):
    """ Exception for tubular motor modelling errors """
    def __init__(self, func_name: str = "", error: str = "") -> None:
        """ Returns a error message with caller and the error """
        msg = f"{func_name} raised error: {error}"
        super().__init__(msg)


class AxialShakeGenerator:
    """ CSG model for a axial shake generator """
    ENVIRONMENT_ID = 0 * nullset
    STATOR_ID = 1 * nullset
    ARMATURE_ID = 2 * nullset
    
    PHASE = StaticCircuit("phase", 0 * ampere, CircuitConfig.series)
    
    def __init__(self, parameters: DynamicLoader) -> None:
        """ Initializes the class & defines dependencies """
        self.params = parameters
        
        # Defines the coordinate system and model materials
        self.coordinate_system = CoordinateSystem.AXI_SYMMETRIC

        self._load_material()
        self._derived_parameters()
    
    def construct_domain(self, solver: BaseSolver) -> Domain:
        """ Constructs the domain based on solver physics domain """
        solver_interfaces = solver.__class__.__bases__
        
        # Derived parameters & reloads materials
        self._derived_parameters()
        self._load_material()
        
        for solver in solver_interfaces:
            if solver == MagneticSolver:
                return ConstructMagnetic.build(self)

        msg = f"{solver_interfaces!r} is not supported by {self.__class__.__name__}"
        raise ModelError("TubularLinearMotor.construct_domain()", msg)

    def build_armature(self) -> list[VectorGeometry]:
        """ Builds the poles within the armature """
        poles = []
        for pole in range(0, int(2 * self.params.model.number_pairs.value)):
            offset = - self.armature_length / 2
            bottom_left = offset + pole * self.pole_length
            
            pole_shape = Builder.rectangle((0 * mm, bottom_left), self.armature_poles_radius, self.pole_length)
            poles.append(pole_shape)
        
        return poles
    
    def build_stator(self) -> list[VectorGeometry]:
        """ Builds the slots within the stator """
        slots = []
        for slot in range(0, int(self.number_slots.value)):
            offset = - self.stator_length / 2
            bottom_left = offset + slot * self.pitch

            slot_shape = Builder.rectangle(
                (self.slot_inner_radius, bottom_left),
                self.params.stator_slots.radial_thickness, self.slot_length
            )
            slots.append(slot_shape)
        
        return slots
    
    def build_boundary(self) -> VectorGeometry:
        """ 
        Builds the boundary shape via tube length with 20% margin axially, 100% radially 
        """
        max_length = 1.2 * self.tube_length
        max_radius = 2 * self.slot_outer_radius
        
        return Builder.rectangle((0 * mm, -max_length / 2), max_radius, max_length)

    def _load_material(self) -> None:
        """ Builds out the material manager with materials """
        manager = MaterialManager()
        
        # Finds the material in the .uiv material library
        self.environmental_material = manager.use_material(self.params.model.environmental_material)
        self.stator_material = manager.use_material(self.params.stator_slots.material)
        self.armature_material = manager.use_material(
            self.params.armature_poles.material, 
            grade=self.params.armature_poles.grade
        )
        
    def _derived_parameters(self) -> None:
        """ Calculates derived parameters from base parameters """
        self.number_poles = 2 * self.params.model.number_pairs
        self.pole_length = self.params.armature_poles.axial_length
        self.slot_length = self.params.stator_slots.axial_length
        
        # Calculates the length of the different components within the assembly
        self.armature_length = self.number_poles * self.pole_length
        self.stator_length = 2 * self.armature_length
        self.tube_length = 3 * self.armature_length
        
        # Calculates the number of slots within the device
        self.number_slots = 2 * self.number_poles
        self.pitch = self.stator_length / self.number_slots

        # Calculates for radial placement
        self.armature_poles_radius = self.params.armature_poles.radial_thickness
        self.slot_inner_radius = (
            self.armature_poles_radius +
            self.params.stator_core.gap_radial_thickness + 
            self.params.stator_core.wall_radial_thickness
        )
        self.slot_outer_radius = self.slot_inner_radius + self.params.stator_slots.radial_thickness
        

class ConstructMagnetic:
    """ Constructs the magnetic domain vai adding magnetic metadata to geometry """
    @classmethod
    def calculate_number_turns(cls, generator: AxialShakeGenerator) -> int:
        """ Calculates the approximate number of turns within a slot """
        params = generator.params
        radius = params.stator_slots.radial_thickness
        
        # Calculates the cross sectional area, wire area and than effective material area
        slot_area = radius * generator.slot_length
        wire_area = params.stator_slots.wire_diameter ** 2
        
        # Calculates the effective area within the slot excluding enamel
        effective_copper_area = slot_area * params.stator_slots.fill_factor
        turns = ceil(effective_copper_area / wire_area)
        
        if turns < 0:
            msg = f"Derived parameter 'turns' cannot be {turns}. Slots must have non-zero area"
            raise ModelError("ConstructMagnetic.calculate_number_turns", msg)
        
        return turns
    
    @classmethod
    def build(cls, generator: AxialShakeGenerator) -> Domain:
        """ Builds the magnetic simulation via adding metadata to geometry """
        # Builds the armature, stator and boundary
        poles = generator.build_armature()
        slots = generator.build_stator()
        boundary = generator.build_boundary()
        
        # Defines simulation parts via promoting and metadata
        params = generator.params
        parts = []
        
        # Adds the slots to the domain
        turns = cls.calculate_number_turns(generator)
        for index, slot in enumerate(slots):
            # Sets the phase of slot in pattern [A, A'] or [A, A]
            phase = generator.PHASE
            polarity = 1 # +1 if index % 2 == 0 else -1
            
            # Constructs meta-data and promotes to part while appending to domain
            metadata = MagneticData(
                generator.STATOR_ID, generator.stator_material, 
                phase, turns * polarity, params.stator_slots.wire_diameter
            )
            parts.append(Builder.promote_to_part(slot, metadata))
            
        # Adds the poles to the domain
        for index, pole in enumerate(poles):
            # Alternate magnetization direction every pole (e.g. N-S-N-S)
            pole_magnetization = 90 if index % 2 == 0 else - 90
            
            # Constructs meta-data and promotes to part while appending to domain
            metadata = MagneticData(
                generator.ARMATURE_ID, generator.armature_material,
                magnetization = pole_magnetization * nullset
            )
            parts.append(Builder.promote_to_part(pole, metadata))
        
        # Overall simulation problem definition
        meta = MagneticData(generator.ENVIRONMENT_ID, generator.environmental_material)
        return Domain(
            parts, 
            BoundaryType.DIRICHLET, 
            meta, 
            generator.coordinate_system,
            boundary,
            params.model.environmental_temperature
        )