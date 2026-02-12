from GPIB import GPIBController


class LGAD_IV(GPIBController):
    """
    LGAD (Low Gain Avalanche Detector) IV (Current-Voltage) characterization class.
    Inherits from GPIBController to handle GPIB communication with test instruments.
    """
    
    def __init__(self, visa_library=None):
        """
        Initialize LGAD_IV characterization controller.
        
        Args:
            visa_library: Path to VISA library (optional)
        """
        super().__init__(visa_library)


def ParameterAnalyzer4200ASCS_SMUs():
    """
    Used to test connection and basic commands with a Keithley 4200A-SCS Parameter Analyzer SMUs.
    """
    # Initialize LGAD_IV controller (now inherits from GPIBController)
    lgad_iv = LGAD_IV()

    # List available resources
    resources = lgad_iv.list_resources()
    print(f"Available instruments: {resources}")

    if resources:
        instrument_address = resources[0]
        if lgad_iv.connect_instrument(instrument_address, "my_instrument"):

            # Send a command
            if lgad_iv.send_command("my_instrument", "CH1, 'V1', 'I1', 1, 3"):
                print("Command sent successfully")
            else:
                print("Failed to send command")

            
            # Read a measurement
            #measurement = lgad_iv.query_command("my_instrument", "READ?")
            #print(f"Measurement: {measurement}")
            
            # Clean up
            lgad_iv.disconnect_instrument("my_instrument")

    # Close all connections
    lgad_iv.close_all_connections()


if __name__ == "__main__":
    print("LGAD IV Characterization Test")
    print("=" * 30)
    
    try:
        ParameterAnalyzer4200ASCS_SMUs()
    except Exception as e:
        print(f"Error in LGAD IV test: {e}")
        print("\nNote: Make sure you have:")
        print("- A GPIB instrument connected and powered on")
        print("- The correct VISA library installed and configured")