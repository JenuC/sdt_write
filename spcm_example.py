#!/usr/bin/env python
"""
SPCM Wrapper Example Script
---------------------------
This script demonstrates how to use the SPCM wrapper to interface with 
Becker & Hickl SPC modules for time-correlated single photon counting.
"""

import time
import ctypes
import numpy as np
import matplotlib.pyplot as plt
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
    
    # Get information about available modules
    for mod_no in range(8):  # Check up to 8 possible modules
        mod_info, result = spcm.get_module_info(mod_no)
        if result == 0 and mod_info.in_use != 0:
            print(f"\nModule {mod_no}:")
            print(f"  Type: {mod_info.module_type}")
            print(f"  Bus number: {mod_info.bus_number}")
            print(f"  Slot number: {mod_info.slot_number}")
            print(f"  In use: {mod_info.in_use}")
            
            # Get the parameters for this module
            params, result = spcm.get_parameters(mod_no)
            if result == 0:
                print(f"  ADC Resolution: {params.adc_resolution}")
                print(f"  Collection Time: {params.collect_time} s")
                print(f"  Sync Frequency Divider: {params.sync_freq_div}")
                print(f"  TAC Range: {params.tac_range} ns")
    
    # If we found at least one module, perform a measurement with the first one (module 0)
    mod_no = 0
    
    # Configure the module for a simple measurement
    params, result = spcm.get_parameters(mod_no)
    if result == 0:
        # Modify some parameters for our measurement
        params.collect_time = 1.0  # 1 second collection time
        params.stop_on_time = 1    # Stop on collection time
        params.stop_on_ovfl = 0    # Don't stop on overflow
        
        # Set the modified parameters
        result = spcm.set_parameters(mod_no, params)
        if result < 0:
            print(f"Error setting parameters: {spcm.get_error_string(result)}")
            return
    
    # Start the measurement
    print("\nStarting measurement...")
    result = spcm.start_measurement(mod_no)
    if result < 0:
        print(f"Error starting measurement: {spcm.get_error_string(result)}")
        return
    
    # Monitor the measurement progress
    while True:
        state, result = spcm.test_state(mod_no)
        if result < 0:
            print(f"Error getting module state: {spcm.get_error_string(result)}")
            break
        
        if state == 0:  # SPC_MEASURING
            # Read the current rates
            rates, result = spcm.read_rates(mod_no)
            if result == 0:
                print(f"\rSync Rate: {rates.sync_rate:.1f} Hz, CFD Rate: {rates.cfd_rate:.1f} Hz, TAC Rate: {rates.tac_rate:.1f} Hz", end="")
            
            # Sleep for a short time
            time.sleep(0.1)
        else:
            # Measurement has completed or was stopped
            print("\nMeasurement completed")
            break
    
    # Read data from the measurement
    mem_info, result = spcm.configure_memory(mod_no, params.adc_resolution, 0)
    if result < 0:
        print(f"Error configuring memory: {spcm.get_error_string(result)}")
    else:
        print(f"\nMemory configuration:")
        print(f"  Max blocks: {mem_info.max_block_no}")
        print(f"  Block length: {mem_info.block_length}")
        
        # Read the first block of data
        block = 0
        page = 0
        data_size = 2**params.adc_resolution
        data_buffer = (ctypes.c_ushort * data_size)()
        
        result = spcm.lib.SPC_read_data_block(mod_no, block, page, 0, 0, data_size-1, data_buffer)
        if result < 0:
            print(f"Error reading data block: {spcm.get_error_string(result)}")
        else:
            # Convert to numpy array and plot
            data = np.array([data_buffer[i] for i in range(data_size)], dtype=np.uint16)
            
            plt.figure(figsize=(10, 6))
            plt.plot(data)
            plt.title("SPC Measurement Data")
            plt.xlabel("Time Channel")
            plt.ylabel("Counts")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig("spc_measurement.png")
            plt.show()
    
    # Close the SPCM library
    spcm.close()
    print("SPCM library closed")

if __name__ == "__main__":
    main() 