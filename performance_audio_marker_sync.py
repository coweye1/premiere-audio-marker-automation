"""
Performance-Based Audio Marker Synchronization Tool

Detects transient peaks from performance-derived audio
and generates aligned timeline markers in an active
Adobe Premiere Pro sequence.

Designed for performance timing alignment and workflow automation.
"""

import librosa
import numpy as np
import pymiere
import tkinter as tk
from tkinter import filedialog
from scipy.signal import find_peaks


# Adjustable global timing offset (in seconds)
GLOBAL_OFFSET = -0.00002


def choose_audio_file(prompt: str) -> str:
    """
    Open file dialog for selecting an audio file.

    Parameters:
        prompt (str): Dialog window title

    Returns:
        str: Selected file path
    """
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title=prompt,
        filetypes=[("Audio Files", "*.wav *.mp3 *.flac")]
    )


def detect_performance_peaks(audio_file: str):
    """
    Detect transient peaks from performance-derived audio.

    Parameters:
        audio_file (str): Path to input audio file

    Returns:
        np.ndarray: Array of detected peak sample indices
        int: Sample rate
    """
    y, sr = librosa.load(audio_file, sr=None)

    envelope = np.abs(y)
    derivative = np.diff(envelope)
    derivative = np.append(derivative, 0)

    peak_indices, _ = find_peaks(
        derivative,
        height=np.max(derivative) * 0.2,
        distance=sr // 400
    )

    filtered_peaks = []
    last_peak = None
    peak_window = int(0.03 * sr)

    for peak in peak_indices:
        if last_peak is None or (peak - last_peak) > peak_window:
            filtered_peaks.append(peak)
            last_peak = peak

    print(f"[INFO] Detected {len(filtered_peaks)} performance peaks.")
    return np.array(filtered_peaks), sr


def add_markers_to_premiere(peaks: np.ndarray, sr: int):
    """
    Add timeline markers to active Premiere Pro sequence.

    Parameters:
        peaks (np.ndarray): Detected peak sample indices
        sr (int): Sample rate
    """
    try:
        project = pymiere.objects.app.project
        sequence = project.activeSequence

        if not sequence:
            print("[ERROR] No active Premiere Pro sequence found.")
            return

        print(f"[INFO] Adding {len(peaks)} performance markers...")

        for peak in peaks:
            time_sec = (peak / sr) + GLOBAL_OFFSET
            marker = sequence.markers.createMarker(time_sec)
            marker.name = "Performance Peak"
            marker.comments = f"Detected at {time_sec:.6f}s"
            marker.setColorByIndex(2)  # Different color from reference mode

        print("[SUCCESS] Performance markers added successfully.")

    except Exception as e:
        print(f"[ERROR] {e}")


def main():
    audio_file = choose_audio_file("Select performance audio file")

    if not audio_file:
        print("[WARNING] No file selected.")
        return

    peaks, sr = detect_performance_peaks(audio_file)
    add_markers_to_premiere(peaks, sr)


if __name__ == "__main__":
    main()
