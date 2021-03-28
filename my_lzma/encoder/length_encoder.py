from my_lzma.encoder.base_encoder import BaseEncoder
from my_lzma.probability import Probability
from my_lzma.encoder.bit_tree_encoder import BitTreeEncoder
from my_lzma import const


class LengthEncoder(BaseEncoder):
    """Реализует кодирование длины совпадения."""

    def __init__(self, *args):
        super().__init__(*args)
        self.low_coder = [BitTreeEncoder(3, self.range_encoder) for i in
                          range(1 << self.pb)]
        self.mid_coder = [BitTreeEncoder(3, self.range_encoder) for i in
                          range(1 << self.pb)]
        self.high_coder = BitTreeEncoder(8, self.range_encoder)
        self.choice1 = Probability()
        self.choice2 = Probability()

    def encode(self, length: int, pb_context: int) -> None:
        """Кодирует длину совпадения."""
        length -= const.MIN_MATCH_LEN
        if length < 8:
            self.range_encoder.encode_bit(self.choice1, 0)
            self.low_coder[pb_context].encode(length)
        else:
            self.range_encoder.encode_bit(self.choice1, 1)
            if length < 16:
                self.range_encoder.encode_bit(self.choice2, 0)
                self.mid_coder[pb_context].encode(length - 8)
            else:
                self.range_encoder.encode_bit(self.choice2, 1)
                self.high_coder.encode(length - 16)
