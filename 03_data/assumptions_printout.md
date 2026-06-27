# Solver Assumptions

> [!Important]
> Solver Adapter: FEMMMagnetostaticSolver
> These assumptions apply to both the initial resistance solution and each quasi-transient frame.

```
=== model assumptions ===
• Coordinates = axi, depth = 0.000 (m)
• Frequency = 0 Hz, asymptotic field conditions
• Dirichlet Boundary (A = 0), Flux boundary shunt
• copper_0.200 m(m) coercivity assumed to be 0.0 (A/m)
• copper_0.200 m(m) uses linear interpolation to calculate conductivity
• Phase is assumed to be a constant current source
• NdFeB uses linear interpolation to calculate conductivity
• Air coercivity assumed to be 0.0 (A/m)
• Air uses linear interpolation to calculate conductivity
• Air conductivity set to 0.0 (S/m) to ensure correct domain behavior (gases only)
=========================
```