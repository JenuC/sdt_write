#!/usr/bin/env python
"""
Save SDT File Example
-------------------
This script demonstrates how to save measurement data to an .sdt file
using the SPC_save_data_to_sdtfile function.
"""

import os
import numpy as np
import ctypes
from spcm_wrapper import SPCM, SPC_Error

def main():
    # Initialize the SPCM wrapper
    try:
        spcm = SPCM()
        print("Successfully loaded SPCM DLL")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the SPCM DLL is installed correctly")
        return
    
    # Initialize the module
    result = spcm.init()
    if result < 0:
        print(f"Error initializing SPC module: {spcm.get_error_string(result)}")
        return
    
    print("SPC module initialized successfully")
    
    # Example 1: Save data directly from the module
    save_data_from_module(spcm)
    
    # Example 2: Create synthetic data and save it
    create_and_save_data(spcm)
    
    # Close the SPCM library
    spcm.close()
    print("SPCM library closed")

def save_data_from_module(spcm):
    """Read data from the SPC module and save it to an .sdt file"""
    mod_no = 0  # Use the first module
    
    # Check if the module is available
    mod_info, result = spcm.get_module_info(mod_no)
    if result != 0 or mod_info.in_use == 0:
        print(f"Module {mod_no} not found or not in use")
        return
    
    print(f"Saving data from module {mod_no}")
    
    # Configure the module for a simple measurement
    params, result = spcm.get_parameters(mod_no)
    if result != 0:
        print(f"Error getting parameters: {spcm.get_error_string(result)}")
        return
    
    # Modify parameters for measurement
    params.collect_time = 1.0  # 1 second collection time
    params.stop_on_time = 1    # Stop on collection time
    params.stop_on_ovfl = 0    # Don't stop on overflow
    
    # Set the modified parameters
    result = spcm.set_parameters(mod_no, params)
    if result < 0:
        print(f"Error setting parameters: {spcm.get_error_string(result)}")
        return
    
    # Configure memory
    mem_info, result = spcm.configure_memory(mod_no, params.adc_resolution, 0)
    if result < 0:
        print(f"Error configuring memory: {spcm.get_error_string(result)}")
        return
    
    # Start measurement
    print("Starting measurement...")
    result = spcm.start_measurement(mod_no)
    if result < 0:
        print(f"Error starting measurement: {spcm.get_error_string(result)}")
        return
    
    # Wait for measurement to complete
    import time
    while True:
        state, result = spcm.test_state(mod_no)
        if result < 0:
            print(f"Error getting module state: {spcm.get_error_string(result)}")
            break
        
        if state != 0:  # Not measuring anymore
            print("Measurement completed")
            break
        
        # Show some progress
        rates, _ = spcm.read_rates(mod_no)
        print(f"\rSync Rate: {rates.sync_rate:.1f} Hz, CFD Rate: {rates.cfd_rate:.1f} Hz", end="")
        time.sleep(0.1)
    
    print("\nReading measurement data...")
    
    # Read the measured data
    block = 0
    page = 0
    data_size = 2**params.adc_resolution
    data_buffer = (ctypes.c_ushort * data_size)()
    
    result = spcm.lib.SPC_read_data_block(mod_no, block, page, 0, 0, data_size-1, data_buffer)
    if result < 0:
        print(f"Error reading data block: {spcm.get_error_string(result)}")
        return
    
    # Save to .sdt file
    output_file = "module_measurement.sdt"
    print(f"Saving data to {output_file}...")
    
    result = spcm.save_data_to_sdtfile(mod_no, data_buffer, output_file)
    if result < 0:
        print(f"Error saving data to SDT file: {spcm.get_error_string(result)}")
    else:
        print(f"Data successfully saved to {output_file}")

def create_and_save_data(spcm):
    """Create synthetic data and save it to an .sdt file"""
    print("\nCreating synthetic data...")
    
    # Create a simple decay curve with some noise
    data_size = 4096  # 12-bit resolution (2^12)
    x = np.arange(data_size)
    
    # Exponential decay with time constant of 500 channels
    decay = 10000 * np.exp(-x / 500)
    
    # Add some noise
    noise = np.random.poisson(decay + 1)
    data = noise.astype(np.uint16)
    
    # Save to .sdt file
    output_file = "synthetic_decay.sdt"
    print(f"Saving synthetic data to {output_file}...")
    
    mod_no = 0  # Use the first module (even if not present, the DLL needs a module number)
    result = spcm.save_data_to_sdtfile(mod_no, data, output_file)
    
    if result < 0:
        print(f"Error saving data to SDT file: {spcm.get_error_string(result)}")
    else:
        print(f"Data successfully saved to {output_file}")
        
        # Print some information about the file
        file_size = os.path.getsize(output_file)
        print(f"File size: {file_size} bytes")
        print(f"Data points: {data_size}")

if __name__ == "__main__":
    main() 