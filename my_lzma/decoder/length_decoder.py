from my_lzma.decoder.base_decoder import BaseDecoder
from my_lzma.decoder.bit_tree_decoder import BitTreeDecoder
from my_lzma.probability import Probability
from my_lzma import const


class LengthDecoder(BaseDecoder):
    """Реализует декодирование длины совпадения."""

    def __init__(self, *args):
        super().__init__(*args)
        self.low_coder = [BitTreeDecoder(3, self.range_decoder) for i in
                          range(1 << self.pb)]
        self.mid_coder = [BitTreeDecoder(3, self.range_decoder) for i in
                          range(1 << self.pb)]
        self.high_coder = BitTreeDecoder(8, self.range_decoder)
        self.choice1 = Probability()
        self.choice2 = Probability()

    def decode(self, pb_context: int) -> int:
        """Декодирует длину совпадения."""
        if self.range_decoder.decode_bit(self.choice1) == 0:
            length = self.low_coder[pb_context].decode()
        elif self.range_decoder.decode_bit(self.choice2) == 0:
            length = self.mid_coder[pb_context].decode() + 8
        else:
            length = self.high_coder.decode() + 16
        return length + const.MIN_MATCH_LEN
