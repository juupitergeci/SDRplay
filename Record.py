

"""______________________________________SDRplay Recorder Script_____________________________________"""

"""This code allows you to record data with the SDRplay RSP2 device,
   it is designed for desktop computers with little power and memory
"""


"""Modify the center frequency, bandwidth, sample rate, it also allows
   recording for a specific time in integration_time, for example it allows
   recording 10 sessions of 10 seconds in number_of_segmentes and storing them in individual bin files
"""  

""" @Jupitergeci credits"""


import SoapySDR
from SoapySDR import *  # Import all functions and classes
import numpy as np
from tqdm import tqdm

def configure_device(center_freq, sample_rate, bandwidth):
    args = dict(driver="sdrplay")
    sdr = SoapySDR.Device(args)
    sdr.setFrequency(SOAPY_SDR_RX, 0, center_freq)
    sdr.setSampleRate(SOAPY_SDR_RX, 0, sample_rate)
    sdr.setBandwidth(SOAPY_SDR_RX, 0, bandwidth)
    return sdr

def take_samples(sdr, duration, save_path):
    rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
    sdr.activateStream(rx_stream)
    samples = []
    elapsed_time = 0
    sample_rate = sdr.getSampleRate(SOAPY_SDR_RX, 0)
    total_samples = int(duration * sample_rate)
    buffer_size = 1024
    with tqdm(total=total_samples, desc=f"Recording data ", unit=" samples") as pbar:
        while elapsed_time < duration:
            buffer = np.zeros(buffer_size, np.complex64)
            sr = sdr.readStream(rx_stream, [buffer], len(buffer))
    
            if sr.ret > 0:
                samples.extend(buffer[:sr.ret])
                elapsed_time += sr.ret / sample_rate
                pbar.update(sr.ret)

    sdr.deactivateStream(rx_stream)
    with open(save_path, "wb") as f:
        f.write(np.array(samples).tobytes())

# Configure center frequency, sample rate, and bandwidth
center_freq = 20.2e6  # Center frequency in Hz
sample_rate = 1e6     # Sample rate in Hz
bandwidth = 1.536e6   # Bandwidth in Hz
integration_time = 10  # Integration time in seconds
number_of_segments = 60 # Number of 10-second segments

if __name__ == "__main__":
    device = configure_device(center_freq, sample_rate, bandwidth)
    for i in range(number_of_segments):
        save_path = f"/data3/samples_{i}.bin"  # select your folder
        take_samples(device, duration=integration_time, save_path=save_path)
        
        
        
        
