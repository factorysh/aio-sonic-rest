"""
Ordered collection of bytes for write once, read many, from any number of
process.  It uses two files and mmap.

"data" file is the concatenation of values (some bytes).

"index" file is an array of positions, start/end, encoded as unsigned int,
in big indian.

CollectionSerializer is an helper, it stores jsoned value.
"""


from pathlib import Path
import struct
import json
from mmap import mmap


class CollectionWriter:
    def __init__(self, path, mode=0o777):
        if isinstance(path, Path):
            self.path = path
        else:
            self.path = Path(path)
        self.mode = mode
        self._start()

    def reset(self):
        self.close()
        (self.path / "index").unlink()
        (self.path / "data").unlink()
        self._start()

    def _start(self):
        self.path.mkdir(mode=self.mode, parents=True, exist_ok=True)
        p = self.path / "index"
        self._poz = 0
        if p.exists():
            self._len = int(p.stat().st_size / 8)
            if self._len > 0:
                with p.open("r+b") as i:
                    m = mmap(i.fileno(), 0)
                    _, self._poz = struct.unpack("!II", m[-8:])
        else:
            self._len = 0
        self._idx_w = p.open("ab")
        self._data_w = (self.path / "data").open("ab")
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __len__(self):
        return self._len

    def flush(self):
        self._data_w.flush()
        self._idx_w.flush()

    def close(self):
        self.flush()
        self._data_w.close()
        self._idx_w.close()
        self._closed = True

    def write(self, raw: bytes):
        if self._closed:
            raise Exception("Collection is closed")
        self._data_w.write(raw)
        self._idx_w.write(struct.pack("!II", self._poz, self._poz + len(raw)))
        self._len += 1
        self._poz += len(raw)


class CollectionSerializer(CollectionWriter):
    def serialize(self, data):
        return json.dumps(data)

    def append(self, data):
        raw = self.serialize(data)
        if type(raw) == str:
            raw = raw.encode("utf8")
        self.write(raw)


class CollectionReader:
    def __init__(self, path):
        path = Path(path)
        self._len = int((path / "index").stat().st_size / 8)
        self._idx_o = open(str(path / "index"), "r+b")
        self._idx = mmap(self._idx_o.fileno(), 0)
        self._data_o = open(str(path / "data"), "r+b")
        self._data = mmap(self._data_o.fileno(), 0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self._idx_o.close()
        self._data_o.close()

    def __len__(self):
        return self._len

    def __getitem__(self, index):
        if type(index) != int:
            raise TypeError("index must be an int")
        if index >= self._len:
            raise IndexError("index does no exists")
        if index < 0:
            index = self._len - index
        start, end = struct.unpack("!II", self._idx[index * 8 : index * 8 + 8])
        return self._data[start:end]
