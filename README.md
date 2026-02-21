# Premiere Audio Marker Automation

Python-based automation scripts for detecting timing peaks in audio files and generating timeline markers in Adobe Premiere Pro.

## Overview

This project provides two synchronization modes for automated marker generation:

### Reference-Based Synchronization
Detects peak events from externally generated reference audio and creates aligned markers in an active Premiere Pro sequence.

### Performance-Based Synchronization
Detects transient events from performance-derived audio and generates timeline markers aligned to actual performance timing.

## Features

- Automated peak detection using signal processing
- Configurable global timing offset
- Premiere Pro integration via pymiere
- Workflow optimization for repetitive marker placement

## Technologies

- Python
- librosa
- numpy
- scipy
- pymiere
- tkinter
