#!/usr/bin/env python3
"""
GPIB Communication Module

This module provides functionality to communicate with instruments via GPIB
using PyVISA library. It includes methods for sending commands, reading responses,
and managing GPIB connections.

Requirements:
    - PyVISA: pip install pyvisa
    - NI-VISA or compatible VISA implementation
"""

import pyvisa
import time
from typing import Optional, List, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPIBController:
    """
    A class to handle GPIB communication with instruments.
    """
    
    def __init__(self, visa_library: Optional[str] = None):
        """
        Initialize GPIB controller.
        
        Args:
            visa_library: Path to VISA library (optional)
        """
        try:
            if visa_library:
                self.rm = pyvisa.ResourceManager(visa_library)
            else:
                self.rm = pyvisa.ResourceManager()
            self.instruments = {}
            logger.info("GPIB Controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GPIB controller: {e}")
            raise
    
    def list_resources(self) -> List[str]:
        """
        List all available VISA resources.
        
        Returns:
            List of available resource names
        """
        try:
            resources = self.rm.list_resources()
            logger.info(f"Available resources: {resources}")
            return list(resources)
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return []
    
    def connect_instrument(self, resource_name: str, alias: str = None) -> bool:
        """
        Connect to a GPIB instrument.
        
        Args:
            resource_name: VISA resource name (e.g., 'GPIB0::10::INSTR')
            alias: Optional alias for the instrument
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            instrument = self.rm.open_resource(resource_name)
            # Set common timeout and termination settings
            instrument.timeout = 10000  # 10 seconds
            instrument.write_termination = '\n'
            instrument.read_termination = '\n'
            
            # Use alias if provided, otherwise use resource name
            key = alias if alias else resource_name
            self.instruments[key] = instrument
            
            logger.info(f"Connected to instrument: {resource_name} (alias: {key})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {resource_name}: {e}")
            return False
    
    def disconnect_instrument(self, identifier: str) -> bool:
        """
        Disconnect from a GPIB instrument.
        
        Args:
            identifier: Resource name or alias of the instrument
            
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if identifier in self.instruments:
                self.instruments[identifier].close()
                del self.instruments[identifier]
                logger.info(f"Disconnected from instrument: {identifier}")
                return True
            else:
                logger.warning(f"Instrument {identifier} not found")
                return False
        except Exception as e:
            logger.error(f"Error disconnecting from {identifier}: {e}")
            return False
    
    def send_command(self, identifier: str, command: str, delay: float = 0.1) -> bool:
        """
        Send a command to a GPIB instrument.
        
        Args:
            identifier: Resource name or alias of the instrument
            command: SCPI or instrument-specific command
            delay: Delay after sending command (seconds)
            
        Returns:
            True if command sent successfully, False otherwise
        """
        try:
            if identifier not in self.instruments:
                logger.error(f"Instrument {identifier} not connected")
                return False
            
            self.instruments[identifier].write(command)
            time.sleep(delay)
            logger.debug(f"Sent command to {identifier}: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command '{command}' to {identifier}: {e}")
            return False
    
    def query_command(self, identifier: str, command: str, delay: float = 0.1) -> Optional[str]:
        """
        Send a query command and read the response.
        
        Args:
            identifier: Resource name or alias of the instrument
            command: SCPI or instrument-specific query command
            delay: Delay after sending command (seconds)
            
        Returns:
            Response string if successful, None otherwise
        """
        try:
            if identifier not in self.instruments:
                logger.error(f"Instrument {identifier} not connected")
                return None
            
            response = self.instruments[identifier].query(command)
            time.sleep(delay)
            logger.debug(f"Query to {identifier}: {command} -> {response.strip()}")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error querying command '{command}' to {identifier}: {e}")
            return None
    
    def read_response(self, identifier: str) -> Optional[str]:
        """
        Read a response from a GPIB instrument.
        
        Args:
            identifier: Resource name or alias of the instrument
            
        Returns:
            Response string if successful, None otherwise
        """
        try:
            if identifier not in self.instruments:
                logger.error(f"Instrument {identifier} not connected")
                return None
            
            response = self.instruments[identifier].read()
            logger.debug(f"Read from {identifier}: {response.strip()}")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error reading from {identifier}: {e}")
            return None
    
    def get_identification(self, identifier: str) -> Optional[str]:
        """
        Get instrument identification using *IDN? command.
        
        Args:
            identifier: Resource name or alias of the instrument
            
        Returns:
            Instrument identification string if successful, None otherwise
        """
        return self.query_command(identifier, "*IDN?")
    
    def reset_instrument(self, identifier: str) -> bool:
        """
        Reset instrument to default state using *RST command.
        
        Args:
            identifier: Resource name or alias of the instrument
            
        Returns:
            True if reset successful, False otherwise
        """
        return self.send_command(identifier, "*RST", delay=2.0)
    
    def clear_instrument(self, identifier: str) -> bool:
        """
        Clear instrument status using *CLS command.
        
        Args:
            identifier: Resource name or alias of the instrument
            
        Returns:
            True if clear successful, False otherwise
        """
        return self.send_command(identifier, "*CLS")
    
    def wait_for_completion(self, identifier: str, timeout: float = 30.0) -> bool:
        """
        Wait for instrument operation to complete using *OPC? command.
        
        Args:
            identifier: Resource name or alias of the instrument
            timeout: Maximum wait time in seconds
            
        Returns:
            True if operation completed, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.query_command(identifier, "*OPC?")
            if response == "1":
                return True
            time.sleep(0.1)
        
        logger.warning(f"Timeout waiting for operation completion on {identifier}")
        return False
    
    def close_all_connections(self):
        """
        Close all instrument connections and clean up resources.
        """
        for identifier in list(self.instruments.keys()):
            self.disconnect_instrument(identifier)
        
        try:
            self.rm.close()
            logger.info("All GPIB connections closed")
        except Exception as e:
            logger.error(f"Error closing resource manager: {e}")


# Example usage functions
def test_connection():
    """
    Test GPIB connection and basic commands.
    """
    # Initialize GPIB controller
    gpib = GPIBController()
    
    # List available resources
    resources = gpib.list_resources()
    print(f"Available instruments: {resources}")
    
    if resources:
        instrument_address = resources[0]  # Use first available instrument
        if gpib.connect_instrument(instrument_address, "my_instrument"):
            gpib.disconnect_instrument("my_instrument")
    
    # Close all connections
    gpib.close_all_connections()


if __name__ == "__main__":
    print("GPIB Communication Test")
    print("=" * 30)
    
    try:
        test_connection()
    except Exception as e:
        print(f"Error in example: {e}")
        print("\nNote: Make sure you have:")
        print("1. PyVISA installed: pip install pyvisa")
        print("2. VISA runtime installed (NI-VISA or compatible)")
        print("3. GPIB instruments connected and powered on")
