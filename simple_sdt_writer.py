#!/usr/bin/env python
"""
Simple SDT Writer
----------------
A minimal script to create a single .sdt file without requiring a physical module.
"""

import os
import numpy as np
import ctypes
from spcm_wrapper import SPCM, SPC_Error

def create_and_save_sdt(output_file="simple_decay.sdt", data_size=4096):
    """
    Create a simple decay curve and save it as an .sdt file
    
    Parameters:
    output_file (str): Name of the output .sdt file
    data_size (int): Number of data points (typically 2^n)
    
    Returns:
    bool: True if successful, False otherwise
    """
    print(f"Creating .sdt file: {output_file}")
    
    # Step 1: Initialize the SPCM wrapper
    try:
        spcm = SPCM()
        print("Successfully loaded SPCM DLL")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the SPCM DLL is installed correctly")
        return False
    
    # Step 2: Initialize the DLL (required even without physical hardware)
    result = spcm.init()
    if result < 0:
        print(f"Warning: SPC initialization returned error: {spcm.get_error_string(result)}")
        print("This is expected if no module is connected. Continuing with SDT file creation...")
    else:
        print("SPC DLL initialized successfully")
    
    # Step 3: Simulate a module presence (even without physical hardware)
    mod_no = 0
    result = spcm.simulate_module_for_sdt(mod_no)
    if result < 0:
        print(f"Warning: Module simulation returned error: {spcm.get_error_string(result)}")
        print("Attempting to continue anyway...")
    else:
        print("Module simulation successful")
    
    # Step 4: Create the data (simple exponential decay with noise)
    try:
        print("Creating decay curve data...")
        x = np.arange(data_size)
        
        # Parameters for the decay curve
        decay_constant = 500
        amplitude = 10000
        background = 10
        
        # Create decay with some baseline
        decay = amplitude * np.exp(-x / decay_constant) + background
        
        # Add Poisson noise (typical for photon counting)
        noise = np.random.poisson(decay)
        data = noise.astype(np.uint16)  # Convert to unsigned 16-bit integers
        
        print(f"Created decay curve with {data_size} points (τ = {decay_constant} channels)")
    except Exception as e:
        print(f"Error creating data: {e}")
        spcm.close()
        return False
    
    # Step 5: Save the data to an .sdt file
    try:
        print(f"Saving data to {output_file}...")
        result = spcm.save_data_to_sdtfile(mod_no, data, output_file)
        
        if result < 0:
            print(f"Error saving data to SDT file: {spcm.get_error_string(result)}")
            spcm.close()
            return False
        
        # Verify the file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"Successfully created {output_file} ({file_size} bytes)")
        else:
            print(f"Error: File {output_file} was not created")
            spcm.close()
            return False
    except Exception as e:
        print(f"Error saving data: {e}")
        spcm.close()
        return False
    
    # Step 6: Clean up
    spcm.close()
    print("SPCM library closed")
    
    return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create a simple .sdt file')
    parser.add_argument('--output', '-o', default='simple_decay.sdt',
                        help='Output file name (default: simple_decay.sdt)')
    parser.add_argument('--size', '-s', type=int, default=4096,
                        help='Data size (default: 4096)')
    args = parser.parse_args()
    
    success = create_and_save_sdt(args.output, args.size)
    
    if success:
        print("SDT file creation completed successfully!")
    else:
        print("SDT file creation failed.")
        exit(1)

if __name__ == "__main__":
    main() 