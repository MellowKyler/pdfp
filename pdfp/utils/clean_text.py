import pymupdf
from PySide6.QtCore import Signal, QObject
import logging

logger = logging.getLogger("pdfp")

def clean_text(file):
    """
    Cleans up and normalizes the text of a file.
    Args:
        file (str): Fullpath to file with text to be transformed.
    Returns:
        text (str): Cleaned text.
    """

    lowerfile = file.lower()
    if lowerfile.endswith('.pdf'):
        with pymupdf.open(file) as doc:
            text = "\n".join([page.get_text() for page in doc])
    elif lowerfile.endswith('.txt'):
        with open(file, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()
    else:
        logger.warning(f"Filetype is not PDF or TXT.")
        return

    text = ' '.join(text.splitlines())
    text = text.replace('- ', '')
    text = text.strip()
    text = ' '.join(text.split())
    #text = text.encode('utf-8').decode('utf-8')
    return text