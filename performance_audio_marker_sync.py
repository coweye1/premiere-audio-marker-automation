import librosa
import numpy as np
import pymiere
import tkinter as tk
from tkinter import filedialog
from scipy.signal import find_peaks

# Define your desired global offset here (e.g., 0.0001 seconds to delay markers by 1 frame)
global_offset = -0.00002  

# File dialog for choosing audio files
def choose_audio_file(prompt):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title=prompt,
        filetypes=[("Audio Files", "*.wav *.mp3 *.flac")]
    )
    return file_path

# Detect peaks with improved early detection
def detect_peaks(audio_file):
    y, sr = librosa.load(audio_file, sr=None)
    envelope = np.abs(y)
    derivative = np.diff(envelope)
    derivative = np.append(derivative, 0)  # Match original length

    # 기존보다 좀 더 민감한 필터링 (볼륨 상승 시작 지점 탐지)
    peak_indices, _ = find_peaks(derivative, height=np.max(derivative) * 0.15, distance=sr // 500)
    
    # ** 첫 변곡점만 선택하도록 개선 **
    filtered_peaks = []
    last_peak = None
    peak_window = int(0.04 * sr)  # 40ms

    for peak in peak_indices:
        if last_peak is None or (peak - last_peak) > peak_window:
            filtered_peaks.append(peak)
            last_peak = peak

    print(f"Detected {len(filtered_peaks)} refined peaks in {audio_file}")
    return np.array(filtered_peaks), sr

# Add markers in Premiere Pro with global offset
def add_markers(peaks, sr):
    try:
        project = pymiere.objects.app.project
        active_sequence = project.activeSequence
        if not active_sequence:
            print("No active sequence found. Please open a sequence in Premiere Pro.")
            return

        print(f"Adding {len(peaks)} refined markers with global offset {global_offset} seconds...")

        for peak in peaks:
            time_in_seconds = (peak / sr) + global_offset  # Apply global offset
            marker = active_sequence.markers.createMarker(time_in_seconds)
            marker.name = "Refined Peak"
            marker.comments = f"Detected at {time_in_seconds:.6f}s (Offset applied)"
            marker.setColorByIndex(3)  # Orange marker

        print("Refined markers added successfully with offset!")
    except Exception as e:
        print(f"Error adding markers: {e}")
    finally:
        project = None
        active_sequence = None

# Main function
def main():
    step_file = choose_audio_file("Select the step audio file")

    if step_file:
        refined_peaks, sr = detect_peaks(step_file)  # Improved peak detection
        add_markers(refined_peaks, sr)  # Add refined markers with offset
    else:
        print("Audio file must be selected.")

if __name__ == "__main__":
    main()
