from my_lzma.decoder.lzma_decoder import LZMADecoder
from pathlib import Path


def cmp_files(file1: Path, file2: Path) -> None:
    with file1.open() as f:
        data_1 = f.read()
    with file2.open() as f:
        data_2 = f.read()
    assert data_1 == data_2


def test_decode_a():
    in_file = Path().cwd() / 'tests' / 'a.lzma'
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    decoder = LZMADecoder(in_file, out_file)
    decoder.decode()
    decoder.out_window.out_stream.file.close()
    cmp_files(out_file, Path().cwd() / 'tests' / 'a.txt')


def test_decode_a_eos():
    in_file = Path().cwd() / 'tests' / 'a_eos.lzma'
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    decoder = LZMADecoder(in_file, out_file)
    decoder.decode()
    decoder.out_window.out_stream.file.close()
    cmp_files(out_file, Path().cwd() / 'tests' / 'a.txt')


def test_decode_a_eos_and_size():
    in_file = Path().cwd() / 'tests' / 'a_eos_and_size.lzma'
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    decoder = LZMADecoder(in_file, out_file)
    decoder.decode()
    decoder.out_window.out_stream.file.close()
    cmp_files(out_file, Path().cwd() / 'tests' / 'a.txt')


def test_decode_a_lp1_lc2_pb1():
    in_file = Path().cwd() / 'tests' / 'a_lp1_lc2_pb1.lzma'
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    decoder = LZMADecoder(in_file, out_file)
    decoder.decode()
    decoder.out_window.out_stream.file.close()
    cmp_files(out_file, Path().cwd() / 'tests' / 'a.txt')


def test_bad_corrupted():
    in_file = Path().cwd() / 'tests' / 'bad_corrupted.lzma'
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    try:
        decoder = LZMADecoder(in_file, out_file)
        decoder.decode()
    except BaseException:
        return
    assert False


def test_bad_eos_incorrect_size():
    in_file = Path().cwd() / 'tests' / 'bad_eos_incorrect_size.lzma'
    out_file = Path().cwd() / 'tests' / 'temp.txt'
    try:
        decoder = LZMADecoder(in_file, out_file)
        decoder.decode()
    except BaseException:
        return
    assert False


def test_bad_incorrect_size():
    in_file = Path().cwd() / 'bad_incorrect_size.lzma'
    out_file = Path().cwd() / 'temp.txt'
    try:
        decoder = LZMADecoder(in_file, out_file)
        decoder.decode()
    except BaseException:
        return
    assert False
