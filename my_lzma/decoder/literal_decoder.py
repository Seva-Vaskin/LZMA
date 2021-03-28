from my_lzma.decoder.base_decoder import BaseDecoder
from my_lzma.decoder.bit_tree_decoder import BitTreeDecoder
from my_lzma.lzma_state import LZMAState


class LiteralDecoder(BaseDecoder):
    """Реализует декодирование литералов."""

    def __init__(self, *args):
        super().__init__(*args)
        self.match_prob = [[[BitTreeDecoder(8, self.range_decoder)
                             for k in range(2)]
                            for j in range(1 << self.lp)]
                           for i in range(1 << self.lc)]
        self.prob = [[BitTreeDecoder(8, self.range_decoder)
                      for j in range(1 << self.lp)]
                     for i in range(1 << self.lc)]

    def decode(self, state: LZMAState, rep0: int) -> int:
        """Декодирует литерал."""
        if self.out_window.num_decoded:
            prev_byte = int.from_bytes(self.out_window[1], 'big')
        else:
            prev_byte = 0
        lc_context = prev_byte >> (8 - self.lc)
        lp_context = self.out_window.num_decoded & ((1 << self.lp) - 1)
        match_prob = self.match_prob[lc_context][lp_context]
        prob = self.prob[lc_context][lp_context]
        literal = 0
        v = 1
        if int(state) >= 7:
            match_byte = int.from_bytes(self.out_window[rep0 + 1], 'big')
            while True:
                match_bit = (match_byte >> 7) & 1
                match_byte <<= 1
                bit = self.range_decoder.decode_bit(match_prob[match_bit][v])
                literal = literal << 1 | bit
                v = v * 2 + bit
                if bit != match_bit or v >= len(match_prob[0].tree):
                    break
        while v < len(prob.tree):
            bit = self.range_decoder.decode_bit(prob[v])
            literal = literal << 1 | bit
            v = v * 2 + bit
        return literal
