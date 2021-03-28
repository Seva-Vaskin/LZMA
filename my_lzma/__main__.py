from pathlib import Path
from my_lzma.decoder.lzma_decoder import LZMADecoder
from my_lzma.encoder.lzma_encoder import LZMAEncoder
from my_lzma import const
import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--encode', help='Установите этот флаг, '
                                               'если программа должна '
                                               'работать в режиме '
                                               'архивирования',
                        action='store_true')
    parser.add_argument('-d', '--decode', help='Установите этот флаг, '
                                               'если программа должна '
                                               'работать в режиме '
                                               'деархивирования',
                        action='store_true')
    parser.add_argument('-i', '--input', help='Путь до входного файла',
                        type=str)
    parser.add_argument('-o', '--output', help='Путь до выходного файла',
                        type=str)
    parser.add_argument('--lc', help='lc параметр кодирования. По умолчанию '
                                     'lc=3', type=int, default=3,
                        choices=[i for i in range(const.MAX_LC + 1)])
    parser.add_argument('--lp', help='lp параметр кодирования. По умолчанию '
                                     'lp=0', type=int, default=0,
                        choices=[i for i in range(const.MAX_LP + 1)])
    parser.add_argument('--pb', help='pb параметр кодирования. По умолчанию '
                                     'pb=2', type=int, default=2,
                        choices=[i for i in range(const.MAX_PB + 1)])
    parser.add_argument('-s', '--size', help='Размер словаря для кодирования '
                                             'в байтах. По умолчанию 16 Мб',
                        type=int, default=16777216)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.encode ^ args.decode:
        print("Неверно выбран режим работы архиватора", file=sys.stderr)
        sys.exit(0)
    in_path = Path(args.input)
    if not in_path.is_file():
        print("Неверный путь до входного файла", file=sys.stderr)
        sys.exit(0)
    out_path = Path(args.output)
    if out_path.exists() and not out_path.is_file():
        print("Неверный путь до выходного файла", file=sys.stderr)
        sys.exit(0)
    if not 0 <= args.size <= 0xFFFFFFFF:
        print("Размер словаря должен быть целым беззнаковым 32 битным числом.",
              file=sys.stderr)
        sys.exit(0)

    if args.decode:
        decoder = LZMADecoder(in_path, out_path)
        decoder.decode()
    elif args.encode:
        encoder = LZMAEncoder(in_path, out_path, args.lc, args.lp, args.pb,
                              args.size)
        encoder.encode()
