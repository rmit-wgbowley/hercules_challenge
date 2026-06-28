<!--
Color Palette:
- #F3F4F4
- #0DFDF7
-->

<p align="center">
  <img src="04_media/quasi_transient_magnitude_of_b.gif" style="max-width:600px;">
  <br>
  <em>Axial Shake Powered Pill System – Electromechanical Design of the IsoPod by <a href="https://github.com/wgbowley">William Bowley</a></em>
</p>

--- 
The Hercules Challenge is a co-design consortium challenge available to first-semester, first-year engineers through the mandatory introductory class, "Introduction to Professional Engineering."

> [!IMPORTANT]
> `The Pantheon` consortium received a commendation award for their work on the `IsoPod` at the Hercules Challenge night at RMIT.

# Overview

![MIT License](https://img.shields.io/badge/License-MIT-F3F4F4?style=flat-square&logoColor=black)
![Domain](https://img.shields.io/badge/Domain-Energy_Harvesting-F3F4F4?style=flat-square&color=0DFDF7)
![Power](https://img.shields.io/badge/Output-0.43W-F3F4F4?style=flat-square&color=0DFDF7)
![EM](https://img.shields.io/badge/Physics-Electromagnetics-F3F4F4?style=flat-square&logo=physics&logoColor=F3F4F4)

The `IsoPod` is a pill system that reminds users when to take their medication through an e-ink display on the cylindrical bi-sector face of the device, providing a simple visual reminder.

This repository focuses on the design, simulation, construction, and validation of the `axial shake generator` (ASG) at the device's core. The generator converts intentional shaking motion into electrical energy via magnetic induction, which charges the IsoPod's Li-Po battery. This extends battery life, or with enough motion, can enable complete self-reliance.

### Why generate electrical?

In humanitarian contexts, reliable grid power isn't guaranteed, nor are reliable supply chains for expendable batteries. The ASG decouples the `IsoPod` from external infrastructure by converting user motion into electrical energy. Alongside this, the device helps compensate for human memory limitations through consistent and precise medication reminders, tasks where embedded systems excel.

# Axial Shake Generator

<div align="center">
  <a href="01_simulation/parameters.uiv">
    <img src="04_media/demonstrator_cross_section.png" alt="Generator cross section" style="max-width:600px;">
  </a>
  <p><i>Figure 1: Cross-sectional analysis: <a href="01_simulation/parameters.uiv">Click here for parameters</a></i></p>
</div>

The generator consists of an armature (purple) made of poles (magnets), a stator (light blue) made of slots (coils), and restoring magnets which act as magnetic springs that allow the armature to build velocity from the user shaking the device with their forearm muscles.

## Electromagnetics

An ASG produces electricity via the interaction between a slot and a pole. When a pole moves axially through a slot, it produces an induced voltage within that slot due to the changing magnetic field generating a changing electric field. The induced electric field opposes the change in magnetic flux that produced it, a consequence of Lenz's law. These ideas come together to form `Faraday's Law of Induction`:

$$V = -N\frac{d\Phi}{dt} \implies -\frac{d\lambda}{dt}$$

where $λ = N\Phi$ is the flux linkage between the slot and pole. Flux linkage can be thought of as the magnitude of how strongly the magnetic field links with the winding (turns in a slot). Higher linkage generally means the system can produce a larger induced voltage for the same change in armature position.

Luckily, using related rates, the two main parameters appear:

$$V_{\text{induced}} = -\frac{d\lambda}{dt} \implies -\frac{d\lambda}{dz} \cdot \frac{dz}{dt}$$

The first term is the derivative of flux linkage over the z-axis (magnetic design), and the second term is the z-axis velocity (mechanical input). These can be analytically approximated as:

> [!important]
> Flux linkage can be approximated analytically for intuition. The final flux linkage was obtained using Finite Element Analysis (FEA).

$$\frac{dz}{dt} = A \omega \cos(\omega t + \phi)$$
$$\frac{d\lambda}{dz} = \frac{d}{dz} (B \cos(z)) \implies -\mu H \sin(2\pi z)$$

> [!note]
> For a simple magnetic circuit, magnetic flux density can be related to magnetic field strength by `B = μH`, where `B` is the magnetic flux density, `H` is the magnetic field intensity, and `μ` is the permeability, the ability of a material to support magnetic flux.

These two derivatives expose the important mechanics of the system. Increasing acceleration `A` and frequency `ω` may increase induced voltage, but these are constrained by the user's physical abilities. Whereas the permeability `μ` and `H` may increase the induced voltage while generally not being constrained by the user's physical abilities.

Once induced voltage is established, the usable electrical power is determined by the generator's internal resistance:

$$P = \frac{V_{\text{rms}}^2}{R_{\text{internal}}}$$

This relationship drives one of the main trade-offs: increasing turns raises induced voltage but also increases resistance due to longer wire length. The optimal design maximizes `V/R`, not just peak voltage.

> [!important]
> The generator design was constrained by the IsoPod system requirements:
> - Cylindrical form factor: radial thickness < `12.5 mm`, height < `250 mm`
> - Human-powered input motion (reasonable frequency and acceleration)
> - Low-maintenance energy harvesting
> - Easy to construct with basic tools

## Design & Topology

<div align="center">
  <img src="04_media/high_level_topology.png" alt="Generator high-level topology" style="max-width:600px;">
  <p><i>Figure 2: High level electrical machine topology</i></p>
</div>

> [!note]
> `N-S` represents an axially magnetized permanent magnet pole. `PA` represents phase A, where `PA+` and `PA-` indicate opposite winding directions.

The high-level topology in figure 2 was selected to enable oscillatory motion through magnetic restoring forces. The additional end poles act as magnetic springs, creating a restoring force when the armature approaches the limits of travel. This allows the armature to return towards the centre position after displacement.

The alternating pole arrangement (`N-S|S-N`) was selected because the transition between opposing poles creates a rapid change in magnetic field along the z-axis, increasing the spatial rate of change of flux linkage:

$$V \propto \frac{d\lambda}{dz}$$

A pole pitch of `10 mm` was selected, matching the pole length and maintaining direct magnetic coupling between adjacent opposing poles. The topology uses four stator slots interacting with four active armature poles, with additional poles placed on each end of the armature to increase usable travel distance. This allows approximately `20 mm` of positive and negative armature displacement while maintaining magnetic coupling between the armature and stator.

Maintaining slot overlap throughout the motion range produces a more consistent induced voltage waveform, where the primary amplitude is dominated by the mechanical velocity term:


$$V \propto \frac{dz}{dt}$$

The symmetric pole arrangement also reduces unwanted harmonic content compared with asymmetric topologies. Finally, no high-permeability materials were introduced into the armature or stator structure. The stator consists of copper windings, while the magnetic poles use `N52 Neodymium` permanent magnets.

Given the 4 slots within the stator and the 8 poles within the armature, the measured frequency relationship suggests:

$$f_{\text{electrical}} \approx 4 \times f_{\text{mechanical}}$$

This is consistent with the pole pitch and the number of magnetic cycles encountered per mechanical oscillation.

## Numerical Model

> [!important]
> This area is recommended for individuals more familiar with electromagnetic finite element simulations.

The ASG was modelled using `FemmMagneticRender` (FEMM) with `shapely` for translating `PYFEA` CSG (constructive solid geometry) to FEMM native primitives. An axially symmetric coordinate system (z-r) was used due to the generator's rotational symmetry around its z-axis. A Dirichlet boundary condition was applied, with the radial boundary at `2×` the slot outer radius and the axial boundary at `1.2×` the stator tube length. The armature motion relative to the origin was simulated using:

$$ z = \text{travel} \cdot \sin(2\pi f t) $$

The resistance was obtained from `FemmMagneticSolver` during an initial configuration solve, and then the flux linkage was obtained per solve. Using the simulation time-step, the induced voltage was calculated using finite difference:

$$V_{\text{induced}} = -\frac{\lambda_{\text{new}} - \lambda_{\text{old}}}{t_{\text{step}}}$$

This was then used to calculate the RMS voltage, and using the generator's internal resistance, the expected power output was obtained. This method represents a `quasi-transient` method due to its use of asymptotic field conditions ($t=\infty$) per time step. This is reasonable due to the absence of highly magnetically permeable materials and the low operating frequency of the generator.

## Simulation Results

> [!IMPORTANT]
> The model was configured with the following parameters:
> - Temperature: `293.15 K`, Time step: `1ms`
> - Mechanical Shaking Frequency: `8.81 Hz`, Electrical Shaking Frequency: `35.2 Hz`
> - peak-to-peak travel: `40 mm`
> - Pole Coercivity: `956 kA/m`, Pole Permeability: `1.05 ∅`
> - Slot Conductivity: `60.07 MS/m`, Slot Permeability: `1.0 ∅`, Fill Factor: `0.47 ∅`, Turns: `184`

<div align="center">
  <img src="04_media/magnitude_of_b_analog_z.png" alt="|B| vs Z" style="max-width:600px;">
  <p><i>Figure 3: Simulated static |B| along the z-axis of the generator</i></p>
</div>

> [!IMPORTANT]
> The quasi-transient simulation predicted:
> - Time: `0.228 s`, Time steps: `228`
> - Peak voltage: `5.161 V`, RMS Voltage: `2.696 V` 
> - Positive Rate: `486.06 V/s`, Negative Rate: `-844.25 V/s`
> - Resistance: `22.54 Ω`, Power: `0.323 W` 

<div align="center">
  <img src="04_media/FEM_simple_induced_voltage_plot.png" alt="Induced voltage vs time" style="max-width:600px;">
  <p><i>Figure 4: Simulated induced voltage vs time and position vs time</i></p>
</div>

The parameter file can be found [here](01_simulation/01_simple_motion/parameters.uiv), written in `.uiv` (unit-informed values). The simulation files can be found [here](01_simulation/readme.md), written in Python using the `pyfea` solver-adapter engine. Solver assumptions can be found [here](03_data/assumptions_printout.md).

## Construction

The generator was printed out of ABS on a Voron 2.4. The armature consisted of a carbon fibre rod with `8` x `N52` poles inserted into it in the pattern described above, using superglue to secure the end poles.

The stator consisted of `4` coils with `180` turns per coil of `0.2 mm` enameled copper wire, with each coil wound in the opposite direction to the last as described above. The coils were secured in place with `10 mm` and `5 mm` thick Kapton tape, with the first and last layers of the coil being wrapped.

The restoring magnets were flat `12 mm x 3 mm` neodymium magnets. The generator stator was split into two pieces: the main piece, which housed the coils and one restoring magnet, and the cap, which held the other restoring magnet and was attached via `3` x `M3 x 20 mm` bolts. The two outputs of the generator were secured to the side and then extended with `~1.25 mm` stranded copper wire.

<div align="center">
  <img src="04_media/generator_side_profile.jpg" alt="Generator Side profile" style="max-width:600px;">
  <p><i>Figure 5: Side profile (Construction)</i></p>
</div>


## Results

The completed generator was tested by hand-shaking at a measured fundamental mechanical frequency of `8.81 Hz` with a electrical frequency of `35.2 Hz`
(the 4 coils produce 4 cycles per mechanical oscillation). The open-circuit voltage was recorded using an oscilloscope:


> [!IMPORTANT]
> The oscilloscope measurements:
> - Positive Peak: `16.8 V`, Negative Peak: `-16.4 V`
> - Positive Rate: `131 V/s`, Negative Rate: `-246 V/s` (Slew Rate)
> - V_RMS(AV): `3.47 V`, V_RMS(PEAK): `3.63 V`
> - Resistance: `27.8 Ω`, Power: `0.43-0.47 W`

> [!NOTE]
> Slew rate can be effected by probe loading due to parasitic capacitance and inductance. Hence `dv/dt` may be slowed due to the `LRC` circuit formed.

<div align="center">
  <img src="04_media/oscilloscope_trace.png" alt="Oscilloscope trace" style="max-width:600px;">
  <p><i>Figure 6: Voltage vs time trace @ 10V/div vertical, 50ms/div horizontal</i></p>
</div>

The measured waveform shown in Figure 6 has a similar shape to the predicted waveform in Figure 4. However, the negative recovery appears stretched while still being a similar amplitude. This is most likely attributed to degradation of the prototype due to its usage as a demo item. Another notable observation is that the trace appears asymmetric in the rate of change, with a higher negative voltage rate than positive. This may be due to gravity assisting downward acceleration while opposing upward motion.

# Validation

The simulated power output was `0.323 W` whereas the measured power was `0.43-0.47 W`, which is within 25% of the measured value. The peak voltages are much higher and the slew rate was significantly different, leading to the possible source being the idealized motion of the armature versus the realized motion.

The simulation used a higher mechanical frequency but produced lower peak voltages. If the prototype's armature acceleration was much higher than expected, the armature was likely slamming into the end-caps due to the repulsion force not being high enough. The maximum velocity was most likely higher and hence:

$$V \propto \frac{d\lambda}{dz}$$

## New Mechanical Model

> [!important]
> This area is recommended for individuals more familiar with electromagnetic finite element simulations.

Given this, a new model for the motion could be proposed that takes into consideration the magnetic repulsion force and the likely much higher mechanical acceleration but lower frequency, using an oscillating force function:

$$F_{\text{magnetic}} = -\frac{dU}{dz}$$
$$F_{\text{shaking}} = am\sin(\omega t + \phi)$$

One approach would be to model the armature velocity as:

$$\frac{dz}{dt} = \int \frac{F_{\text{magnetic}} + F_{\text{shaking}}}{m} \ dt$$

> [!Note]
> Euler method was used to integrate from acceleration to z-position, the stability was not formalized.

However, given the ability of `FemmMagneticSolver` to calculate the Maxwell stress tensor, the $F_{\text{magnetic}}$ term will be obtained directly from the solver rather than using finite difference of the magnetic energy density over the z-axis. This decouples the solution from the displacement output, removing dynamic step sizes and leading to a more stable solution.

## Simulation Results 

> [!IMPORTANT]
> The model was configured with the following parameters:
> - Temperature: `293.15 K`, Time step: `1 ms`
> - Mechanical Shaking Frequency: `2.2 Hz`, Electrical Shaking Frequency: `8.8 Hz`
> - Acceleration: `75 m/s²`, peak-to-peak travel: `40 mm`
> - Pole Coercivity: `956 kA/m`, Pole Permeability: `1.05 ∅`
> - Slot Conductivity: `60.07 MS/m`, Slot Permeability: `1.0 ∅`, Fill Factor: `0.47 ∅`, Turns: `184`

> [!IMPORTANT]
> The quasi-transient simulation predicted:
> - Time: `0.228 s`, Time steps: `228`
> - Peak voltage: `12.35 V`, RMS Voltage: `3.44 V` 
> - Positive Rate: `634.76 V/s`, Negative Rate: `-2.32 kV/s`
> - Resistance: `22.54 Ω`, Power: `0.526 W` 

<div align="center">
  <img src="04_media/FEM_advance_induced_voltage_plot.png" alt="Induced voltage vs time" style="max-width:600px;">
  <p><i>Figure 6: New simulation results (Simulation Results)</i></p>
</div>

The parameter file can be found [here](01_simulation/02_advance_motion/parameters.uiv), written in `.uiv` (unit-informed values). The simulation files can be found [here](01_simulation/readme.md), written in Python using the `pyfea` solver-adapter engine. Solver assumptions can be found [here](03_data/assumptions_printout.md).

# Conclusion





### Bibtex Citation:

```
@misc{Bowley_2024,
  author = {Bowley, William},
  title = {{IsoPod: Axial Shake Generator}},
  url = {https://github.com/rmit-wgbowley/isopod-generator},
  year = {2024},
  note = {
    GitHub repository,
    Electromagnetic Subsystem Of The Isopod
  },
  license = {MIT}
}
```