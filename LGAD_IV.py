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


def ParameterAnalyzer4200ASCS_SMUs(channel, voltage, current, source_mode, source_function):
    """
    Used to perform the LGAD IV characterization with Keithley 4200A-SCS Parameter Analyzer SMUs.
    """
    # Initialize LGAD_IV controller
    lgad_iv = LGAD_IV()

    # List available resources
    resources = lgad_iv.list_resources()
    print(f"Available resources: {resources}")
    if resources:
        if lgad_iv.connect_instrument(resources[2], "parameterAnalyzer"):
            print(f"Connected to: {resources[2]}")

            # Send a command
            command = f"CH{channel}, 'V{voltage}', 'I{current}', {source_mode}, {source_function}"
            if lgad_iv.send_command("parameterAnalyzer", command):
                print(f"Succesfully sent command '{command}' to {resources[2]}")
            else:
                print(f"Failed to send command '{command} to {resources[2]}'")

    # Close all connections
    lgad_iv.close_all_connections()


if __name__ == "__main__":
    print("LGAD IV Characterization")
    print("=" * 30)

    # For documentaiton of available ParameterAnalyzer4200ASCS_SMUs commands, see page 58 in the pdf found here https://www.tek.com/en/manual/parametric-analyzer/model-4200a-scs-kxci-remote-control-programming-keithley-4200a-scs-parameter-analyzer
    parser = argparse.ArgumentParser(description="Perform IV curve characterization on an LGAD by sending GPIB commands to ParameterAnalyzer4200ASCS_SMUs")
    parser.add_argument("--channel", type=int, default=1, help="Which SMU to send commands to")
    parser.add_argument("--voltage", type=float, default=1.0, help="What voltage to hold the SMU at [V]")
    parser.add_argument("--current", type=float, default=0.001, help="What current to hold the SMU at [A]")
    parser.add_argument("--source_mode", type=int, default=1, help="1=volatage, 2=current, 3=common")
    parser.add_argument("--source_function", type=int, default=3, help="1=VAR1 sweep, 2=VAR2 sweep, 3=constant, 4=VAR1")
    args = parser.parse_args()
    
    try:
        ParameterAnalyzer4200ASCS_SMUs(args.channel, args.voltage, args.current, args.source_mode, args.source_function)
    except Exception as e:
        print(f"Error in LGAD IV test: {e}")
        print("\nNote: Make sure you have:")
        print("- A GPIB instrument connected and powered on")
        print("- The correct VISA library installed and configured")