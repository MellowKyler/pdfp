<img align="left" width="100" height="100" src="https://raw.githubusercontent.com/MellowKyler/pdfp/main/logo.ico" alt="icon">

# pdfp
PDF Processor - a GUI for some common PDF operations.

![pdfp](https://github.com/MellowKyler/pdfp/assets/108599378/cadedac6-8246-4d87-9121-732d6234db19)

## Operations
- Converts EPUBs to PDFs
- Turns PDF pages into PNGs
- Optical character recognition
- Crops PDF dimensions
- Removes pages and keeps specified pages
- Copies contents without line breaks or trailing em-dashes
- Converts text to speech

## Dependencies
pdfp is basically just a wrapper for other software, so there are a lot of dependencies. Tested in Linux. I cannot confirm that everything will work in Windows, but most things should.
- **Python:**
  - PySide6
  - pyperclip
  - PyPDF2
- **Operating System:**
  - [Bal4Web](https://www.cross-plus-a.com/bweb.htm)
  - [Balabolka](https://www.cross-plus-a.com/balabolka.htm)
  - [Briss (2.0 preferable)](https://github.com/mbaeuerle/Briss-2.0)
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
  - Remember to save to windows style directory if you're on Linux (ex. Z:\home\willow\Downloads\book.wav)
