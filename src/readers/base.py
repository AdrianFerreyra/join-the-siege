from abc import ABC, abstractmethod


class FileReader(ABC):
    _SUPPORTED_FILE_EXTENSIONS = []

    def supports_extension(self, file_extension: str):
        return file_extension.upper() in self._SUPPORTED_FILE_EXTENSIONS

    @abstractmethod
    def read(self, file_bytes):
        pass
