<img align="left" width="100" height="100" src="https://raw.githubusercontent.com/MellowKyler/pdfp/main/pdfp/images/logo.ico" alt="icon">

# pdfp
PDF Processor - a GUI for some common PDF operations.

![pdfp](https://raw.githubusercontent.com/MellowKyler/pdfp/main/docs/demo.png)

## Features
- Converts files to PDF
- Converts PDF pages into PNGs
- Optical character recognition
- Crops PDF dimensions
- Removes pages and keeps specified pages
- Copies contents without line breaks or trailing hypens
- Converts text to speech
- Drag, drop, and convert multiple files at a time

## Pre-Installation
- Download [Briss](https://github.com/mbaeuerle/Briss-2.0)
  - Requires [Java](https://www.oracle.com/java/technologies/downloads) 8 or above
- Install [Tesseract and Ghostscript](https://ocrmypdf.readthedocs.io/en/latest/installation.html#installing-on-windows) (requirements for ocrmypdf)

### Optional - Balabolka TTS
Download [Balabolka](https://www.cross-plus-a.com/balabolka.htm) as an alternative to gTTS
- This is my preferred free Text-to-Speech method. gTTS gets rate limited very quickly.
- If you are not on Windows, Balabolka runs through [Wine](https://www.winehq.org/). You can configure a Wine prefix if desired.
- Ctrl+K for Skin options. "FM" is my preference.
- Ctrl+Shift+D for Use Online TTS Service. "Google \[1\] - English (US)" is my preference.

## Installation and Running

### Install with [pip](https://pypi.org/project/pdfp/)

```bash
$ pip install pdfp
$ pdfp
```

Or install from git (if I haven't published an update to PyPI):

```bash
$ pip install git+https://github.com/DrearyWillow/pdfp.git
$ pdfp
```

## Notes
Tested in Linux and Windows. Mac should work as well, but I don't own one so I can't confirm compatibility.