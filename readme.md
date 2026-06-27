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

## Overview

![MIT License](https://img.shields.io/badge/License-MIT-F3F4F4?style=flat-square&logoColor=black)
![Domain](https://img.shields.io/badge/Domain-Energy_Harvesting-F3F4F4?style=flat-square&color=0DFDF7)
![Power](https://img.shields.io/badge/Output-0.43W-F3F4F4?style=flat-square&color=0DFDF7)
![EM](https://img.shields.io/badge/Physics-Electromagnetics-F3F4F4?style=flat-square&logo=physics&logoColor=F3F4F4)

The `IsoPod` is a pill system that reminds users when to take their medication through an e-ink display on the cylindrical bi-sector face of the device, providing a simple visual reminder.

This repository focuses on the design, simulation, construction, and validation of the `axial shake generator` at the device's core. The generator converts intentional shaking motion into electrical energy via magnetic induction, which charges the IsoPod's Li-Po battery. This extends battery life, or with enough motion, can enable complete self-reliance.

### Why generate electrical?

In humanitarian contexts, reliable grid power isn't guaranteed, nor are reliable supply chains for expendable batteries. The `axial shake generator` decouples the `IsoPod` from external infrastructure by converting user motion into electrical energy. Alongside this, the device helps compensate for human memory limitations through consistent and precise medication reminders tasks where embedded systems excel.