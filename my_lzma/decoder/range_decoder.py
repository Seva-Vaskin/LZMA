from my_lzma.input_output import InputStream
from my_lzma import const
from my_lzma.probability import Probability


class RangeDecoder:
    """Класс реализующий декодирование диапазона."""

    def __init__(self, in_stream: InputStream):
        self.range = 0xFFFFFFFF
        self.corrupted = False
        self.in_stream = in_stream
        first_byte = in_stream.read()
        code_bytes = in_stream.read(4)
        self.code = int.from_bytes(code_bytes, byteorder='big')
        if first_byte != b'\x00' or self.code == self.range:
            self.corrupted = True

    def normalize(self):
        """Поддерживает диапазон достаточно большим."""
        if self.range < const.RANGE_BORDER:
            self.range <<= 8
            self.code <<= 8
            b = self.in_stream.read()
            self.code |= int.from_bytes(b, byteorder='big')

    def decode_bit(self, prob0: Probability) -> int:
        """Декодирует бит. Обновляет вероятность встретить 0."""
        bound = (self.range >> const.PROB_BITS) * int(prob0)
        if self.code < bound:
            bit = 0
            self.range = bound
            prob0.prob += (((1 << const.PROB_BITS) - int(prob0)) >>
                           const.MOVE_BITS)
        else:
            bit = 1
            self.range -= bound
            self.code -= bound
            prob0.prob -= int(prob0) >> const.MOVE_BITS
        self.normalize()

        return bit

    def decode_direct_bits(self, bits_count: int) -> int:
        """Декодирует bits_count битов."""
        res = 0
        for i in range(bits_count):
            self.range >>= 1
            if self.code < self.range:
                bit = 0
            else:
                bit = 1
                self.code -= self.range
            res = res << 1 | bit
            self.normalize()

        return res

    def is_finished_ok(self):
        """Проверяет корректность завершения потока."""
        return self.code == 0
