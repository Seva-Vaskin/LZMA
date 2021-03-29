from my_lzma.input_output import OutputStream
from collections import deque


class OutWindow:
    """Работает с выходным потоком, запоминает
    последние выведенные size бит.
    """

    def __init__(self, size: int, out_stream: OutputStream):
        self.buf = deque()
        self.max_size = size
        self.out_stream = out_stream
        self.num_decoded = 0

    def put_byte(self, b: bytes) -> None:
        """Помещает байт b в выходной поток."""
        self.buf.appendleft(b)
        if len(self.buf) > self.max_size:
            self.buf.pop()
        self.out_stream.write(b)
        self.num_decoded += 1

    def __getitem__(self, item: int) -> bytes:
        """Возвращает item-ный c конца элемент из выходного потока."""
        if not 1 <= item <= len(self.buf):
            raise IndexError
        return self.buf[item - 1]

    def copy_match(self, dist: int, match_length: int) -> None:
        """Копирует строку длины match_length, первый символ которой имеет
        номер dist в буфере, в выходной поток.
        """
        for i in range(match_length):
            b = self[dist]
            self.put_byte(b)
