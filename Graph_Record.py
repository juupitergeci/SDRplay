
"""_________________________________SDRplay Graph Script__________________________________________"""


"""This code graphs the data taken by fragmentation from the Record.py script,
   it is important to indicate the number of segments in num_segments, verify the
   frequency and the sample rate, you can choose which plots you want to display with plot_type
 """


"""@Jupitergeci credits"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import gc
from datetime import datetime, timedelta

def seconds_to_utc(seconds, start_time):
    """Convert seconds from start time to UTC time."""
    return [start_time + timedelta(seconds=s) for s in seconds]

def plot_time_and_frequency_from_file(file_path, save_path, sample_rate, center_freq, start_time_utc, plot_type="all"):
    with open(file_path, "rb") as f:
        samples = np.frombuffer(f.read(), dtype=np.complex64)[:]

    time = np.arange(0, len(samples) / sample_rate, 1 / sample_rate)
    magnitude_db = 20 * np.log10(np.abs(samples))

    figures = []

    if plot_type == "all" or plot_type == "time":
        fig, ax1 = plt.subplots(figsize=(12, 8))
        ax1.plot(time, magnitude_db)
        ax1.set_title("Signal in Time Domain", fontsize=16)
        ax1.set_xlabel("Time (s)", fontsize=16)
        ax1.set_ylabel("Amplitude (dB)", fontsize=16)
        ax1.tick_params(axis='both', which='major', labelsize=12)
        figures.append(fig)

    if plot_type == "all" or plot_type == "spectrogram":
        fig, ax2 = plt.subplots(figsize=(12, 8))
        Pxx, freqs, bins, im = ax2.specgram(samples, Fs=sample_rate, NFFT=1024, noverlap=512, Fc=center_freq, scale='dB',cmap="jet")
        
        # Add colorbar with adjusted label and tick sizes
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_label('Intensity (dB)', fontsize=16, rotation=270, labelpad=15)
        cbar.ax.tick_params(labelsize=12)
        
        # Convert the x-axis from seconds to UTC
        time_bins = seconds_to_utc(bins, start_time_utc)
        ax2.set_xticks(np.linspace(bins[0], bins[-1], num=10))  # Set the x-ticks to cover the range
        ax2.set_xticklabels([dt.strftime('%H:%M:%S') for dt in seconds_to_utc(np.linspace(bins[0], bins[-1], num=10), start_time_utc)], fontsize=12)
        
        ax2.set_title("Spectrogram", fontsize=16)
        ax2.set_xlabel("Time (UTC)", fontsize=16)
        ax2.set_ylabel("Frequency (Hz)", fontsize=16)
        ax2.tick_params(axis='both', which='major', labelsize=12)
        figures.append(fig)

    if plot_type == "all" or plot_type == "fourier":
        fft_result = np.fft.fft(samples)
        frequencies = np.fft.fftfreq(len(samples), d=1/sample_rate)
        fft_result_shift = np.fft.fftshift(fft_result)
        frequencies_shift = np.fft.fftshift(frequencies)
        adjusted_frequencies = frequencies_shift + center_freq
        fft_result_db = 20 * np.log10(np.abs(fft_result_shift))

        fig, ax3 = plt.subplots(figsize=(12, 8))
        ax3.plot(adjusted_frequencies / 1e6, fft_result_db)
        ax3.set_title("Fourier Transform", fontsize=15)
        ax3.set_xlabel("Frequency (MHz)", fontsize=15)
        ax3.set_ylabel("Amplitude (dB)", fontsize=15)
        ax3.tick_params(axis='both', which='major', labelsize=12)
        figures.append(fig)

    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path)
        plt.close('all')  # Close all figures to free memory
    else:
        plt.show()

    # Force garbage collection
    del samples
    gc.collect()

    return figures

# Parameters
sample_rate = 1e6       # Sample rate in Hz
center_freq = 20.2e6    # Center frequency in Hz
num_segments = 100      # Number of 10-second segments
segment_duration = 10   # Duration of each segment in seconds
interval_between_segments = 1  # Interval between segments in seconds

start_time_utc = datetime(2024, 7, 21, 16, 30, 11)  # Initial start time in UTC

save_folder_path = "/graph/"

for i in range(num_segments):
    file_path = f"/datos/samples_{i}.bin"
    
    
    # Adjust start time for the current segment
    segment_start_time = start_time_utc + timedelta(seconds=i * (segment_duration + interval_between_segments))
    
    # Change the plot type here ("all", "time", "spectrogram", "fourier")
    plot_type = "spectrogram"
    
    save_path = f"{save_folder_path}plot_{i}_{plot_type}.png"
    figures = plot_time_and_frequency_from_file(file_path, save_path, sample_rate, center_freq, segment_start_time, plot_type)

    # Display the figures on the screen
    for fig in figures:
        plt.show()


