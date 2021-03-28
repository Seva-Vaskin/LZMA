from my_lzma import const


class Probability:
    """Хранит вероятность в формате целого числа от 0 до 2^11."""

    def __init__(self, prob: int = const.DEFAULT_PROB):
        self.prob = prob

    def __int__(self):
        return self.prob
