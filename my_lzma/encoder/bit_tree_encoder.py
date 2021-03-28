from my_lzma.probability import Probability
from my_lzma.encoder.range_encoder import RangeEncoder


class BitTreeEncoder:
    """Реализует кодирование чисел с помощью дерева вероятностей."""

    def __init__(self, num_length: int, range_encoder: RangeEncoder):
        self.tree = [Probability() for i in range(1 << num_length)]
        self.num_length = num_length
        self.range_encoder = range_encoder

    def encode(self, num: int) -> None:
        """Кодирует num_length битное число от старших битов к младшим."""
        v = 1
        for i in range(self.num_length):
            bit = num >> (self.num_length - 1) & 1
            num <<= 1
            self.range_encoder.encode_bit(self.tree[v], bit)
            v = v * 2 + bit

    def reverse_encode(self, num: int):
        """Кодирует num_bits битное число от младших битов к старшим."""
        v = 1
        for i in range(self.num_length):
            bit = num & 1
            num >>= 1
            self.range_encoder.encode_bit(self.tree[v], bit)
            v = v * 2 + bit

    def __getitem__(self, v: int) -> Probability:
        """Возвращает вероятность, хранящуюся в вершине v дерева."""
        return self.tree[v]
