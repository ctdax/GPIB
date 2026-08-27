from GPIB import GPIBController
import argparse

class LGAD_IV(GPIBController):
    """
    LGAD IV characterization class.
    Inherits from GPIBController to handle GPIB communication with test instruments.
    """
    
    def __init__(self, visa_library=None):
        """
        Initialize LGAD_IV characterization controller.
        
        Args:
            visa_library: Path to VISA library (optional)
        """
        super().__init__(visa_library)


def ParameterAnalyzer4200ASCS_SMUs(voltage, compliance=0.001, voltage_range=1):
    """
    Force a voltage on SMU1 and measure the resulting current on SMU2, using the
    4200A-SCS KXCI user-mode command set (US / DV / TI).

    SMU2 is held at 0 V so it acts as the current-sensing return path for the device
    under test, while SMU1 sources the bias voltage.

    Args:
        voltage: Bias voltage to force on SMU1 [V]
        compliance: Current compliance for SMU1, and voltage compliance for SMU2 [A]
        voltage_range: Voltage source range code (0 = autorange, 1 = 20V, 2/3 = 200V, ...)
    """
    # Initialize LGAD_IV controller
    lgad_iv = LGAD_IV()

    # List available resources
    resources = lgad_iv.list_resources()
    print(f"Available resources: {resources}")
    if resources:
        if lgad_iv.connect_instrument(resources[2], "parameterAnalyzer"):
            print(f"Connected to: {resources[2]}")

            # Switch to user mode - required before DV/DI/TV/TI commands
            lgad_iv.send_command("parameterAnalyzer", "US")

            # SMU1: force the bias voltage, set current compliance
            dv1_command = f"DV1,{voltage_range},{voltage},{compliance}"
            if lgad_iv.send_command("parameterAnalyzer", dv1_command):
                print(f"Succesfully sent command '{dv1_command}' to {resources[2]}")
            else:
                print(f"Failed to send command '{dv1_command}' to {resources[2]}")

            # SMU2: hold at 0 V so it acts as the current-sensing return path
            dv2_command = f"DV2,{voltage_range},0,{compliance}"
            if lgad_iv.send_command("parameterAnalyzer", dv2_command):
                print(f"Succesfully sent command '{dv2_command}' to {resources[2]}")
            else:
                print(f"Failed to send command '{dv2_command}' to {resources[2]}")

            # Trigger a current measurement on SMU2 and read the result back
            current_reading = lgad_iv.query_command("parameterAnalyzer", "TI2")
            print(f"Current measured on SMU2: {current_reading}")

    # Close all connections
    lgad_iv.close_all_connections()


if __name__ == "__main__":
    print("LGAD IV Characterization")
    print("=" * 30)

    # For documentation of available commands, see the KXCI Remote Control Programming
    # manual: DV/DI on page 5-41, TV/TI on page 5-43, US on page 5-39
    # https://www.tek.com/en/manual/parametric-analyzer/model-4200a-scs-kxci-remote-control-programming-keithley-4200a-scs-parameter-analyzer
    parser = argparse.ArgumentParser(description="Force a voltage on SMU1 and measure current on SMU2")
    parser.add_argument("--voltage", type=float, default=1.0, help="Bias voltage to force on SMU1 [V]")
    parser.add_argument("--compliance", type=float, default=0.001, help="Current compliance on SMU1 / voltage compliance on SMU2")
    parser.add_argument("--voltage_range", type=int, default=1, help="0=autorange, 1=20V, 2/3=200V, 4=200mV (preamp), 5=2V (preamp)")
    args = parser.parse_args()
    
    try:
        ParameterAnalyzer4200ASCS_SMUs(args.voltage, args.compliance, args.voltage_range)
    except Exception as e:
        print(f"Error in LGAD IV test: {e}")
        print("\nNote: Make sure you have:")
        print("- A GPIB instrument connected and powered on")
        print("- The correct VISA library installed and configured")