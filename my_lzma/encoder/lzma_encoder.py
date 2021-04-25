from my_lzma.encoder.base_encoder import BaseEncoder
from my_lzma.encoder.range_encoder import RangeEncoder
from my_lzma.probability import Probability
from my_lzma.encoder.literal_encoder import LiteralEncoder
from my_lzma.encoder.distance_encoder import DistanceEncoder
from my_lzma.encoder.length_encoder import LengthEncoder
from pathlib import Path
from my_lzma.input_output import InputStream, OutputStream
from my_lzma.encoder.in_window import InWindow
from my_lzma.lzma_state import LZMAState
from my_lzma import const
from my_lzma.history import History


class LZMAEncoder(BaseEncoder):
    """Реализует кодирование LZMA."""

    def __init__(self, in_file: Path, out_file: Path, lc: int, lp: int,
                 pb: int, dict_size: int):
        self.input_stream = InputStream(in_file)
        self.file_size = in_file.stat().st_size
        self.output_stream = OutputStream(out_file)
        self.dict_size = dict_size
        range_encoder = RangeEncoder(self.output_stream)
        in_window = InWindow(dict_size, self.input_stream)
        super().__init__(lc, lp, pb, range_encoder, in_window)
        self.is_match = [[Probability() for j in range(1 << pb)] for i in
                         range(12)]
        self.is_rep = [Probability() for i in range(12)]
        self.is_rep_123 = [Probability() for i in range(12)]
        self.is_rep_23 = [Probability() for i in range(12)]
        self.is_rep_3 = [Probability() for i in range(12)]
        self.is_rep_0 = [[Probability() for j in range(1 << pb)] for i in
                         range(12)]
        self.literal_encoder = LiteralEncoder(lc, lp, pb, range_encoder,
                                              in_window)
        self.distance_encoder = DistanceEncoder(lc, lp, pb, range_encoder,
                                                in_window)
        self.length_encoder = LengthEncoder(lc, lp, pb, range_encoder,
                                            in_window)
        self.rep_length_encoder = LengthEncoder(lc, lp, pb, range_encoder,
                                                in_window)
        self.state = LZMAState()
        self.history = History()

    def encode_properties(self) -> None:
        """Кодирует свойства LZMA декодера."""
        if not (0 <= self.lc <= const.MAX_LC):
            raise Exception("Неверный параметр lc")
        if not (0 <= self.lp <= const.MAX_LP):
            raise Exception("Неверный параметр lp")
        if not (0 <= self.pb <= const.MAX_PB):
            raise Exception("Неверный параметр pb")
        if not (0 <= self.dict_size <= 0xFFFFFFFF):
            raise Exception("Неверный размер словаря")
        self.output_stream.write(
            bytes([(self.pb * 5 + self.lp) * 9 + self.lc]))
        self.output_stream.write(self.dict_size.to_bytes(4, 'little'))
        self.output_stream.write(self.file_size.to_bytes(8, 'little'))

    def pb_context(self) -> int:
        return self.in_window.num_encoded & ((1 << self.pb) - 1)

    def encode(self) -> None:
        """Кодирует LZMA."""
        self.encode_properties()
        while not self.in_window.is_finished():
            if self.try_encode_rep():
                continue
            if self.try_encode_short_rep():
                continue
            if self.try_encode_simple_match():
                continue
            self.encode_literal()
        self.range_encoder.terminate()

    def try_encode_rep(self) -> bool:
        """Пытается закодировать объект типа simple rep.
        Возвращает True, если удалось закодировать, иначе False.
        """
        if len(self.in_window.prev_buf) == 0:
            return False
        rep_num = -1
        match_length = 0
        for i in range(const.HISTORY_LEN):
            length = self.in_window.find_match_from(self.history[i])
            if length > match_length:
                match_length = length
                rep_num = i
        if match_length < const.MIN_MATCH_LEN:
            return False
        self.encode_rep(match_length, rep_num)
        return True

    def try_encode_short_rep(self) -> bool:
        """Пытается закодировать объект типа short rep.
        Возвращает True, если удалось закодировать, иначе False.
        """
        if len(self.in_window.prev_buf) == 0:
            return False
        if self.in_window[self.history[0]] != self.in_window.next_buf[0]:
            return False
        self.encode_short_rep()
        return True

    def try_encode_simple_match(self) -> bool:
        """Пытается закодировать объект типа simple match.
        Возвращает True, если удалось закодировать, иначе False.
        """
        match = self.in_window.find_match()
        if match is None:
            return False
        match_length, distance = match
        self.encode_simple_match(match_length, distance)
        return True

    def encode_literal(self) -> None:
        """Кодирует объект типа literal."""
        self.range_encoder.encode_bit(
            self.is_match[int(self.state)][self.pb_context()], 0)
        literal = int.from_bytes(self.in_window.next_buf[0], 'big')
        self.literal_encoder.encode(self.state, self.history[0], literal)
        self.in_window.move_window()
        self.state.update_literal()

    def encode_simple_match(self, match_length: int, distance: int) -> None:
        """Кодирует объект типа simple match."""
        self.range_encoder.encode_bit(
            self.is_match[int(self.state)][self.pb_context()], 1)
        self.range_encoder.encode_bit(self.is_rep[int(self.state)], 0)
        self.length_encoder.encode(match_length, self.pb_context())
        self.distance_encoder.encode(match_length, distance)
        self.history.add(distance)
        for i in range(match_length):
            self.in_window.move_window()
        self.state.update_simple_match()

    def encode_rep(self, match_length: int, rep_num: int) -> None:
        """Кодирует объект типа simple rep."""
        self.range_encoder.encode_bit(
            self.is_match[int(self.state)][self.pb_context()], 1)
        self.range_encoder.encode_bit(self.is_rep[int(self.state)], 1)
        if rep_num == 0:
            self.range_encoder.encode_bit(self.is_rep_123[int(self.state)], 0)
            self.range_encoder.encode_bit(
                self.is_rep_0[int(self.state)][self.pb_context()], 1)
        else:
            self.range_encoder.encode_bit(self.is_rep_123[int(self.state)], 1)
            if rep_num == 1:
                self.range_encoder.encode_bit(
                    self.is_rep_23[int(self.state)], 0)
            else:
                self.range_encoder.encode_bit(
                    self.is_rep_23[int(self.state)], 1)
                if rep_num == 2:
                    self.range_encoder.encode_bit(
                        self.is_rep_3[int(self.state)], 0)
                else:
                    self.range_encoder.encode_bit(
                        self.is_rep_3[int(self.state)], 1)
        distance = self.history[rep_num]
        self.history.add(distance)
        self.rep_length_encoder.encode(match_length, self.pb_context())
        for i in range(match_length):
            self.in_window.move_window()
        self.state.update_rep()

    def encode_short_rep(self) -> None:
        """Кодирует объект типа short rep."""
        self.range_encoder.encode_bit(
            self.is_match[int(self.state)][self.pb_context()], 1)
        self.range_encoder.encode_bit(self.is_rep[int(self.state)], 1)
        self.range_encoder.encode_bit(self.is_rep_123[int(self.state)], 0)
        self.range_encoder.encode_bit(
            self.is_rep_0[int(self.state)][self.pb_context()], 0)
        self.in_window.move_window()
        self.state.update_short_rep()

    def get_compression_rate(self) -> float:
        return self.in_window.in_stream.processed / self.range_encoder.out_stream.processed
