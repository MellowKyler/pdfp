import logging
from pathlib import Path
from typing import cast

import pymupdf

logger = logging.getLogger("pdfp")


def clean_text(file: str) -> str | None:
    path = Path(file)

    if path.suffix.lower() == ".pdf":
        with pymupdf.open(file) as doc:
            all_text = [cast("str", page.get_text()) for page in doc]  # pyright: ignore[reportUnknownMemberType]
            text = "\n".join(all_text)
    elif path.suffix.lower() == ".txt":
        text = path.read_text(encoding="utf-8")
    else:
        logger.warning("Filetype is not PDF or TXT.")
        return None

    text = " ".join(text.splitlines())
    text = text.replace("- ", "")
    text = text.strip()
    return " ".join(text.split())
