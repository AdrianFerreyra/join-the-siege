import io

import PyPDF2

from src.readers.base import FileReader


class PDFReader(FileReader):
    _SUPPORTED_FILE_EXTENSIONS = ["PDF"]

    def read(self, file_bytes):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()
