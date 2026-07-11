# Exam-Time PC Lockdown System

A Python-based system that locks a PC into a controlled "exam mode" to prevent malpractice during computer-based tests — blocking distracting apps, locking key folders, and running a fullscreen countdown that can't be closed until time is up.

## Features

- **Fullscreen lockdown screen** — always-on-top, cannot be minimized or closed while the exam is running
- **Live countdown timer** — large on-screen timer that changes color as time runs low (green → orange → red in the final 30 seconds)
- **Automatic app blocking** — continuously monitors running processes and force-closes distracting apps (Chrome, Firefox, Edge, Discord, Spotify, Steam, VLC, YouTube, Netflix, and more)
- **Folder locking** — automatically renames/locks the Downloads, Videos, and Music folders for the exam duration, and restores them automatically once the exam ends
- **Activity logging** — every locked folder, blocked app, and exam start/end event is timestamped and written to `logs/exam_log.txt`
- **Clean session lifecycle** — one command starts the exam (lock folders, start monitoring, go fullscreen); ending the timer automatically reverses everything

## Tech Stack

- **Python 3**
- **Tkinter** — fullscreen GUI and live countdown display
- **psutil** — real-time process monitoring and termination
- **threading** — runs the app monitor in the background without freezing the UI

## How It Works

1. Run the script and choose **Start Exam-Mode**
2. Enter the exam duration in minutes
3. The app immediately:
   - Locks the Downloads, Videos, and Music folders
   - Starts a background thread that scans and closes any blocked app every second
   - Launches a fullscreen, always-on-top countdown window that can't be closed
4. When the timer hits zero, the fullscreen window closes automatically, monitoring stops, and all locked folders are restored
5. A full log of the session (what was blocked, when folders were locked/unlocked) is saved to `logs/exam_log.txt`

## Installation

```bash
pip install psutil
```
(Tkinter usually ships with Python by default; if missing, install via `pip install tk`)

## Usage

```bash
python exam_lockdown_simple.py
```

## Disclaimer

This project was built as a learning exercise in process monitoring, file system control, and GUI development in Python. It is intended for personal/educational use in a controlled environment — not for deployment on shared or production systems without further safety review.
