
"""______________________________________SDRplay Recorder Script_____________________________________"""

"""This code allows you to record data with the SDRplay RSP2 device,
   it is designed for desktop computers with big power and memory
"""


"""Modify the center frequency, bandwidth, sample rate, it also allows
   recording for a specific time in integration_time
"""  

""" @Jupitergeci credits"""




#!/usr/bin/env python3
import SoapySDR
from SoapySDR import *
import numpy as np
import matplotlib.pyplot as plt
import gc

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
    buffer_size = 1024

    while elapsed_time < duration:
        buffer = np.zeros(buffer_size, np.complex64)
        sr = sdr.readStream(rx_stream, [buffer], len(buffer))
        if sr.ret > 0:
            samples.extend(buffer[:sr.ret])
            elapsed_time += sr.ret / sample_rate

    sdr.deactivateStream(rx_stream)

    with open(save_path, "wb") as f:
        f.write(np.array(samples).tobytes())

def plot_time_and_frequency(file_path, sample_rate, center_freq):
    with open(file_path, "rb") as f:
        samples = np.frombuffer(f.read(), dtype=np.complex64)[:]

    plt.figure(figsize=(12, 8))

    # Time domain plot
    plt.subplot(3, 1, 1)
    time = np.arange(0, len(samples) / sample_rate, 1 / sample_rate)
    plt.plot(time, samples)
    plt.title("Signal in Time Domain")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")

    # Spectrogram plot
    plt.subplot(3, 1, 2)
    plt.specgram(samples, Fs=sample_rate, NFFT=1024, noverlap=512, Fc=center_freq)
    plt.title("Spectrogram")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")

    # Fourier Transform plot
    fft_result = np.fft.fft(samples)
    frequencies = np.fft.fftfreq(len(samples), d=1/sample_rate)
    fft_result_shift = np.fft.fftshift(fft_result)
    frequencies_shift = np.fft.fftshift(frequencies)
    adjusted_frequencies = frequencies_shift + center_freq
    fft_result_db = 20 * np.log10(np.abs(fft_result_shift))

    plt.subplot(3, 1, 3)
    plt.plot(adjusted_frequencies / 1e6, fft_result_db)
    plt.title("Fourier Transform")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Amplitude (dB)")

    plt.tight_layout()
    plt.grid(alpha=0.4)
    plt.show()

if __name__ == "__main__":
    center_freq = 107.4e6  # Center frequency in Hz
    sample_rate = 1e6     # Sample rate in Hz
    bandwidth = 1.536e6   # Bandwidth in Hz
    integration_time = 10

    device = configure_device(center_freq, sample_rate, bandwidth)
    take_samples(device, duration=integration_time, save_path="data/samples0.bin")

    file_path = "data/samples0.bin"
    plot_time_and_frequency(file_path, sample_rate, center_freq)

