#!/usr/bin/env python
"""
Force SDT Writer
---------------
This script forcefully writes .sdt files without requiring hardware by using
a more aggressive approach to bypass DLL checks.
"""

import os
import numpy as np
import ctypes
from spcm_wrapper import SPCM, SPC_Error, SPCdata, SPCMemConfig, SPCModInfo

def force_write_sdt(output_file="forced_decay.sdt", data_size=4096):
    """
    Forcefully write a decay curve to an .sdt file bypassing normal checks
    
    Parameters:
    output_file (str): Output filename
    data_size (int): Number of data points
    
    Returns:
    bool: True if successful, False otherwise
    """
    print(f"Forcefully creating .sdt file: {output_file}")
    
    # Load the SPCM DLL
    try:
        spcm = SPCM()
        print("Successfully loaded SPCM DLL")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False
    
    # Initialize (will fail without hardware, but we continue anyway)
    result = spcm.init()
    print(f"DLL initialization result: {result} (negative is expected without hardware)")
    
    # ALTERNATIVE 1: Direct calling the underlying SPC_save_data_to_sdtfile function
    # This is the most direct approach - bypassing the wrapper method
    try:
        print("APPROACH 1: Direct calling the SPC_save_data_to_sdtfile function")
        
        # Create a decay curve with noise (same as before)
        x = np.arange(data_size)
        decay_constant = 500
        amplitude = 10000
        decay = amplitude * np.exp(-x / decay_constant)
        noise = np.random.poisson(decay + 1)
        data = noise.astype(np.uint16)
        
        # Create a ctypes buffer
        buffer_size = data.size
        ctypes_buffer = (ctypes.c_ushort * buffer_size)()
        for i in range(buffer_size):
            ctypes_buffer[i] = data[i]
        
        # Calculate number of bytes (each element is 2 bytes for c_ushort)
        bytes_no = buffer_size * 2
        
        # Directly call the DLL function with module 0
        mod_no = 0
        result = spcm.lib.SPC_save_data_to_sdtfile(mod_no, ctypes_buffer, bytes_no, output_file.encode('utf-8'))
        
        if result == 0:
            print(f"SUCCESS! File saved to {output_file}")
            # Verify the file was created
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"File size: {file_size} bytes")
                # Skip other approaches if this one worked
                spcm.close()
                return True
        else:
            print(f"FAILED with error: {spcm.get_error_string(result)}")
    except Exception as e:
        print(f"Error in approach 1: {e}")
    
    # ALTERNATIVE 2: Try using a different module number
    try:
        print("\nAPPROACH 2: Trying different module numbers")
        
        # Create the same data again
        x = np.arange(data_size)
        decay = amplitude * np.exp(-x / decay_constant)
        noise = np.random.poisson(decay + 1)
        data = noise.astype(np.uint16)
        
        # Try with several module numbers
        for mod_no in range(8):  # Try all 8 possible module slots
            print(f"Trying with module number {mod_no}...")
            
            # First try to simulate the module
            spcm.simulate_module_for_sdt(mod_no)
            
            # Then try to save
            alt_output = f"alt_mod{mod_no}_{output_file}"
            result = spcm.save_data_to_sdtfile(mod_no, data, alt_output)
            
            if result == 0:
                print(f"SUCCESS with module {mod_no}! File saved to {alt_output}")
                if os.path.exists(alt_output):
                    file_size = os.path.getsize(alt_output)
                    print(f"File size: {file_size} bytes")
                    # If it worked, copy this file to the original requested output
                    import shutil
                    shutil.copy(alt_output, output_file)
                    print(f"Copied to requested name: {output_file}")
                    # Skip other approaches
                    spcm.close()
                    return True
            else:
                print(f"  Failed with error: {spcm.get_error_string(result)}")
    except Exception as e:
        print(f"Error in approach 2: {e}")
        
    # ALTERNATIVE 3: Use a workaround to manually create a basic .sdt file
    try:
        print("\nAPPROACH 3: Creating a basic .sdt file manually")
        
        # Create the data
        x = np.arange(data_size)
        decay = amplitude * np.exp(-x / decay_constant)
        noise = np.random.poisson(decay + 1)
        data = noise.astype(np.uint16)
        
        # Minimal SDT header (just enough to be recognized)
        # SDT has a 4096-byte header followed by the raw data
        header = bytearray(4096)
        
        # Put some magic values in the header
        header[0:4] = b'SPC '  # Magic identifier
        header[4:6] = (data_size).to_bytes(2, byteorder='little')  # Size
        header[6:8] = (1).to_bytes(2, byteorder='little')  # Number of curves
        
        # Create the file manually
        with open(output_file, 'wb') as f:
            f.write(header)
            f.write(data.tobytes())
        
        print(f"Manually created file: {output_file}")
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"File size: {file_size} bytes")
            print("Note: This file has a simplified header and may not be fully compatible with all software")
            spcm.close()
            return True
    except Exception as e:
        print(f"Error in approach 3: {e}")
    
    # Clean up
    spcm.close()
    print("All approaches failed. SDT file could not be created.")
    return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Force creation of .sdt files without hardware')
    parser.add_argument('--output', '-o', default='forced_decay.sdt', 
                        help='Output filename (default: forced_decay.sdt)')
    parser.add_argument('--size', '-s', type=int, default=4096,
                        help='Data size (default: 4096)')
    args = parser.parse_args()
    
    success = force_write_sdt(args.output, args.size)
    
    if success:
        print("\nSDT file creation completed successfully!")
    else:
        print("\nAll approaches failed. SDT file could not be created.")
        exit(1)

if __name__ == "__main__":
    main() 