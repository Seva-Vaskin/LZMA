from my_lzma.decoder.range_decoder import RangeDecoder
from my_lzma.decoder.out_window import OutWindow


class BaseDecoder:
    """Описывает общую часть декодеров."""

    def __init__(self, lc: int, lp: int, pb: int, range_decoder: RangeDecoder,
                 out_window: OutWindow):
        self.lc = lc
        self.lp = lp
        self.pb = pb
        self.range_decoder = range_decoder
        self.out_window = out_window

    def decode(self, *args) -> None:
        """Данный метод должен быть реализован в наследниках."""
        raise NotImplementedError()
