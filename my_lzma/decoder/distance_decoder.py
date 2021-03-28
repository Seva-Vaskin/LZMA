from my_lzma.decoder.base_decoder import BaseDecoder
from my_lzma.decoder.bit_tree_decoder import BitTreeDecoder
from my_lzma import const


class DistanceDecoder(BaseDecoder):
    """Реализует декодирование дистанции между строками совпадения."""

    def __init__(self, *args):
        super().__init__(*args)
        self.case_decoder = [BitTreeDecoder(6, self.range_decoder)
                             for i in range(const.LEN_CONTEXTS)]
        self.x_decoder = [BitTreeDecoder((i + 2) >> 1, self.range_decoder)
                          for i in range(10)]
        self.z_decoder = BitTreeDecoder(4, self.range_decoder)

    def decode(self, match_length: int) -> int:
        """Декодирует дистанцию между сроками совпадения."""
        length_context = match_length - const.MIN_MATCH_LEN
        if length_context > const.LEN_CONTEXTS - 1:
            length_context = const.LEN_CONTEXTS - 1
        case = self.case_decoder[length_context].decode()
        if case < 4:
            return case
        elif case < 14:
            x_bits = (case - 2) >> 1
            ans = 2 | (case & 1)
            x = self.x_decoder[case - 4].reverse_decode()
            ans = ans << x_bits | x
            return ans
        else:
            y_bits = (case - 10) >> 1
            ans = 2 | (case & 1)
            y = self.range_decoder.decode_direct_bits(y_bits)
            ans = ans << y_bits | y
            z = self.z_decoder.reverse_decode()
            ans = ans << 4 | z
            return ans
