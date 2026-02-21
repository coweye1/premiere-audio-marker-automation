import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pymiere
import tkinter as tk
from tkinter import filedialog

# Create a file dialog to choose the audio file
def choose_audio_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select an audio file", 
        filetypes=[("Audio Files", "*.wav *.mp3 *.flac")]
    )
    return file_path

# Detect peaks with small distance and then filter the closest ones
def detect_peaks(audio_file):
    y, sr = librosa.load(audio_file, sr=None)
    envelope = np.abs(y)

    # Initial peak detection with a very small distance (high precision)
    peaks, _ = find_peaks(envelope, height=0.3, distance=sr // 2000)

    # Filter: Keep only the first peak within each 'group'
    filtered_peaks = [peaks[0]]
    min_distance_samples = sr // 15  # Custom filtering distance

    for i in range(1, len(peaks)):
        if peaks[i] - filtered_peaks[-1] > min_distance_samples:
            filtered_peaks.append(peaks[i])

    print(f"Total Peaks Detected: {len(peaks)}")
    print(f"Filtered Peaks: {len(filtered_peaks)}")

    # Plot the waveform with filtered peaks
    plt.figure(figsize=(10, 4))
    plt.plot(envelope, alpha=0.6, label='Envelope')
    plt.plot(filtered_peaks, envelope[filtered_peaks], "x", label='Filtered Peaks')
    plt.legend()
    plt.show()

    return filtered_peaks, sr

# Add markers only for filtered peaks, with a global time offset
def add_markers(peaks, sr, offset=0.0):
    try:
        project = pymiere.objects.app.project
        active_sequence = project.activeSequence

        if not active_sequence:
            print("No active sequence found. Please open a sequence in Premiere Pro.")
            return

        print(f"Adding {len(peaks)} point markers with a global offset of {offset} seconds...")
        for peak_idx in peaks:
            time_in_seconds = (peak_idx / sr) + offset  # Apply global offset
            marker = active_sequence.markers.createMarker(time_in_seconds)
            marker.name = "Precise Peak"
            marker.comments = f"Peak at {time_in_seconds:.6f}s"
            marker.setColorByIndex(1)  # Red marker for Code B

        print("Markers added successfully!")
    except Exception as e:
        print(f"Error adding markers: {e}")

# Main function
def main():
    audio_file = choose_audio_file()
    if audio_file:
        print(f"Selected audio file: {audio_file}")

        peaks, sr = detect_peaks(audio_file)

        # Define your desired global offset here (e.g., 0.5 seconds)
        global_offset = -0.0001

        # Add markers for filtered peaks with the global offset
        add_markers(peaks, sr, offset=global_offset)
    else:
        print("No audio file selected.")

if __name__ == "__main__":
    main()
