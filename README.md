<img align="left" width="100" height="100" src="https://raw.githubusercontent.com/MellowKyler/pdfp/main/pdfp/images/logo.ico" alt="icon">

# pdfp
PDF Processor - a GUI for some common PDF operations.

![pdfp](https://raw.githubusercontent.com/MellowKyler/pdfp/main/docs/demo.png)

## Features
- Converts EPUBs to PDFs
- Turns PDF pages into PNGs
- Optical character recognition
- Crops PDF dimensions
- Removes pages and keeps specified pages
- Copies contents without line breaks or trailing em-dashes
- Converts text to speech
- Drag, drop, and convert multiple files at a time

## Pre-Installation
- Download [Briss](https://github.com/mbaeuerle/Briss-2.0)
  - Specify the location of the jar file in pdfp's settings.
- You might need to install [ocrmypdf's requirements](https://github.com/ocrmypdf/OCRmyPDF?tab=readme-ov-file#requirements) if you don't have them already.

## Installation and Running

### Install with [PyPI](https://pypi.org/project/pdfp/)

```bash
$ pip install pdfp
$ pdfp
```

Or install from git (if I haven't published an update):

```bash
$ pip install git+https://github.com/MellowKyler/pdfp.git
$ pdfp
```

### Run from source

1. Have Python version 3.10-3.13 installed, and [poetry](https://python-poetry.org/)
2. Download the source code
3. Install required Python modules with `poetry install`
4. Run the program with `poetry run pdfp`

## Notes
Tested in Linux. I cannot confirm that everything will work in Windows, but most things should.
