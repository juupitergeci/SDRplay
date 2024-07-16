
"""_________________________________SDRplay Graph Script__________________________________________"""


"""This code graphs the data taken by fragmentation from the Record.py script,
   it is important to indicate the number of segments in num_segments, verify the
   frequency and the sample rate, you can choose which plots you want to display with plot_type
 """


"""@Jupitergeci credits"""


import numpy as np
import matplotlib.pyplot as plt
import gc

def plot_time_and_frequency_from_file(file_path, save_path, sample_rate, center_freq, plot_type="all"):
    with open(file_path, "rb") as f:
        samples = np.frombuffer(f.read(), dtype=np.complex64)[:]

    time = np.arange(0, len(samples) / sample_rate, 1 / sample_rate)
    magnitude_db = 20 * np.log10(np.abs(samples))

    figures = []

    if plot_type == "all" or plot_type == "time":
        fig, ax1 = plt.subplots(figsize=(12, 8))
        ax1.plot(time, magnitude_db)
        ax1.set_title("Signal in Time Domain")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Amplitude (dB)")
        figures.append(fig)

    if plot_type == "all" or plot_type == "spectrogram":
        fig, ax2 = plt.subplots(figsize=(12, 8))
        ax2.specgram(samples, Fs=sample_rate, NFFT=1024, noverlap=512, Fc=center_freq)
        ax2.set_title("Spectrogram", size=15)
        ax2.set_xlabel("Time (s)", size=15)
        ax2.set_ylabel("Frequency (Hz)", size=15)
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
        ax3.set_title("Fourier Transform")
        ax3.set_xlabel("Frequency (MHz)")
        ax3.set_ylabel("Amplitude (dB)")
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

save_folder_path = "data/graphs/"

for i in range(num_segments):
    file_path = f"data/samples_{i}.bin"
    
    # Change the plot type here ("all", "time", "spectrogram", "fourier")
    plot_type = "spectrogram"
    
    save_path = f"{save_folder_path}plot_{i}_{plot_type}.png"
    figures = plot_time_and_frequency_from_file(file_path, save_path, sample_rate, center_freq, plot_type)

    # Display the figures on the screen
    for fig in figures:
        plt.show()

