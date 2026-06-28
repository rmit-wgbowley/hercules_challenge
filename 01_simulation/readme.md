# Simulation

> [!IMPORTANT]
> I wouldn't recommend running these as `pyfea` is still actively under development and the abstraction boundaries are not perfect.

## 01 Simple Motion

Uses a simplified model for the user's shaking motion to reduce numerical complexity. Questionable accuracy due to motion path differences.

Simple motion can be found [here](/01_simulation/01_simple_motion/).

## 02 Advanced Motion

This simulation uses an oscillating function for the user's shaking motion and also uses the Maxwell stress tensor to calculate the magnetic force (`F_magnetic`) for the restoring motion.

Advanced motion can be found [here](/01_simulation/02_advance_motion/).