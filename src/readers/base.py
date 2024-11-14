from abc import ABC, abstractmethod


class FileReader(ABC):
    _SUPPORTED_FILE_EXTENSIONS = []

    def supports_extension(self, file_extension):
        return file_extension in self._SUPPORTED_FILE_EXTENSIONS

    @abstractmethod
    def read(self, file_bytes):
        pass
