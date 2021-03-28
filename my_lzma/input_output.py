from pathlib import Path


class InputStream:
    """Класс, отвечающий за входной поток."""

    def __init__(self, file: Path):
        self.file = file.open("rb")
        self.processed = 0

    def read(self, bytes_cnt: int = 1) -> bytes:
        """Читает bytes_cnt байт из входного потока."""
        read_bytes = self.file.read(bytes_cnt)
        self.processed += len(read_bytes)
        return read_bytes

    def __del__(self):
        self.file.close()


class OutputStream:
    """Класс, отвечающий за выходной поток."""

    def __init__(self, file: Path):
        self.file = file.open("wb")
        self.processed = 0

    def write(self, b: bytes) -> None:
        """Помещает байтовую строку b в выходной поток."""
        self.file.write(b)
        self.processed += len(b)

    def __del__(self):
        self.file.close()
