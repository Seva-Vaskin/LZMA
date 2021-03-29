from pathlib import Path
from my_lzma.encoder.lzma_encoder import LZMAEncoder
from my_lzma.decoder.lzma_decoder import LZMADecoder


def cmp_files(file1: Path, file2: Path) -> None:
    with file1.open() as f:
        data_1 = f.read()
    with file2.open() as f:
        data_2 = f.read()
    assert data_1 == data_2


def test_a():
    in_file = Path().cwd() / 'tests' / 'a.txt'
    mid_file = Path().cwd() / 'tests' / 'temp.lzma'
    encoder = LZMAEncoder(in_file, mid_file, 3, 0, 2, 1024 * 1024)
    encoder.encode()
    encoder.range_encoder.out_stream.file.close()
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    decoder = LZMADecoder(mid_file, out_file)
    decoder.decode()
    decoder.out_window.out_stream.file.close()
    cmp_files(in_file, out_file)


def test_long_string():
    in_file = Path().cwd() / 'tests' / 'long_string.txt'
    mid_file = Path().cwd() / 'tests' / 'temp.lzma'
    encoder = LZMAEncoder(in_file, mid_file, 3, 0, 2, 300)
    encoder.encode()
    encoder.range_encoder.out_stream.file.close()
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    decoder = LZMADecoder(mid_file, out_file)
    decoder.decode()
    decoder.out_window.out_stream.file.close()
    cmp_files(in_file, out_file)


def test_rand_string():
    in_file = Path().cwd() / 'tests' / 'rand_string.txt'
    mid_file = Path().cwd() / 'tests' / 'temp.lzma'
    encoder = LZMAEncoder(in_file, mid_file, 3, 0, 2, 300)
    encoder.encode()
    encoder.range_encoder.out_stream.file.close()
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    decoder = LZMADecoder(mid_file, out_file)
    decoder.decode()
    decoder.out_window.out_stream.file.close()
    cmp_files(in_file, out_file)


def test_incorrect_lc():
    in_file = Path().cwd() / 'tests' / 'long_string.txt'
    out_file = Path().cwd() / 'tests' / 'temp.lzma'
    try:
        encoder = LZMAEncoder(in_file, out_file, -1, 0, 2, 1024)
        encoder.encode()
    except BaseException:
        return
    assert False


def test_incorrect_lp():
    in_file = Path().cwd() / 'tests' / 'long_string.txt'
    out_file = Path().cwd() / 'tests' / 'temp.lzma'
    try:
        encoder = LZMAEncoder(in_file, out_file, 3, -1, 2, 1024)
        encoder.encode()
    except BaseException:
        return
    assert False


def test_incorrect_pb():
    in_file = Path().cwd() / 'tests' / 'long_string.txt'
    out_file = Path().cwd() / 'tests' / 'temp.lzma'
    try:
        encoder = LZMAEncoder(in_file, out_file, 3, 0, -1, 1024)
        encoder.encode()
    except BaseException:
        return
    assert False


def test_incorrect_dict_size():
    in_file = Path().cwd() / 'tests' / 'long_string.txt'
    out_file = Path().cwd() / 'tests' / 'temp.lzma'
    try:
        encoder = LZMAEncoder(in_file, out_file, 3, 0, 2, -1)
        encoder.encode()
    except BaseException:
        return
    assert False
