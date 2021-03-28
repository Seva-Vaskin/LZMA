from my_lzma.decoder.base_decoder import BaseDecoder
from my_lzma.decoder.out_window import OutWindow
from my_lzma.decoder.range_decoder import RangeDecoder
from my_lzma.probability import Probability
from my_lzma.decoder.literal_decoder import LiteralDecoder
from my_lzma.decoder.distance_decoder import DistanceDecoder
from my_lzma.decoder.length_decoder import LengthDecoder
from typing import Tuple
from pathlib import Path
from my_lzma.input_output import InputStream, OutputStream
from my_lzma import const
from my_lzma.lzma_state import LZMAState
from my_lzma.history import History


class LZMADecoder(BaseDecoder):
    """Реализует декодирование LZMA."""

    def __init__(self, in_file: Path, out_file: Path):
        input_stream = InputStream(in_file)
        properties = input_stream.read(5)
        lc, lp, pb, dict_size = LZMADecoder.decode_properties(properties)
        unpack_size_bytes = input_stream.read(8)
        self.unpack_size = int.from_bytes(unpack_size_bytes,
                                          byteorder='little')
        self.unpack_size_defined = self.unpack_size != 0xFFFFFFFFFFFFFFFF
        output_stream = OutputStream(out_file)
        out_window = OutWindow(dict_size, output_stream)
        range_decoder = RangeDecoder(input_stream)
        super().__init__(lc, lp, pb, range_decoder, out_window)
        self.is_match = [[Probability() for j in range(1 << pb)] for i in
                         range(12)]
        self.is_rep = [Probability() for i in range(12)]
        self.is_rep_123 = [Probability() for i in range(12)]
        self.is_rep_23 = [Probability() for i in range(12)]
        self.is_rep_3 = [Probability() for i in range(12)]
        self.is_rep_0 = [[Probability() for j in range(1 << pb)] for i in
                         range(12)]
        self.literal_decoder = LiteralDecoder(lc, lp, pb, range_decoder,
                                              out_window)
        self.distance_decoder = DistanceDecoder(lc, lp, pb, range_decoder,
                                                out_window)
        self.length_decoder = LengthDecoder(lc, lp, pb, range_decoder,
                                            out_window)
        self.rep_length_decoder = LengthDecoder(lc, lp, pb, range_decoder,
                                                out_window)
        self.history = History()
        self.state = LZMAState()
        self.end_marker = False

    @staticmethod
    def decode_properties(properties: bytes) -> Tuple[int, int, int, int]:
        """Декодирует свойства LZMA декодера."""
        contexts = properties[0]
        if contexts >= 9 * 5 * 5:
            raise Exception("Неверные параметры LZMA")
        lc = contexts % 9
        contexts //= 9
        lp = contexts % 5
        contexts //= 5
        pb = contexts
        dict_size = int.from_bytes(properties[1:5:], byteorder='little')
        if dict_size < const.DICT_MIN:
            dict_size = const.DICT_MIN
        return lc, lp, pb, dict_size

    def pb_context(self):
        return self.out_window.num_decoded & ((1 << self.pb) - 1)

    def decode(self):
        """Декодирует LZMA."""
        while not self.end_marker and (not self.unpack_size_defined or
                                       self.unpack_size > 0):
            if self.range_decoder.decode_bit(self.is_match[int(self.state)][
                                                 self.pb_context()]):
                self.decode_match()
            else:
                self.decode_literal()
        if self.unpack_size_defined and self.unpack_size != 0:
            raise Exception("LZMA error")
        if not self.range_decoder.is_finished_ok() and not \
                self.check_end_marker_in_input_stream():
            raise Exception("LZMA error")

    def check_end_marker_in_input_stream(self) -> bool:
        """Проверяет наличие флага завершения во входном потоке."""
        if self.end_marker:
            return False
        bit = self.range_decoder.decode_bit(self.is_match[int(self.state)][
                                                self.pb_context()])
        if not bit:
            return False
        bit = self.range_decoder.decode_bit(self.is_rep[int(self.state)])
        if bit:
            return False
        length = self.length_decoder.decode(self.pb_context())
        distance = self.distance_decoder.decode(length)
        return distance == 0xFFFFFFFF and self.range_decoder.is_finished_ok()

    def decode_literal(self):
        """Декодирует литерал и помещает его в выходной поток."""
        literal = self.literal_decoder.decode(self.state, self.history[0])
        self.out_window.put_byte(bytes([literal]))
        self.unpack_size -= 1
        self.state.update_literal()

    def decode_match(self):
        """Декодирует пару (match, distance), используя simple или rep match.
        """
        if self.range_decoder.decode_bit(self.is_rep[int(self.state)]):
            self.decode_rep_match()
        else:
            self.decode_simple_match()

    def decode_rep_match(self):
        if self.range_decoder.decode_bit(self.is_rep_123[int(self.state)]):
            # rep match 1/2/3
            if not self.range_decoder.decode_bit(
                    self.is_rep_23[int(self.state)]):
                distance = self.history[1]
            elif not self.range_decoder.decode_bit(
                    self.is_rep_3[int(self.state)]):
                distance = self.history[2]
            else:
                distance = self.history[3]
        else:
            # rep 0 / short rep
            if self.range_decoder.decode_bit(self.is_rep_0[int(self.state)][
                                                 self.pb_context()]):
                # rep match 0
                distance = self.history[0]
            else:
                # Short rep match
                self.decode_short_rep_match()
                return
        self.history.add(distance)
        length = self.rep_length_decoder.decode(self.pb_context())
        self.unpack_size -= length
        if self.unpack_size_defined and self.unpack_size < 0:
            raise Exception("LZMA error")
        self.out_window.copy_match(distance + 1, length)
        self.state.update_rep()

    def decode_simple_match(self):
        """Декодирует пару (match, distance), используя length и distance
        декодеры, помещает соответствующую подстроку в выходной поток.
        """
        length = self.length_decoder.decode(self.pb_context())
        distance = self.distance_decoder.decode(length)
        if distance == 0xFFFFFFFF:
            self.end_marker = True
            return
        self.unpack_size -= length
        if self.unpack_size_defined and self.unpack_size < 0:
            raise Exception("LZMA error")
        self.history.add(distance)
        self.out_window.copy_match(distance + 1, length)
        self.state.update_simple_match()

    def decode_short_rep_match(self):
        self.out_window.copy_match(self.history[0] + 1, 1)
        self.unpack_size -= 1
        self.state.update_short_rep()
