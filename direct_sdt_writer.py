#!/usr/bin/env python
"""
Direct SDT Writer
---------------
This script creates .sdt files directly without using the SPCM DLL at all.
The created files have a simplified header but should be readable by most software.
"""

import os
import numpy as np
import struct

def create_sdt_header(num_points, num_curves=1, adc_resolution=12, time_per_point=200e-12):
    """
    Create a simplified .sdt file header
    
    Parameters:
    num_points (int): Number of data points per curve
    num_curves (int): Number of curves in the file
    adc_resolution (int): ADC resolution in bits (usually 12)
    time_per_point (float): Time per point in seconds
    
    Returns:
    bytes: The header data as bytes
    """
    # Create a 4096 byte header (standard size for SDT files)
    header = bytearray(4096)
    
    # File type identifier (ASCII "SPC" followed by space)
    header[0:4] = b'SPC '
    
    # Header version
    header[4:6] = struct.pack('<H', 910)  # Version 910 (a common version)
    
    # Number of curves
    header[6:8] = struct.pack('<H', num_curves)
    
    # Number of points per curve
    header[8:12] = struct.pack('<L', num_points)
    
    # Time per point (in nanoseconds)
    time_per_point_ns = time_per_point * 1e9
    header[12:16] = struct.pack('<f', time_per_point_ns)
    
    # ADC resolution
    header[16:18] = struct.pack('<H', adc_resolution)
    
    # TAC range in nanoseconds (arbitrary but reasonable value)
    header[20:24] = struct.pack('<f', time_per_point_ns * num_points)
    
    # Acquisition time in seconds (arbitrary but reasonable value)
    header[28:32] = struct.pack('<f', 1.0)  
    
    # Measurement date/time fields (not critical, setting to zeros)
    # Used in offsets 54-76
    
    # Number of routing channels (set to 1 for simplicity)
    header[42:44] = struct.pack('<H', 1)
    
    # Module type (set to 140 = SPC-140, a common module)
    header[46:48] = struct.pack('<H', 140)
    
    # Additional flags and parameters can be set as needed,
    # but this minimal header should make the file recognizable
    
    return bytes(header)

def create_decay_data(num_points, decay_constant=500, amplitude=10000, background=10, add_noise=True):
    """
    Create exponential decay data
    
    Parameters:
    num_points (int): Number of data points
    decay_constant (float): Decay time constant in channels
    amplitude (float): Initial amplitude
    background (float): Background level
    add_noise (bool): Whether to add Poisson noise
    
    Returns:
    numpy.ndarray: The data as a uint16 array
    """
    x = np.arange(num_points)
    decay = amplitude * np.exp(-x / decay_constant) + background
    
    if add_noise:
        # Add Poisson noise for realism
        noise = np.random.poisson(decay)
        data = noise.astype(np.uint16)
    else:
        data = decay.astype(np.uint16)
    
    return data

def create_sdt_file(output_file, num_points=4096, decay_constant=500, amplitude=10000, 
                   background=10, add_noise=True, time_per_point=200e-12, 
                   adc_resolution=12, curves=None):
    """
    Create an .sdt file with exponential decay data
    
    Parameters:
    output_file (str): Output filename
    num_points (int): Number of data points per curve
    decay_constant (float): Decay time constant in channels
    amplitude (float): Initial amplitude
    background (float): Background level
    add_noise (bool): Whether to add Poisson noise
    time_per_point (float): Time per point in seconds
    adc_resolution (int): ADC resolution in bits
    curves (list): List of numpy arrays, each array is a curve to include. If None, a default curve is created.
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        print(f"Creating SDT file: {output_file}")
        
        # Create the header
        num_curves = len(curves) if curves is not None else 1
        header = create_sdt_header(num_points, num_curves, adc_resolution, time_per_point)
        
        # Create or use the data
        if curves is None:
            # Create a single decay curve
            data = create_decay_data(num_points, decay_constant, amplitude, background, add_noise)
            curves = [data]
        
        # Verify that all curves have the expected length
        for i, curve in enumerate(curves):
            if len(curve) != num_points:
                print(f"Warning: Curve {i} has {len(curve)} points instead of {num_points}")
                # Truncate or pad to match expected length
                if len(curve) > num_points:
                    curves[i] = curve[:num_points]
                else:
                    padded = np.zeros(num_points, dtype=np.uint16)
                    padded[:len(curve)] = curve
                    curves[i] = padded
        
        # Write the file
        with open(output_file, 'wb') as f:
            # Write the header
            f.write(header)
            
            # Write each curve
            for curve in curves:
                # SDT files store data as 16-bit unsigned integers
                curve_data = curve.astype(np.uint16).tobytes()
                f.write(curve_data)
        
        # Verify the file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            expected_size = 4096 + (num_points * 2 * num_curves)  # Header + data
            print(f"Created file: {output_file}")
            print(f"File size: {file_size} bytes (expected: {expected_size} bytes)")
            
            if abs(file_size - expected_size) > 4:  # Allow small difference due to header details
                print("Warning: File size doesn't match expected size exactly")
            
            return True
        else:
            print(f"Error: Failed to create file {output_file}")
            return False
    
    except Exception as e:
        print(f"Error creating SDT file: {e}")
        return False

def create_multi_exponential(num_points=4096):
    """Create a multi-exponential decay curve"""
    x = np.arange(num_points)
    amp1, tau1 = 8000, 200  # Fast component
    amp2, tau2 = 4000, 800  # Slow component
    decay = amp1 * np.exp(-x / tau1) + amp2 * np.exp(-x / tau2)
    noise = np.random.poisson(decay + 1)
    return noise.astype(np.uint16)

def create_gaussian_peak(num_points=4096):
    """Create a Gaussian peak"""
    x = np.arange(num_points)
    amplitude = 10000
    center = 2000
    width = 300
    gaussian = amplitude * np.exp(-(x - center)**2 / (2 * width**2))
    noise = np.random.poisson(gaussian + 1)
    return noise.astype(np.uint16)

def create_demo_files():
    """Create several example SDT files with different data patterns"""
    # 1. Simple exponential decay
    create_sdt_file("direct_decay.sdt")
    
    # 2. Multi-exponential decay
    data = create_multi_exponential()
    create_sdt_file("direct_multi_exp.sdt", curves=[data])
    
    # 3. Gaussian peak
    data = create_gaussian_peak()
    create_sdt_file("direct_gaussian.sdt", curves=[data])
    
    # 4. Multiple curves in one file
    decay1 = create_decay_data(4096, decay_constant=300, amplitude=5000)
    decay2 = create_decay_data(4096, decay_constant=800, amplitude=15000)
    gaussian = create_gaussian_peak()
    create_sdt_file("direct_multicurve.sdt", curves=[decay1, decay2, gaussian], num_curves=3)
    
    # 5. Decay with different parameters
    create_sdt_file("direct_slow_decay.sdt", decay_constant=2000, amplitude=20000)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Create SDT files directly without using SPCM DLL')
    parser.add_argument('--output', '-o', default=None, 
                        help='Output filename (default: creates several example files)')
    parser.add_argument('--size', '-s', type=int, default=4096,
                        help='Number of data points (default: 4096)')
    parser.add_argument('--tau', '-t', type=float, default=500,
                        help='Decay time constant in channels (default: 500)')
    parser.add_argument('--amplitude', '-a', type=float, default=10000,
                        help='Initial amplitude (default: 10000)')
    parser.add_argument('--background', '-b', type=float, default=10,
                        help='Background level (default: 10)')
    parser.add_argument('--no-noise', action='store_true',
                        help='Disable Poisson noise generation')
    parser.add_argument('--demo', action='store_true',
                        help='Create several example files with different data patterns')
    
    args = parser.parse_args()
    
    if args.demo or args.output is None:
        create_demo_files()
        print("\nCreated several example SDT files")
    else:
        success = create_sdt_file(
            args.output, 
            num_points=args.size,
            decay_constant=args.tau,
            amplitude=args.amplitude,
            background=args.background,
            add_noise=not args.no_noise
        )
        
        if success:
            print(f"\nSDT file {args.output} created successfully")
        else:
            print(f"\nFailed to create SDT file {args.output}")
            exit(1)

if __name__ == "__main__":
    main() 