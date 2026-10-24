"""A content-addressed object store that names blobs exactly like git does."""
import hashlib
import math
import os
import tempfile
import zlib


def blob_id(content: bytes) -> str:
    header = b"blob %d\0" % len(content)
    return hashlib.sha1(header + content).hexdigest()


class Store:
    def __init__(self, root):
        self.root = root

    def _path(self, oid):
        return os.path.join(self.root, oid[:2], oid[2:])

    def put(self, content: bytes) -> str:
        oid = blob_id(content)
        path = self._path(oid)
        if not os.path.exists(path):              # same content is stored once
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(zlib.compress(b"blob %d\0" % len(content) + content))
        return oid

    def get(self, oid) -> bytes:
        with open(self._path(oid), "rb") as f:
            raw = zlib.decompress(f.read())
        content = raw[raw.index(b"\0") + 1:]
        assert blob_id(content) == oid, "object corrupted"
        return content


if __name__ == "__main__":
    assert blob_id(b"hello\n") == "ce013625030ba8dba906f756967f9e9ca394464a"
    assert blob_id(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    with tempfile.TemporaryDirectory() as d:
        s = Store(d)
        a = s.put(b"E = 210e9  # steel, Pa\n")
        b = s.put(b"E = 210e9  # steel, Pa\n")
        c = s.put(b"E = 210e9  # steel, Pa \n")   # one extra space
        assert a == b and a != c
        assert s.get(a) == b"E = 210e9  # steel, Pa\n"
        print("ids:", a[:10], c[:10])
    p = (1e6) ** 2 / 2 ** 161
    assert 3.4e-37 < p < 3.5e-37
    assert math.ceil(math.log2(1000)) == 10
    print(f"collision chance for 1e6 objects: {p:.2e}")
