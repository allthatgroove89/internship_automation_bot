# Simple App Automation

A Python application for automating simple applications like Notepad through window manipulation and keyboard shortcuts.

## Project Structure

```
├── main.py              # Main entry point
├── automation.py        # Core automation class
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the automation script:
```bash
python main.py
```

## Features

- Launch applications
- Focus and maximize windows
- Window positioning
- Screenshot capture (with OCR placeholder)
- Process monitoring

## Dependencies

- `psutil`: Process and system utilities
- `pyautogui`: GUI automation
- `pygetwindow`: Window management

## Example

The script will automatically:
1. Launch Notepad
2. Focus the Notepad window
3. Maximize the window
4. Position it on the primary monitor

