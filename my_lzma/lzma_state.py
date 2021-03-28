class LZMAState:
    """Описывает состояние LZMA кодера/декодера в виде числа от 0 до 11."""

    def __init__(self, val: int = 0):
        self.val = val

    def update_literal(self):
        """Обновляет состояние, если встретился literal."""
        if self.val < 4:
            self.val = 0
        elif self.val < 10:
            self.val -= 3
        else:
            self.val -= 6

    def update_simple_match(self):
        """Обновляет состояние, если встретился simple match."""
        if self.val < 7:
            self.val = 7
        else:
            self.val = 10

    def update_short_rep(self):
        """Обновляет состояние, если встретился short rep match."""
        if self.val < 7:
            self.val = 9
        else:
            self.val = 11

    def update_rep(self):
        """Обновляет состояние, если встретился rep match."""
        if self.val < 7:
            self.val = 8
        else:
            self.val = 11

    def __int__(self):
        return self.val
