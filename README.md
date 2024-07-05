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

## Dependencies
pdfp is basically just a wrapper for other software, so there are a lot of dependencies. Tested in Linux. I cannot confirm that everything will work in Windows, but most things should.
- **Python:**
  - PySide6
  - pyperclip
  - pypdf
- **Operating System:**
  - [Bal4Web](https://www.cross-plus-a.com/bweb.htm)
  - [Balabolka](https://www.cross-plus-a.com/balabolka.htm)
  - [Briss](https://github.com/mbaeuerle/Briss-2.0)
  - pdftk
  - ocrmypdf
  - ebook-convert
  - pdftotext
  - pdftoppm

## Balabolka advice
- I recommend against using Bal4Web TTS, since it has less language options will cause the whole application to stall while it slowly works. It's mostly included just a proof of concept.
- Instead, I recommend using Balabolka itself. Here is my advised setup!
  - View > Skins (Ctrl + K) > FM 
  - View > Font and Colors (Ctrl + B) > Dark
  - Tools > Use online TTS service (Ctrl + Shift + D) > Google [1]
  - Remember to save to Windows style directory if you're on Linux (ex. Z:\home\willow\Downloads\book.wav)

## Installation and Running
### pip
[https://pypi.org/project/pdfp/](https://pypi.org/project/pdfp/)
`pip install pdfp`
### Manual
Code button >> download zip >> unzip file >> cd into directory >> `python main.py`

## Notes
srry this is hella scuffed i tried my best :3 <br>
it's my first time trying GUI dev, i hope to improve this over time and make it more stable

