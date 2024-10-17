from pyspectra.readers.read_dx import read_dx
def convert(file_path):
    return read_dx.read(file_path)