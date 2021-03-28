from my_lzma.encoder.range_encoder import RangeEncoder
from my_lzma.encoder.in_window import InWindow


class BaseEncoder:
    """Описывает общую часть кодеров."""

    def __init__(self, lc: int, lp: int, pb: int, range_encoder: RangeEncoder,
                 in_window: InWindow):
        self.lc = lc
        self.lp = lp
        self.pb = pb
        self.range_encoder = range_encoder
        self.in_window = in_window

    def encode(self, *args):
        """Данный метод должен быть реализован в наследниках."""
        raise NotImplementedError()
