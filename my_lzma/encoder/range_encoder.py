from my_lzma import const
from my_lzma.probability import Probability
from my_lzma.input_output import OutputStream


class RangeEncoder:
    """Класс, реализующий кодирование диапазона."""

    def __init__(self, out_stream: OutputStream):
        self.range = 0xFFFFFFFF
        self.low = 0
        self.cache = 0
        self.cache_size = 1
        self.out_stream = out_stream

    def normalize(self):
        """Поддерживает диапазон достаточно большим."""
        carry_bit = self.low >> 32
        first_byte = self.low >> 24 & 0xFF
        if carry_bit == 0 and first_byte != 0xFF:
            self.out_stream.write(bytes([self.cache]))
            for i in range(self.cache_size - 1):
                self.out_stream.write(b'\xFF')
            self.cache = first_byte
            self.cache_size = 0
        elif carry_bit == 1:
            assert first_byte != 0xFF
            self.out_stream.write(bytes([self.cache + 1]))
            for i in range(self.cache_size - 1):
                self.out_stream.write(b'\x00')
            self.cache = first_byte
            self.cache_size = 0
        self.cache_size += 1
        self.low = self.low & 0x00FFFFFF
        self.low <<= 8
        self.range <<= 8

    def encode_bit(self, prob0: Probability, bit: int) -> None:
        """Кодирует бит. Обновляет вероятность встретить 0."""
        if self.range < const.RANGE_BORDER:
            self.normalize()
        bound = (self.range >> const.PROB_BITS) * int(prob0)
        if bit == 0:
            self.range = bound
            prob0.prob += (((1 << const.PROB_BITS) - int(prob0)) >>
                           const.MOVE_BITS)
        else:
            self.range -= bound
            self.low += bound
            prob0.prob -= int(prob0) >> const.MOVE_BITS

    def encode_direct_bits(self, num: int, bit_count: int) -> None:
        """Кодирует bits_count битов из числа num."""
        for i in range(bit_count):
            if self.range < const.RANGE_BORDER:
                self.normalize()
            self.range >>= 1
            bit = num >> (bit_count - 1) & 1
            num <<= 1
            if bit == 1:
                self.low += self.range

    def terminate(self):
        """Завершает кодирование диапазона."""
        for i in range(5):
            self.normalize()
