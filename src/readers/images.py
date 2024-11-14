import io

from PIL import Image
import pytesseract
from src.readers.base import FileReader


class ImageReader(FileReader):
    _SUPPORTED_FILE_EXTENSIONS = [
        "PNG",
        "JPEG",
        "TIFF",
        "GIF",
        "WebP",
        "BMP",
        "PNM",
        # From Tesseract Docs (https://tesseract-ocr.github.io/tessdoc/InputFormats.html)
    ]

    def read(self, file_bytes):
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text
