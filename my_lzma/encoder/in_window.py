from my_lzma.input_output import InputStream
from typing import Tuple, Optional
from collections import deque
from my_lzma import const


class InWindow:
    # TODO документация

    def __init__(self, dict_size: int, in_stream: InputStream):
        self.prev_buf = deque()
        self.next_buf = deque()
        self.max_prev_size = dict_size
        self.max_next_size = min(dict_size, const.MAX_MATCH_LEN)
        self.in_stream = in_stream
        self.num_encoded = 0
        while len(self.next_buf) < self.max_next_size:
            if not self.expand_next_buf():
                break

    def expand_next_buf(self) -> bool:
        """Пытается считать очередной символ в next_buf.
        Если удалось считать, то возвращает True, иначе False.
        """
        byte = self.in_stream.read()
        if byte == b'':
            return False
        self.next_buf.append(byte)
        return True

    def move_window(self) -> None:
        """Перекладывает очередной символ из не закодированной части в
        закодированную.
        """
        self.prev_buf.appendleft(self.next_buf[0])
        self.next_buf.popleft()
        if len(self.prev_buf) > self.max_prev_size:
            self.prev_buf.pop()
        self.expand_next_buf()
        self.num_encoded += 1

    def is_finished(self) -> bool:
        """Проверяет, что весь файл был закодирован."""
        return len(self.next_buf) == 0

    def find_match(self) -> Optional[Tuple[int, int]]:
        """Находит максимальную по длине строку из словаря, совпадающую с
        префиксом незакодированной части. Возвращает строку в виде пары
        (match_length, distance). Если не находит совпадение, возвращает None.
        """
        ans_distance = 0
        ans_length = 0
        for distance in range(len(self.prev_buf)):
            length = self.find_match_from(distance)
            if length > ans_length:
                ans_distance = distance
                ans_length = length
        if ans_length < const.MIN_MATCH_LEN:
            return None
        else:
            return ans_length, ans_distance

    def find_match_from(self, distance: int) -> int:
        """Находит максимальную длину совпадения префикса next_buf и
        подстроки prev_buf, начинающейся с точки distance.
        """
        length = 0
        while distance - length >= 0 and length < len(self.next_buf) \
                and self.prev_buf[distance - length] == self.next_buf[length]:
            length += 1
        return length

    def __getitem__(self, item: int):
        """Возвращает элемент с индексом item из prev_buf."""
        return self.prev_buf[item]
