# Simulation

> [!WARNING]
> pyFEA is functionally working and produces physically consistent results.
> However, the API and abstraction boundaries are still under active development and may change.
> It is not yet stable as a public-facing dependency.

## 01 Simple Motion

A reduced-order motion model used to approximate armature dynamics while minimising computational cost.
This model assumes a simplified prescribed motion profile for the moving armature.

### Limitation
Validation against prototype measurements showed a 25–45% underprediction in power output.  
This discrepancy is attributed to the assumed motion profile not capturing the armature's true dynamics.

Simple motion can be found [here](/01_simulation/01_simple_motion/).

## 02 Advanced Motion

This simulation uses a prescribed oscillatory motion model combined with Maxwell stress tensor-based force computation 
to evaluate electromagnetic forces (`F_magnetic`) acting on the armature.

The magnetic force is computed directly from the field solution, avoiding energy-difference approximations.

### Limitation
Validation against prototype measurements showed results within 12–22% of measured values.

Advanced motion can be found [here](/01_simulation/02_advance_motion/).
