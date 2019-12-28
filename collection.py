from pathlib import Path
import struct
from mmap import mmap


class CollectionWriter:
    _data_w = None
    _idx_w = None
    _poz = 0

    def __init__(self, path):
        self.path = path

    def mkdir(self, mode=0o777):
        Path(self.path).mkdir(mode=mode, parents=True, exist_ok=True)

    def data_w(self):
        if self._data_w is None:
            self._data_w = (Path(self.path) / "data").open('wb')
        return self._data_w

    def idx_w(self):
        if self._idx_w is None:
            self._idx_w = (Path(self.path) / "index").open('wb')
        return self._idx_w

    def close(self):
        if self._data_w is not None:
            self._data_w.close()
        if self._idx_w is not None:
            self._idx_w.close()

    def write(self, raw: bytes):
        self.data_w().write(raw)
        self.idx_w().write(struct.pack("!II", self._poz, self._poz+len(raw)))
        self._poz += len(raw)


class CollectionReader:
    def __init__(self, path):
        self._len = (Path(path) / "index").stat().st_size / 8
        self._idx_o = open(Path(path) / "index", "r+b")
        self._idx = mmap(self._idx_o.fileno(), 0)
        self._data_o = open(Path(path) / "data", "r+b")
        self._data = mmap(self._data_o.fileno(), 0)

    def close(self):
        self._idx_o.close()
        self._data_o.close()

    def __len__(self):
        return self._len

    def __getitem__(self, index):
        if type(index) != int:
            raise TypeError()
        if index >= self._len:
            raise IndexError()
        if index < 0:
            index = self._len - index
        start, end = struct.unpack("!II", self._idx[index*8:index*8+8])
        return self._data[start:end]
