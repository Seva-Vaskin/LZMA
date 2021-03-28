from my_lzma.encoder.base_encoder import BaseEncoder
from my_lzma.encoder.bit_tree_encoder import BitTreeEncoder
from my_lzma.lzma_state import LZMAState


class LiteralEncoder(BaseEncoder):
    """Реализует кодирование литералов."""

    def __init__(self, *args):
        super().__init__(*args)
        self.match_prob = [[[BitTreeEncoder(8, self.range_encoder)
                             for k in range(2)]
                            for j in range(1 << self.lp)]
                           for i in range(1 << self.lc)]
        self.prob = [[BitTreeEncoder(8, self.range_encoder)
                      for j in range(1 << self.lp)]
                     for i in range(1 << self.lc)]

    def encode(self, state: LZMAState, rep0: int, literal: int) -> None:
        """Кодирует литерал."""
        if self.in_window.num_encoded:
            prev_byte = int.from_bytes(self.in_window[0], 'big')
        else:
            prev_byte = 0
        lc_context = prev_byte >> (8 - self.lc)
        lp_context = self.in_window.num_encoded & ((1 << self.lp) - 1)
        match_prob = self.match_prob[lc_context][lp_context]
        prob = self.prob[lc_context][lp_context]
        v = 1
        if int(state) >= 7:
            match_byte = int.from_bytes(self.in_window[rep0], 'big')
            while True:
                match_bit = match_byte >> 7 & 1
                match_byte <<= 1
                bit = literal >> 7 & 1
                literal <<= 1
                self.range_encoder.encode_bit(match_prob[match_bit][v], bit)
                v = v * 2 + bit
                if bit != match_bit or v >= len(match_prob[0].tree):
                    break
        while v < len(prob.tree):
            bit = literal >> 7 & 1
            literal <<= 1
            self.range_encoder.encode_bit(prob[v], bit)
            v = v * 2 + bit
