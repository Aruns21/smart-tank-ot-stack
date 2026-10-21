# Smart Tank OT Stack

A layered build of one process, a tank that fills, heats and drains, taken up
the industrial **automation pyramid** bottom-up, from PLC control logic to
IIoT dashboards, as part of my path toward an Industrial Automation / IIoT
engineering role.

Built by [Arun Sudhakaran Nair](https://github.com/Aruns21), M.Sc. student
in Automation Technology at Technische Hochschule Deggendorf.

## Progress

**Stage 1 (Field/Control level): done.** [Software PLC simulator](stage1-plc-simulator/):
scan cycle, state machine, and IEC 61131-3-style timers for a tank
fill → heat → drain sequence.

**Stage 2 (Control ↔ Supervisory level): done.** [Real PLC runtime](stage2-codesys/):
the same sequence, written in Structured Text, running live on CODESYS,
exposed over real Modbus TCP and verified with an independent Python
client.

**Stage 3 (Supervisory level): done.** [Ignition SCADA layer](stage3-ignition/):
a Perspective operator screen showing live valve and heater state with Start and
Stop/Reset controls, plus a Python OPC-UA client reading the same tags by name.

More stages will be added here as they're completed. Each one builds on the
previous one's output rather than standing alone, so the repo's history
tells one continuous story rather than a set of disconnected demos.

## Why this structure

Mirrors the ISA-95 automation pyramid that real plant architectures follow:
field/control devices at the bottom, supervisory/HMI above that, then
MES/historian, then enterprise/cloud analytics. Building it in that order,
starting with actual control logic rather than jumping straight to IIoT
tooling, reflects the core of what a PLC/automation engineer does before
any of the IIoT layer matters.
