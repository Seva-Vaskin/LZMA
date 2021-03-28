from my_lzma.encoder.base_encoder import BaseEncoder
from my_lzma.encoder.bit_tree_encoder import BitTreeEncoder
from my_lzma import const


class DistanceEncoder(BaseEncoder):
    """Реализует кодирование дистанции между строками совпадения."""

    def __init__(self, *args):
        super().__init__(*args)
        self.case_encoder = [BitTreeEncoder(6, self.range_encoder)
                             for i in range(const.LEN_CONTEXTS)]
        self.x_encoder = [BitTreeEncoder((i + 2) >> 1, self.range_encoder)
                          for i in range(10)]
        self.z_encoder = BitTreeEncoder(4, self.range_encoder)

    def encode(self, match_length: int, dist: int) -> None:
        """Кодирует дистанцию между сроками совпадения."""
        length_context = match_length - const.MIN_MATCH_LEN
        if length_context > const.LEN_CONTEXTS - 1:
            length_context = const.LEN_CONTEXTS - 1
        bit_length = dist.bit_length()
        if bit_length <= 2:
            case = dist
        else:
            case = (bit_length - 1) * 2 + (dist >> (bit_length - 2) & 1)
        self.case_encoder[length_context].encode(case)
        if case < 4:
            return
        dist &= (1 << (bit_length - 2)) - 1
        if case < 14:
            self.x_encoder[case - 4].reverse_encode(dist)
        else:
            y_bits = bit_length - 6
            z = dist & 0x0F
            y = dist >> 4
            self.range_encoder.encode_direct_bits(y, y_bits)
            self.z_encoder.reverse_encode(z)
