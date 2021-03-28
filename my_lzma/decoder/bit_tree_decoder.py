from my_lzma.probability import Probability
from my_lzma.decoder.range_decoder import RangeDecoder


class BitTreeDecoder:
    """Реализует декодирование чисел с помощью дерева вероятностей."""

    def __init__(self, num_length: int, range_decoder: RangeDecoder):
        self.tree = [Probability() for i in range(1 << num_length)]
        self.num_length = num_length
        self.range_decoder = range_decoder

    def decode(self) -> int:
        """Декодирует num_length битное число от старших битов к младшим."""
        v = 1
        ans = 0
        for i in range(self.num_length):
            bit = self.range_decoder.decode_bit(self.tree[v])
            v = v * 2 + bit
            ans = (ans << 1) | bit
        return ans

    def reverse_decode(self) -> int:
        """Декодирует num_bits битное число от младших битов к старшим."""
        v = 1
        ans = 0
        for i in range(self.num_length):
            bit = self.range_decoder.decode_bit(self.tree[v])
            v = v * 2 + bit
            ans |= bit << i
        return ans

    def __getitem__(self, v: int) -> Probability:
        """Возвращает вероятность, хранящуюся в вершине v дерева."""
        return self.tree[v]

    # def __setitem__(self, v: int, prob: Probability):
    #     """Устанавливает вероятность prob в вершину дерева v."""
    #     self.tree[v] = prob
