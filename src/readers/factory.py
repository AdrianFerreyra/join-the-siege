from src.readers.base import FileReader
from src.readers.images import ImageReader
from src.readers.pdf import PDFReader


class ExtensionNotAllowedError(Exception):
    pass


READERS: list[FileReader] = [PDFReader(), ImageReader()]


def get_reader(file_extension: str) -> FileReader:
    for reader in READERS:
        if reader.supports_extension(file_extension):
            return reader

    raise ExtensionNotAllowedError("Extension not found", 400)
