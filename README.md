# GPIB Communication

`GPIB.py` provides a small wrapper around PyVISA for communicating with laboratory instruments over GPIB. It discovers VISA resources, opens and closes instrument connections, sends commands, and reads query responses.

## Requirements

- Python 3
- PyVISA: `pip install pyvisa`
- NI-VISA or another compatible VISA implementation
- A powered-on GPIB instrument and a configured GPIB interface

## Basic usage

```python
from GPIB import GPIBController

gpib = GPIBController()
resources = gpib.list_resources()
print(resources)

if resources and gpib.connect_instrument(resources[0], "instrument"):
	print(gpib.get_identification("instrument"))
	gpib.send_command("instrument", "*CLS")
	response = gpib.query_command("instrument", "MEAS?")
	print(response)

gpib.close_all_connections()
```

`list_resources()` returns VISA resource names such as `GPIB0::10::INSTR`. Pass one of these names to `connect_instrument()`. An optional alias makes later calls shorter. Commands are sent with `send_command()`, while `query_command()` sends a command and returns the instrument response. Use `read_response()` when a response is already waiting to be read.

The controller also provides `get_identification()`, `reset_instrument()`, `clear_instrument()`, and `wait_for_completion()`. Always call `close_all_connections()` when finished.

To use a specific VISA library, pass its path when creating the controller:

```python
gpib = GPIBController(visa_library="/path/to/visa/library")
```

## LGAD IV example

`LGAD_IV.py` demonstrates a simple current-voltage measurement with a Keithley 4200A-SCS parameter analyzer. Run it from this directory:

```text
python LGAD_IV.py --voltage 1.0 --compliance 0.001 --voltage_range 1
```

The arguments are:

- `--voltage`: voltage forced by SMU1, in volts; default `1.0`
- `--compliance`: SMU1 current compliance and SMU2 voltage compliance, in amps; default `0.001`
- `--voltage_range`: Keithley source range code; `0` is autorange and `1` is the 20 V range

The example creates an `LGAD_IV` controller, lists VISA resources, and connects to `resources[2]` using the alias `parameterAnalyzer`. It then:

1. Sends `US` to enter the analyzer's user mode.
2. Sends `DV1,<range>,<voltage>,<compliance>` to force the requested voltage on SMU1.
3. Sends `DV2,<range>,0,<compliance>` to hold SMU2 at 0 V as the current-sensing return path.
4. Sends `TI2` and prints the current measured by SMU2.
5. Closes the instrument and VISA resource-manager connections.

The `US`, `DV`, and `TI` commands are Keithley 4200A-SCS KXCI commands, not general GPIB commands. The script currently assumes the analyzer is the third item returned by `list_resources()`; verify the printed resource list and change `resources[2]` if the analyzer appears at another index. Refer to the [Keithley KXCI programming manual](https://www.tek.com/en/manual/parametric-analyzer/model-4200a-scs-kxci-remote-control-programming-keithley-4200a-scs-parameter-analyzer) for command and range-code details.