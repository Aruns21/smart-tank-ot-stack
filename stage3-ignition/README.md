# Stage 3: SCADA Supervisory Layer (Ignition)

An operator screen for the tank sequence from Stages 1 and 2, built in
Ignition (Maker Edition) and connected to the live CODESYS PLC over Modbus TCP.
A small Python client reads the same tags through Ignition's OPC-UA server.

```
Browser (Perspective) --+
                        +--> Ignition Gateway --Modbus TCP--> CODESYS PLC (PLC_PRG)
Python OPC-UA client ---+
```

## What this demonstrates

- **A real supervisory layer.** The PLC still owns the control logic. Ignition
  only reads state and writes operator commands, the same split a real plant uses.
- **Tags as the contract.** Seven boolean tags map the PLC's Modbus coils and
  discrete inputs to names. Everything above this layer works with names, never
  raw addresses.
- **An operator screen (Perspective).** Three status lamps for the inlet valve,
  heater and drain valve, bound to the PLC outputs, plus START and STOP / RESET
  buttons that pulse the PLC's start and stop inputs.
- **An IT/OT bridge.** `opcua_bridge.py` connects over encrypted OPC-UA, reads
  the tags by name with their quality, and prints changes as the server pushes
  them.

## Tag map

Ignition's Modbus item paths are 1-based, while the PLC and the Stage 2 test
script use 0-based addresses.

| Tag | Modbus table | PLC address | Ignition item path |
|---|---|---|---|
| StartButton | Coil | 0 | `[TankSequence_CODESYS]C1` |
| StopButton | Coil | 1 | `[TankSequence_CODESYS]C2` |
| LevelHighSensor | Coil | 2 | `[TankSequence_CODESYS]C3` |
| LevelLowSensor | Coil | 3 | `[TankSequence_CODESYS]C4` |
| InletValve | Discrete Input | 0 | `[TankSequence_CODESYS]DI1` |
| Heater | Discrete Input | 1 | `[TankSequence_CODESYS]DI2` |
| DrainValve | Discrete Input | 2 | `[TankSequence_CODESYS]DI3` |

## Files

- `TankOverview_components.json`: the Perspective view as component JSON. In
  the Designer, open an empty view, select its root container and paste it
  with Ctrl+V (after copying the file's contents to the clipboard).
- `opcua_bridge.py`: the OPC-UA client.
- `requirements.txt`: Python dependency (`asyncua`).

## Running the OPC-UA client

1. In the Gateway, enable "Expose Tag Providers" under OPC UA Server Settings,
   and create a low-privilege user with the ReadWrite role in the `opcua-module`
   user source.
2. Run `python opcua_bridge.py`. Credentials are typed at a hidden prompt and
   are never stored.
3. The first run generates a client certificate under `certs/` (not committed).
   Ignition quarantines unknown clients, so trust it once on the Gateway's
   OPC UA Security page (Server tab), then run again.
4. `--pulse start` or `--pulse stop` presses the matching button through OPC-UA.

## Notes from building it

- Ignition's OPC-UA server only offers encrypted connections with a username
  and password, so the client needs its own certificate.
- Perspective button scripts must be indented inside their wrapper function,
  otherwise the Gateway logs a syntax error and the button does nothing.
- Ignition samples the Modbus device about once a second, so a very short
  pulse can fall between two samples and not show up in a subscription.
