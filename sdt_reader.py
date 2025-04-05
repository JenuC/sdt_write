#!/usr/bin/env python
"""
SDT Reader - Utility for reading Becker & Hickl SPC data files
-------------------------------------------------------------
This script provides functions to read .sdt files saved by Becker & Hickl SPC modules.
"""

import os
import ctypes
import numpy as np
import matplotlib.pyplot as plt
from spcm_wrapper import SPCM, PhotStreamInfo, PhotInfo, PhotInfo64

class SDTReader:
    """Class for reading Becker & Hickl .sdt files"""
    
    def __init__(self):
        """Initialize the SDT reader with an SPCM instance"""
        try:
            self.spcm = SPCM()
            self.initialized = True
        except FileNotFoundError as e:
            print(f"Error: {e}")
            self.initialized = False
    
    def read_sdt_header(self, file_path):
        """Read the header information from an .sdt file"""
        if not self.initialized:
            print("SPCM not initialized")
            return None
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            return None
        
        # Initialize a photon stream for the file
        # Common fifo_types: FIFO_32 = 3, FIFO_48 = 2, FIFO_IMG = 9
        fifo_type = 3  # Default to FIFO_32
        stream_type = 0
        what_to_read = 1  # Read valid photons
        
        stream_handle, result = self.spcm.init_phot_stream(fifo_type, file_path, 1, stream_type, what_to_read)
        
        if result < 0 or stream_handle < 0:
            print(f"Error initializing photon stream: {self.spcm.get_error_string(result)}")
            return None
        
        # Get stream info
        stream_info, result = self.spcm.get_phot_stream_info(stream_handle)
        
        if result < 0:
            print(f"Error getting stream info: {self.spcm.get_error_string(result)}")
            self.spcm.close_phot_stream(stream_handle)
            return None
        
        # Close the stream
        self.spcm.close_phot_stream(stream_handle)
        
        return stream_info
    
    def read_photons(self, file_path, max_photons=1000):
        """Read photons from an .sdt file"""
        if not self.initialized:
            print("SPCM not initialized")
            return None
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            return None
        
        # Initialize a photon stream for the file
        # Common fifo_types: FIFO_32 = 3, FIFO_48 = 2, FIFO_IMG = 9
        fifo_type = 3  # Default to FIFO_32
        stream_type = 0
        what_to_read = 1  # Read valid photons
        
        stream_handle, result = self.spcm.init_phot_stream(fifo_type, file_path, 1, stream_type, what_to_read)
        
        if result < 0 or stream_handle < 0:
            print(f"Error initializing photon stream: {self.spcm.get_error_string(result)}")
            return None
        
        # Read photons
        photons = []
        for i in range(max_photons):
            photon, result = self.spcm.get_photon(stream_handle)
            
            if result < 0:
                # End of file or error
                break
            
            # Create a dictionary with photon data
            photon_data = {
                'macro_time': (photon.mtime_hi << 32) | photon.mtime_lo,
                'micro_time': photon.micro_time,
                'routing_channel': photon.rout_chan,
                'flags': photon.flags
            }
            
            photons.append(photon_data)
        
        # Close the stream
        self.spcm.close_phot_stream(stream_handle)
        
        return photons
    
    def plot_decay(self, file_path, channel=0, bin_width=1):
        """Plot the fluorescence decay curve from an .sdt file"""
        photons = self.read_photons(file_path, max_photons=1000000)
        
        if not photons:
            return
        
        # Filter photons based on routing channel if specified
        if channel > 0:
            filtered_photons = [p for p in photons if p['routing_channel'] == channel]
        else:
            filtered_photons = photons
        
        # Extract micro-times
        micro_times = [p['micro_time'] for p in filtered_photons]
        
        # Bin the micro-times to create a decay curve
        max_time = 4096  # Typical for many SPC modules
        bins = np.arange(0, max_time + bin_width, bin_width)
        hist, edges = np.histogram(micro_times, bins=bins)
        
        # Plot the decay curve
        plt.figure(figsize=(10, 6))
        plt.semilogy(edges[:-1], hist, linewidth=1)
        plt.title(f"Fluorescence Decay Curve (Channel {channel})")
        plt.xlabel("Micro Time (channels)")
        plt.ylabel("Counts (log scale)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
        return hist, edges

def main():
    """Example usage of SDTReader"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Read and display Becker & Hickl .sdt files')
    parser.add_argument('sdt_file', help='Path to the .sdt file to read')
    parser.add_argument('-c', '--channel', type=int, default=0, help='Routing channel to display (0 for all)')
    parser.add_argument('-b', '--bin-width', type=int, default=1, help='Bin width for decay curve')
    parser.add_argument('-i', '--info', action='store_true', help='Show file information only')
    args = parser.parse_args()
    
    reader = SDTReader()
    
    if args.info:
        # Show file information
        info = reader.read_sdt_header(args.sdt_file)
        if info:
            print(f"SDT File Information for {args.sdt_file}:")
            print(f"  FIFO Type: {info.fifo_type}")
            print(f"  Stream Type: {info.stream_type}")
            print(f"  Macro Time Clock: {info.mt_clock}")
            print(f"  Routing Channels: {info.rout_chan}")
            print(f"  File Size: {info.stream_size} bytes")
            print(f"  Total Photons: {info.read_photons + info.invalid_phot}")
    else:
        # Plot decay curve
        reader.plot_decay(args.sdt_file, channel=args.channel, bin_width=args.bin_width)

if __name__ == "__main__":
    main() 