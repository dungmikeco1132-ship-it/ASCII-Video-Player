# 🎬 ASCII Video Player v5 — Ultimate Edition (Spanish Fork)

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![NumPy](https://img.shields.io/badge/NumPy-1.20+-blue.svg)
![Status](https://img.shields.io/badge/Version-Spanish%20Fork-orange.svg)

A text-based (CLI) video player that renders every video frame into high-quality ASCII art directly in your terminal. This version is an **enhanced and translated fork** based on the original work by @stepanussaruran.

---

## ✨ Features of this Fork

- **🖥️ Dynamic Auto-Fit**: The image automatically scales to both terminal width **and height** in real-time, maintaining the correct aspect ratio.
- **🌈 Color/B&W Mode**: Support for 24-bit ANSI color for a premium visual experience or black and white mode for maximum performance.
- **🕹️ Enhanced Interactive Mode**: Guided setup on startup for color, looping, auto-fit, and frame skipping.
- **⚡ Background Decoding**: Uses threading for smooth playback without stuttering.
- **🔄 Loop Mode**: Option to repeat the video automatically.
- **📍 Pinned Status Bar**: The progress bar stays at the bottom of the window to prevent flickering and visual clutter.
- **🌍 Spanish Translation**: Interface, messages, and help are fully translated into Spanish for native speakers.

---

## 🛠️ System Requirements

Before running, ensure you have the necessary libraries installed:

```bash
pip install opencv-python numpy
```
*(On Windows, if you encounter version issues, try: `python -m pip install opencv-python numpy`)*

---

## 🚀 How to Use

### 1. Interactive Mode (Recommended)
Simply run the script and follow the on-screen instructions:
```bash
python ASCII_v5_ultimate_ES.py
```

### 2. Command-Line Mode
For power users who prefer using flags:
```bash
# Play with color and auto-fit
python ASCII_v5_ultimate_ES.py my_video.mp4 --color

# Disable auto-fit and set a fixed width of 150
python ASCII_v5_ultimate_ES.py my_video.mp4 --no-fit --width 150

# Info mode (view video details only)
python ASCII_v5_ultimate_ES.py my_video.mp4 --info
```

---

## ⌨️ Controls
- **Ctrl + C**: Gracefully stops playback and restores the terminal cursor.

## 💡 Credits
- **Original Creator**: [stepanussaruran](https://github.com/stepanussaruran)
- **Translation and Enhancements**: Nicolas Romero (coralgamer) & Gemini AI.

---
*Para la versión en español, consulta [README_ES.md](README_ES.md).*
