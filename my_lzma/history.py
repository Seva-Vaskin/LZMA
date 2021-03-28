from collections import deque
from my_lzma import const


class History:
    """Хранит историю отступов назад за последние 4 шага."""

    def __init__(self):
        self.rep = deque(0 for i in range(const.HISTORY_LEN))

    def add(self, distance: int):
        """Добавляет отступ в историю."""
        self.rep.appendleft(distance)
        self.rep.pop()

    def __getitem__(self, item):
        """Возвращает item-ный элемент из истории."""
        return self.rep[item]
