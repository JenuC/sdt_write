import os
import ctypes
from ctypes import c_short, c_int, c_long, c_float, c_double, c_char, c_char_p, c_ulong, c_ushort, c_uint, POINTER, Structure, Union, c_ubyte, c_ulonglong
from enum import IntEnum
import numpy as np
from typing import List, Optional, Tuple, Dict

# Try to find the appropriate DLL
def find_spcm_dll():
    """Attempts to find the SPCM DLL in common locations"""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "spcm64.dll"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "spcm32.dll"),
        "spcm64.dll",
        "spcm32.dll",
        r"C:\Windows\System32\spcm64.dll",
        r"C:\Windows\System32\spcm32.dll",
        #r"C:\Program Files\BH\SPCM\DLL\spcm64.dll",
        r"C:\Program Files\BH\SPCM\DLL\spcm32.dll",
        r'C:\Program Files (x86)\BH\SPCM\DLL\spcm64.dll',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError("Could not find SPCM DLL. Please ensure it's installed correctly.")

# Error codes 
class SPC_Error(IntEnum):
    OK                          = 0
    INITIALIZATION_ERROR        = -1
    ERROR_ID                    = -2
    ERROR_PAGE                  = -3
    WRONG_EEP_READ_SIZE         = -4
    WRONG_EEP_WRITE_SIZE        = -5
    EEPROM_WRITE_ERROR          = -6
    EEPROM_READ_ERROR           = -7
    EEP_CHKSUM_ERROR            = -8
    UNSUPPORTED_FUNCTION        = -9
    NOT_INIT                    = -10
    WRONG_BLOCK_SIZE            = -11  
    TIME_OUT                    = -12
    OFFSET_OUT_OF_RANGE         = -13

# Define the structures from the header file
class RateValues(Structure):
    _fields_ = [
        ("sync_rate", c_float),   # for TDC-104 Sync/CH4 rate, for DPC-230 - total photons rate in TDC1
        ("cfd_rate", c_float),    # for TDC-104 CH1 rate, for DPC-230 - total photons rate in TDC2
        ("tac_rate", c_float),    # for TDC-104 CH2 rate, for DPC-230 - not used
        ("adc_rate", c_float),    # for TDC-104 CH3 rate, for DPC-230 - not used
    ]

class RateValuesDPC(Structure):
    _fields_ = [
        ("tdc1_rate", c_float * 8),   # photons rates for all TDC1 channels
        ("tdc2_rate", c_float * 8),   # photons rates for all TDC2 channels
        ("sync_rate", c_float),
        ("tdc1_total", c_float),      # sum of rates for all TDC1 active channels
        ("tdc2_total", c_float),      # sum of rates for all TDC2 active channels
    ]

class SPCMemConfig(Structure):
    _fields_ = [
        ("max_block_no", c_long),       # total number of blocks per memory bank
        ("blocks_per_frame", c_long),   # no of blocks per frame
        ("frames_per_page", c_long),    # no of frames per page
        ("maxpage", c_long),            # max number of pages to use in a measurement
        ("block_length", c_long),       # no of 16-bits(32-bits for DPC modules) words per one block
    ]

SPCMemConfigType = POINTER(SPCMemConfig)

class SPCdata(Structure):
    _fields_ = [
        ("base_adr", c_ushort),          # base I/O address on PCI bus
        ("init", c_short),               # set to initialisation result code
        ("cfd_limit_low", c_float),
        ("cfd_limit_high", c_float),
        ("cfd_zc_level", c_float),
        ("cfd_holdoff", c_float),
        ("sync_zc_level", c_float),
        ("sync_holdoff", c_float),
        ("sync_threshold", c_float),
        ("tac_range", c_float),
        ("sync_freq_div", c_short),
        ("tac_gain", c_short),
        ("tac_offset", c_float),
        ("tac_limit_low", c_float),
        ("tac_limit_high", c_float),
        ("adc_resolution", c_short),
        ("ext_latch_delay", c_short),
        ("collect_time", c_float),
        ("display_time", c_float),
        ("repeat_time", c_float),
        ("stop_on_time", c_short),
        ("stop_on_ovfl", c_short),
        ("dither_range", c_short),
        ("count_incr", c_short),
        ("mem_bank", c_short),
        ("dead_time_comp", c_short),
        ("scan_control", c_ushort),
        ("routing_mode", c_ushort),
        ("tac_enable_hold", c_float),
        ("pci_card_no", c_short),
        ("mode", c_ushort),
        ("scan_size_x", c_ulong),
        ("scan_size_y", c_ulong),
        ("scan_rout_x", c_ulong),
        ("scan_rout_y", c_ulong),
        ("scan_flyback", c_ulong),
        ("scan_borders", c_ulong),
        ("scan_polarity", c_ushort),
        ("pixel_clock", c_ushort),
        ("line_compression", c_ushort),
        ("trigger", c_ushort),
        ("pixel_time", c_float),
        ("ext_pixclk_div", c_ulong),
        ("rate_count_time", c_float),
        ("macro_time_clk", c_short),
        ("add_select", c_short),
        ("test_eep", c_short),
        ("adc_zoom", c_short),
        ("img_size_x", c_ulong),
        ("img_size_y", c_ulong),
        ("img_rout_x", c_ulong),
        ("img_rout_y", c_ulong),
        ("xy_gain", c_short),
        ("master_clock", c_short),
        ("adc_sample_delay", c_short),
        ("detector_type", c_short),
        ("chan_enable", c_ulong),
        ("chan_slope", c_ulong),
        ("chan_spec_no", c_ulong),
        ("tdc_control", c_ulong),  # formerly x_axis_type
        ("tdc_offset", c_float * 4),
        ("reserve", c_char * 56),
    ]

class SPCModInfo(Structure):
    _fields_ = [
        ("module_type", c_short),       # module type
        ("bus_number", c_short),        # PCI bus number
        ("slot_number", c_short),       # slot number on PCI bus
        ("in_use", c_short),            # -1 used by other app, 0 not used, 1 in use
        ("init", c_short),              # set to initialisation result code
        ("base_adr", c_ushort),         # base I/O address
    ]

class SPC_Adjust_Para(Structure):
    _fields_ = [
        ("vrt1", c_short),
        ("vrt2", c_short),
        ("vrt3", c_short),
        ("dith_g", c_short),
        ("gain_1", c_float),
        ("gain_2", c_float),
        ("gain_4", c_float),
        ("gain_8", c_float),
        ("tac_r0", c_float),
        ("tac_r1", c_float),
        ("tac_r2", c_float),
        ("tac_r4", c_float),
        ("tac_r8", c_float),
        ("sync_div", c_short),
    ]

class SPC_EEP_Data(Structure):
    _fields_ = [
        ("module_type", c_char * 16),
        ("serial_no", c_char * 16),
        ("date", c_char * 16),
        ("adj_para", SPC_Adjust_Para),
    ]

class PhotInfo(Structure):
    _fields_ = [
        ("mtime_lo", c_ulong),      # macro time clocks low 32 bits
        ("mtime_hi", c_ulong),      # macro time clocks high 32 bits
        ("micro_time", c_ushort),   # micro time
        ("rout_chan", c_ushort),    # routing channel, 0-15
        ("flags", c_ushort),        # photon flags
    ]

class PhotInfo64(Structure):
    _fields_ = [
        ("mtime", c_ulonglong),     # macro time clocks 64 bits
        ("micro_time", c_ushort),   # micro time
        ("rout_chan", c_ushort),    # routing channel
        ("flags", c_ushort),        # photon flags
    ]

class PhotStreamInfo(Structure):
    _fields_ = [
        ("fifo_type", c_short),
        ("stream_type", c_short),
        ("mt_clock", c_int),
        ("rout_chan", c_short),
        ("what_to_read", c_short),
        ("no_of_files", c_short),
        ("no_of_ready_files", c_short),
        ("base_name", c_char * 264),
        ("cur_name", c_char * 264),
        ("first_no", c_short),
        ("cur_no", c_short),
        ("fifo_overruns", c_int),
        ("stream_size", c_ulonglong),
        ("cur_stream_offs", c_ulonglong),
        ("cur_file_offs", c_ulonglong),
        ("invalid_phot", c_ulonglong),
        ("read_photons", c_ulonglong),
        ("read_0_mark", c_ulonglong),
        ("read_1_mark", c_ulonglong),
        ("read_2_mark", c_ulonglong),
        ("read_3_mark", c_ulonglong),
        ("start01_offs", c_uint),
        ("no_of_buf", c_short),
        ("no_of_ready_buf", c_short),
        ("cur_buf_offs", c_uint),
        ("start_OR_mask", c_uint),
        ("start_AND_mask", c_uint),
        ("stop_OR_mask", c_uint),
        ("stop_AND_mask", c_uint),
        ("start_found", c_short),
        ("stop_reached", c_short),
        ("start_time", c_double),
        ("stop_time", c_double),
        ("curr_time", c_double),
        ("start_found_chan", c_uint),
        ("stop_found_chan", c_uint),
    ]

class SPCM:
    """Python wrapper for the SPCM DLL functions"""
    
    def __init__(self, dll_path=None):
        """Initialize the SPCM wrapper with the specified DLL path or auto-detect"""
        if dll_path is None:
            dll_path = find_spcm_dll()
        
        try:
            self.lib = ctypes.CDLL(dll_path)
            self._setup_function_prototypes()
            self.initialized = True
        except Exception as e:
            print(f"Error loading SPCM DLL: {e}")
            self.initialized = False
    
    def _setup_function_prototypes(self):
        """Set up the function prototypes for the DLL functions"""
        
        # Define function prototypes based on the header file
        
        # Initialize functions
        self.lib.SPC_init.argtypes = [c_char_p]
        self.lib.SPC_init.restype = c_short
        
        self.lib.SPC_get_init_status.argtypes = [c_short]
        self.lib.SPC_get_init_status.restype = c_short
        
        # Parameters functions
        self.lib.SPC_get_parameters.argtypes = [c_short, POINTER(SPCdata)]
        self.lib.SPC_get_parameters.restype = c_short
        
        self.lib.SPC_set_parameters.argtypes = [c_short, POINTER(SPCdata)]
        self.lib.SPC_set_parameters.restype = c_short
        
        self.lib.SPC_get_parameter.argtypes = [c_short, c_short, POINTER(c_float)]
        self.lib.SPC_get_parameter.restype = c_short
        
        self.lib.SPC_set_parameter.argtypes = [c_short, c_short, c_float]
        self.lib.SPC_set_parameter.restype = c_short
        
        # Memory configuration functions
        self.lib.SPC_configure_memory.argtypes = [c_short, c_short, c_short, POINTER(SPCMemConfig)]
        self.lib.SPC_configure_memory.restype = c_short
        
        # Measurement control functions
        self.lib.SPC_start_measurement.argtypes = [c_short]
        self.lib.SPC_start_measurement.restype = c_short
        
        self.lib.SPC_stop_measurement.argtypes = [c_short]
        self.lib.SPC_stop_measurement.restype = c_short
        
        self.lib.SPC_pause_measurement.argtypes = [c_short]
        self.lib.SPC_pause_measurement.restype = c_short
        
        self.lib.SPC_restart_measurement.argtypes = [c_short]
        self.lib.SPC_restart_measurement.restype = c_short
        
        # Data reading functions
        self.lib.SPC_read_block.argtypes = [c_short, c_long, c_long, c_long, c_short, c_short, POINTER(c_ushort)]
        self.lib.SPC_read_block.restype = c_short
        
        self.lib.SPC_read_data_block.argtypes = [c_short, c_long, c_long, c_short, c_short, c_short, POINTER(c_ushort)]
        self.lib.SPC_read_data_block.restype = c_short
        
        # Rate reading functions
        self.lib.SPC_read_rates.argtypes = [c_short, POINTER(RateValues)]
        self.lib.SPC_read_rates.restype = c_short
        
        # DPC rates reading
        self.lib.DPC_read_rates.argtypes = [c_short, POINTER(RateValuesDPC)]
        self.lib.DPC_read_rates.restype = c_short
        
        # Status functions
        self.lib.SPC_test_state.argtypes = [c_short, POINTER(c_short)]
        self.lib.SPC_test_state.restype = c_short
        
        # Module info functions
        self.lib.SPC_get_module_info.argtypes = [c_short, POINTER(SPCModInfo)]
        self.lib.SPC_get_module_info.restype = c_short
        
        # EEPROM data functions
        self.lib.SPC_get_eeprom_data.argtypes = [c_short, POINTER(SPC_EEP_Data)]
        self.lib.SPC_get_eeprom_data.restype = c_short
        
        # FIFO functions
        self.lib.SPC_read_fifo.argtypes = [c_short, POINTER(c_ulong), POINTER(c_ushort)]
        self.lib.SPC_read_fifo.restype = c_short
        
        # Error string function
        self.lib.SPC_get_error_string.argtypes = [c_short, c_char_p, c_short]
        self.lib.SPC_get_error_string.restype = c_short
        
        # Photon stream functions
        self.lib.SPC_init_phot_stream.argtypes = [c_short, c_char_p, c_short, c_short, c_short]
        self.lib.SPC_init_phot_stream.restype = c_short
        
        self.lib.SPC_close_phot_stream.argtypes = [c_short]
        self.lib.SPC_close_phot_stream.restype = c_short
        
        self.lib.SPC_get_phot_stream_info.argtypes = [c_short, POINTER(PhotStreamInfo)]
        self.lib.SPC_get_phot_stream_info.restype = c_short
        
        self.lib.SPC_get_photon.argtypes = [c_short, POINTER(PhotInfo)]
        self.lib.SPC_get_photon.restype = c_short
        
        # Save data to SDT file function
        self.lib.SPC_save_data_to_sdtfile.argtypes = [c_short, POINTER(c_ushort), c_ulong, c_char_p]
        self.lib.SPC_save_data_to_sdtfile.restype = c_short
        
        # Close function
        self.lib.SPC_close.argtypes = []
        self.lib.SPC_close.restype = c_short
    
    def init(self, ini_file=None):
        """Initialize the SPC module using the specified ini file"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        if ini_file is None:
            # Pass NULL pointer if no ini_file is specified
            return self.lib.SPC_init(None)
        else:
            return self.lib.SPC_init(ini_file.encode('utf-8'))
    
    def get_init_status(self, mod_no):
        """Get the initialization status of the specified module"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_get_init_status(mod_no)
    
    def get_error_string(self, error_id):
        """Get the error string for the specified error ID"""
        if not self.initialized:
            return "Library not initialized"
        
        error_str = ctypes.create_string_buffer(255)
        result = self.lib.SPC_get_error_string(error_id, error_str, 255)
        
        if result == 0:  # Success
            return error_str.value.decode('utf-8')
        else:
            return f"Error {result} while getting error string"
    
    def get_parameters(self, mod_no):
        """Get the parameters of the specified module"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        params = SPCdata()
        result = self.lib.SPC_get_parameters(mod_no, ctypes.byref(params))
        
        return params, result
    
    def set_parameters(self, mod_no, params):
        """Set the parameters of the specified module"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_set_parameters(mod_no, ctypes.byref(params))
    
    def get_parameter(self, mod_no, par_id):
        """Get a single parameter value"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        value = c_float()
        result = self.lib.SPC_get_parameter(mod_no, par_id, ctypes.byref(value))
        
        return value.value, result
    
    def set_parameter(self, mod_no, par_id, value):
        """Set a single parameter value"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_set_parameter(mod_no, par_id, c_float(value))
    
    def configure_memory(self, mod_no, adc_resolution, no_of_routing_bits):
        """Configure the memory for the specified module"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        mem_info = SPCMemConfig()
        result = self.lib.SPC_configure_memory(mod_no, adc_resolution, no_of_routing_bits, ctypes.byref(mem_info))
        
        return mem_info, result
    
    def start_measurement(self, mod_no):
        """Start a measurement on the specified module"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_start_measurement(mod_no)
    
    def stop_measurement(self, mod_no):
        """Stop a measurement on the specified module"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_stop_measurement(mod_no)
    
    def pause_measurement(self, mod_no):
        """Pause a measurement on the specified module"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_pause_measurement(mod_no)
    
    def restart_measurement(self, mod_no):
        """Restart a measurement on the specified module"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_restart_measurement(mod_no)
    
    def read_rates(self, mod_no):
        """Read the count rates from the specified module"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        rates = RateValues()
        result = self.lib.SPC_read_rates(mod_no, ctypes.byref(rates))
        
        return rates, result
    
    def dpc_read_rates(self, mod_no):
        """Read the count rates from the specified DPC module"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        rates = RateValuesDPC()
        result = self.lib.DPC_read_rates(mod_no, ctypes.byref(rates))
        
        return rates, result
    
    def test_state(self, mod_no):
        """Test the state of the specified module"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        state = c_short()
        result = self.lib.SPC_test_state(mod_no, ctypes.byref(state))
        
        return state.value, result
    
    def get_module_info(self, mod_no):
        """Get information about the specified module"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        mod_info = SPCModInfo()
        result = self.lib.SPC_get_module_info(mod_no, ctypes.byref(mod_info))
        
        return mod_info, result
    
    def get_eeprom_data(self, mod_no):
        """Get EEPROM data from the specified module"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        eep_data = SPC_EEP_Data()
        result = self.lib.SPC_get_eeprom_data(mod_no, ctypes.byref(eep_data))
        
        return eep_data, result
    
    def read_fifo(self, mod_no, buffer_size=1000):
        """Read data from the FIFO buffer of the specified module"""
        if not self.initialized:
            return None, None, SPC_Error.NOT_INIT
        
        count = c_ulong(0)
        data_buffer = (c_ushort * buffer_size)()
        
        result = self.lib.SPC_read_fifo(mod_no, ctypes.byref(count), data_buffer)
        
        if result == 0:  # Success
            data = np.array([data_buffer[i] for i in range(count.value)], dtype=np.uint16)
            return data, count.value, result
        else:
            return None, 0, result
    
    def init_phot_stream(self, fifo_type, spc_file, files_to_use, stream_type, what_to_read):
        """Initialize a photon stream"""
        if not self.initialized:
            return -1, SPC_Error.NOT_INIT
        
        result = self.lib.SPC_init_phot_stream(fifo_type, spc_file.encode('utf-8'), 
                                             files_to_use, stream_type, what_to_read)
        
        if result >= 0:  # Success, returns stream handle
            return result, 0
        else:
            return -1, result
    
    def close_phot_stream(self, stream_hndl):
        """Close a photon stream"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_close_phot_stream(stream_hndl)
    
    def get_phot_stream_info(self, stream_hndl):
        """Get information about a photon stream"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        stream_info = PhotStreamInfo()
        result = self.lib.SPC_get_phot_stream_info(stream_hndl, ctypes.byref(stream_info))
        
        return stream_info, result
    
    def get_photon(self, stream_hndl):
        """Get a photon from a photon stream"""
        if not self.initialized:
            return None, SPC_Error.NOT_INIT
        
        phot_info = PhotInfo()
        result = self.lib.SPC_get_photon(stream_hndl, ctypes.byref(phot_info))
        
        return phot_info, result
    
    def close(self):
        """Close the SPCM library"""
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        return self.lib.SPC_close()
    
    def simulate_module_for_sdt(self, mod_no=0):
        """
        Simulate a module presence for saving SDT files even when no physical hardware is connected.
        This works around the "SPC is not yet initialized or unknown module type" error.
        
        Parameters:
        mod_no (int): Module number to simulate (default: 0)
        
        Returns:
        int: Error code (0 for success)
        """
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        # Create a module info structure to register a fake module
        mod_info = SPCModInfo()
        mod_info.module_type = 140  # SPC-140 type (common module)
        mod_info.in_use = 1        # Mark as in use
        mod_info.init = 1          # Mark as initialized
        mod_info.bus_number = 0    # Fake bus number
        mod_info.slot_number = 0   # Fake slot number
        mod_info.base_adr = 0      # Dummy base address
        
        # Try setting up the module info directly in DLL memory
        # Note: This is a hack that may or may not work depending on the DLL
        try:
            # This approach bypasses normal init by directly manipulating internal DLL state
            # We're using ctypes to access the DLL's global module_info data
            module_info_array = (SPCModInfo * 8).in_dll(self.lib, "_module_info")
            module_info_array[mod_no] = mod_info
        except Exception as e:
            print(f"Module simulation (direct method) failed: {e}")
            # If direct manipulation fails, we'll try the standard approach
        
        # Create a minimal SPCdata structure with all required parameters
        params = SPCdata()
        params.base_adr = 0            # Dummy base address
        params.init = 1                # Pretend it's initialized
        params.mode = 0                # Normal operation mode
        params.adc_resolution = 12     # Common ADC resolution (12-bit)
        params.tac_range = 50.0        # TAC range in ns
        params.sync_freq_div = 1       # Sync frequency divider
        params.cfd_limit_low = 5.0     # CFD lower limit
        params.cfd_limit_high = 80.0   # CFD upper limit
        params.collect_time = 1.0      # Collection time in seconds
        params.repeat_time = 10.0      # Repeat time in seconds
        params.stop_on_time = 1        # Stop on collection time
        params.stop_on_ovfl = 0        # Don't stop on overflow
        params.mem_bank = 0            # Memory bank
        params.dead_time_comp = 1      # Dead time compensation
        
        # Register the simulated module with the DLL via the parameters
        result = self.lib.SPC_set_parameters(mod_no, ctypes.byref(params))
        
        # Force the module to be marked as initialized in the DLL
        # This is another approach to trick the DLL
        try:
            # Using the setmode function might help initialize some internal state
            use_flag = ctypes.c_int(0)
            self.lib.SPC_set_mode(0, 0, ctypes.byref(use_flag))
        except Exception:
            pass  # Ignore errors and continue
        
        # If we're still having issues, try to directly configure memory
        # This helps establish more module state in the DLL
        try:
            mem_info = SPCMemConfig()
            mem_info.max_block_no = 1024
            mem_info.blocks_per_frame = 1
            mem_info.frames_per_page = 1
            mem_info.maxpage = 0
            mem_info.block_length = 2**params.adc_resolution  # Block length based on ADC resolution
            
            # Attempt to configure memory for the simulated module
            self.lib.SPC_configure_memory(mod_no, params.adc_resolution, 0, ctypes.byref(mem_info))
        except Exception:
            pass  # Ignore errors and continue
        
        return result
    
    def save_data_to_sdtfile(self, mod_no, data_buffer, sdt_file):
        """
        Save measurement data to an .sdt file
        
        Parameters:
        mod_no (int): Module number
        data_buffer (numpy.ndarray): Data buffer containing the measurement data
        sdt_file (str): Path to the destination .sdt file
        
        Returns:
        int: Error code (0 for success)
        """
        if not self.initialized:
            return SPC_Error.NOT_INIT
        
        # Try to ensure the module is recognized before saving
        self.simulate_module_for_sdt(mod_no)
        
        # Convert numpy array to ctypes array if needed
        if isinstance(data_buffer, np.ndarray):
            buffer_size = data_buffer.size
            ctypes_buffer = (c_ushort * buffer_size)()
            for i in range(buffer_size):
                ctypes_buffer[i] = data_buffer[i]
        else:
            # Assume it's already a ctypes array
            ctypes_buffer = data_buffer
            buffer_size = len(data_buffer)
        
        # Calculate number of bytes (each element is 2 bytes for c_ushort)
        bytes_no = buffer_size * 2
        
        # Save data to file
        result = self.lib.SPC_save_data_to_sdtfile(mod_no, ctypes_buffer, bytes_no, sdt_file.encode('utf-8'))
        
        return result

# Example of how to use the wrapper
if __name__ == "__main__":
    try:
        # Initialize the SPCM wrapper
        spcm = SPCM()
        
        # Initialize the module
        result = spcm.init()
        if result < 0:
            print(f"Error initializing SPC module: {spcm.get_error_string(result)}")
            exit(1)
        
        # Get information about the first module (module 0)
        mod_info, result = spcm.get_module_info(0)
        if result == 0:
            print(f"Module Type: {mod_info.module_type}")
            print(f"Bus Number: {mod_info.bus_number}")
            print(f"Slot Number: {mod_info.slot_number}")
            print(f"In Use: {mod_info.in_use}")
        else:
            print(f"Error getting module info: {spcm.get_error_string(result)}")
        
        # Get the parameters for the first module
        params, result = spcm.get_parameters(0)
        if result == 0:
            print(f"Sync Rate: {params.sync_freq_div}")
            print(f"Collection Time: {params.collect_time} s")
        else:
            print(f"Error getting parameters: {spcm.get_error_string(result)}")
        
        # Start a measurement
        result = spcm.start_measurement(0)
        if result < 0:
            print(f"Error starting measurement: {spcm.get_error_string(result)}")
        
        # Read rates (example for standard SPC modules)
        rates, result = spcm.read_rates(0)
        if result == 0:
            print(f"Sync Rate: {rates.sync_rate}")
            print(f"CFD Rate: {rates.cfd_rate}")
            print(f"TAC Rate: {rates.tac_rate}")
            print(f"ADC Rate: {rates.adc_rate}")
        else:
            print(f"Error reading rates: {spcm.get_error_string(result)}")
        
        # Stop the measurement
        result = spcm.stop_measurement(0)
        if result < 0:
            print(f"Error stopping measurement: {spcm.get_error_string(result)}")
        
        # Close the library
        spcm.close()
        
    except Exception as e:
        print(f"Error: {e}") 