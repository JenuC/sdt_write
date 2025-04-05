#!/usr/bin/env python
"""
Write SDT File Offline Example
-----------------------------
This script demonstrates how to create and save .sdt files without
requiring a physical SPC module to be connected.
"""

import os
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
    
    # Initialize the DLL - this is required even without physical hardware
    # The initialization might fail if no module is present, but we can still 
    # use the save_data_to_sdtfile function
    result = spcm.init()
    if result < 0:
        print(f"Warning: SPC initialization returned error: {spcm.get_error_string(result)}")
        print("This is expected if no module is connected. Continuing with SDT file creation...")
    else:
        print("SPC DLL initialized successfully")
    
    # Simulate a module presence (even without physical hardware)
    mod_no = 0
    result = spcm.simulate_module_for_sdt(mod_no)
    if result < 0:
        print(f"Warning: Module simulation returned error: {spcm.get_error_string(result)}")
        print("Attempting to continue anyway...")
    else:
        print("Module simulation successful")
    
    print("Creating and saving different types of data...")
    
    # Example 1: Create a synthetic decay curve
    create_decay_curve(spcm)
    
    # Example 2: Create a multi-exponential decay curve
    create_multi_exponential(spcm)
    
    # Example 3: Create a Gaussian peak
    create_gaussian_peak(spcm)
    
    # Example 4: Create a custom pattern
    create_custom_pattern(spcm)
    
    # Example 5: Create a trace with multiple peaks
    create_multi_peak_trace(spcm)
    
    print("\nAll examples completed.")
    
    # Close the library
    spcm.close()
    print("SPCM library closed")

def create_decay_curve(spcm):
    """Create a single exponential decay curve and save it to an .sdt file"""
    print("\n1. Creating single exponential decay curve...")
    
    # Create a simple decay curve with some noise
    data_size = 4096  # 12-bit resolution (2^12)
    x = np.arange(data_size)
    
    # Exponential decay with time constant of 500 channels
    decay_constant = 500
    amplitude = 10000
    
    decay = amplitude * np.exp(-x / decay_constant)
    
    # Add some Poisson noise (typical for photon counting)
    noise = np.random.poisson(decay + 1)
    data = noise.astype(np.uint16)
    
    # Save to .sdt file
    output_file = "single_exponential.sdt"
    print(f"   Saving to {output_file}...")
    
    # Use module number 0 (even though no module is connected)
    mod_no = 0
    result = spcm.save_data_to_sdtfile(mod_no, data, output_file)
    
    if result < 0:
        print(f"   Error saving data to SDT file: {spcm.get_error_string(result)}")
    else:
        print(f"   Data successfully saved to {output_file}")
        
        # Print some information about the file
        file_size = os.path.getsize(output_file)
        print(f"   File size: {file_size} bytes")
        print(f"   Data points: {data_size}")
        print(f"   Decay constant: {decay_constant} channels")
    
    # Visualize the data
    plt.figure(figsize=(10, 6))
    plt.plot(x, data)
    plt.yscale('log')
    plt.title(f"Single Exponential Decay (τ = {decay_constant} channels)")
    plt.xlabel("Time Channel")
    plt.ylabel("Counts (log scale)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("single_exponential.png")
    plt.close()

def create_multi_exponential(spcm):
    """Create a multi-exponential decay curve and save it to an .sdt file"""
    print("\n2. Creating multi-exponential decay curve...")
    
    data_size = 4096
    x = np.arange(data_size)
    
    # Two exponential components with different amplitudes and decay constants
    amp1, tau1 = 8000, 200  # Fast component
    amp2, tau2 = 4000, 800  # Slow component
    
    decay = amp1 * np.exp(-x / tau1) + amp2 * np.exp(-x / tau2)
    
    # Add some Poisson noise
    noise = np.random.poisson(decay + 1)
    data = noise.astype(np.uint16)
    
    # Save to .sdt file
    output_file = "multi_exponential.sdt"
    print(f"   Saving to {output_file}...")
    
    mod_no = 0
    result = spcm.save_data_to_sdtfile(mod_no, data, output_file)
    
    if result < 0:
        print(f"   Error saving data to SDT file: {spcm.get_error_string(result)}")
    else:
        print(f"   Data successfully saved to {output_file}")
        print(f"   Components: τ1 = {tau1} channels, τ2 = {tau2} channels")
    
    # Visualize the data
    plt.figure(figsize=(10, 6))
    plt.plot(x, data)
    plt.yscale('log')
    plt.title(f"Multi-Exponential Decay (τ1 = {tau1}, τ2 = {tau2} channels)")
    plt.xlabel("Time Channel")
    plt.ylabel("Counts (log scale)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("multi_exponential.png")
    plt.close()

def create_gaussian_peak(spcm):
    """Create a Gaussian peak and save it to an .sdt file"""
    print("\n3. Creating Gaussian peak...")
    
    data_size = 4096
    x = np.arange(data_size)
    
    # Gaussian parameters
    amplitude = 10000
    center = 2000
    width = 300
    
    # Create Gaussian peak
    gaussian = amplitude * np.exp(-(x - center)**2 / (2 * width**2))
    
    # Add some Poisson noise
    noise = np.random.poisson(gaussian + 1)
    data = noise.astype(np.uint16)
    
    # Save to .sdt file
    output_file = "gaussian_peak.sdt"
    print(f"   Saving to {output_file}...")
    
    mod_no = 0
    result = spcm.save_data_to_sdtfile(mod_no, data, output_file)
    
    if result < 0:
        print(f"   Error saving data to SDT file: {spcm.get_error_string(result)}")
    else:
        print(f"   Data successfully saved to {output_file}")
        print(f"   Peak center: {center} channels, width: {width} channels")
    
    # Visualize the data
    plt.figure(figsize=(10, 6))
    plt.plot(x, data)
    plt.title(f"Gaussian Peak (Center = {center}, Width = {width} channels)")
    plt.xlabel("Time Channel")
    plt.ylabel("Counts")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("gaussian_peak.png")
    plt.close()

def create_custom_pattern(spcm):
    """Create a custom pattern (sawtooth) and save it to an .sdt file"""
    print("\n4. Creating custom pattern (sawtooth)...")
    
    data_size = 4096
    x = np.arange(data_size)
    
    # Create a sawtooth pattern with 5 teeth
    num_teeth = 5
    tooth_length = data_size // num_teeth
    
    pattern = np.zeros(data_size)
    for i in range(num_teeth):
        start = i * tooth_length
        end = (i + 1) * tooth_length
        pattern[start:end] = np.linspace(0, 20000, tooth_length)
    
    # Add some noise
    noise = np.random.normal(0, 200, data_size)
    pattern = pattern + noise
    pattern = np.clip(pattern, 0, 65535)  # Ensure within uint16 range
    data = pattern.astype(np.uint16)
    
    # Save to .sdt file
    output_file = "sawtooth_pattern.sdt"
    print(f"   Saving to {output_file}...")
    
    mod_no = 0
    result = spcm.save_data_to_sdtfile(mod_no, data, output_file)
    
    if result < 0:
        print(f"   Error saving data to SDT file: {spcm.get_error_string(result)}")
    else:
        print(f"   Data successfully saved to {output_file}")
        print(f"   Pattern: Sawtooth with {num_teeth} teeth")
    
    # Visualize the data
    plt.figure(figsize=(10, 6))
    plt.plot(x, data)
    plt.title(f"Sawtooth Pattern ({num_teeth} teeth)")
    plt.xlabel("Time Channel")
    plt.ylabel("Counts")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("sawtooth_pattern.png")
    plt.close()

def create_multi_peak_trace(spcm):
    """Create a trace with multiple peaks and save it to an .sdt file"""
    print("\n5. Creating a trace with multiple peaks...")
    
    data_size = 4096
    x = np.arange(data_size)
    
    # Create a trace with multiple Gaussian peaks
    peak_centers = [500, 1200, 2000, 3000, 3800]
    peak_widths = [100, 150, 200, 180, 120]
    peak_amplitudes = [5000, 10000, 8000, 12000, 6000]
    
    trace = np.zeros(data_size)
    for center, width, amplitude in zip(peak_centers, peak_widths, peak_amplitudes):
        peak = amplitude * np.exp(-(x - center)**2 / (2 * width**2))
        trace += peak
    
    # Add some baseline
    baseline = 100
    trace += baseline
    
    # Add Poisson noise
    noise = np.random.poisson(trace)
    data = noise.astype(np.uint16)
    
    # Save to .sdt file
    output_file = "multi_peak_trace.sdt"
    print(f"   Saving to {output_file}...")
    
    mod_no = 0
    result = spcm.save_data_to_sdtfile(mod_no, data, output_file)
    
    if result < 0:
        print(f"   Error saving data to SDT file: {spcm.get_error_string(result)}")
    else:
        print(f"   Data successfully saved to {output_file}")
        print(f"   Number of peaks: {len(peak_centers)}")
    
    # Visualize the data
    plt.figure(figsize=(10, 6))
    plt.plot(x, data)
    plt.title(f"Trace with Multiple Peaks ({len(peak_centers)} peaks)")
    plt.xlabel("Time Channel")
    plt.ylabel("Counts")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("multi_peak_trace.png")
    plt.close()
    
    # Also create a zoomed-in view of the first peak
    plt.figure(figsize=(10, 6))
    zoom_range = slice(max(0, peak_centers[0] - 3*peak_widths[0]), 
                        min(data_size, peak_centers[0] + 3*peak_widths[0]))
    plt.plot(x[zoom_range], data[zoom_range])
    plt.title(f"Zoomed View of Peak 1 (Center = {peak_centers[0]}, Width = {peak_widths[0]})")
    plt.xlabel("Time Channel")
    plt.ylabel("Counts")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("peak1_zoom.png")
    plt.close()

if __name__ == "__main__":
    main() 