import json
from pathlib import Path
from .collection import CollectionSerializer, CollectionReader


def test_Collection():
    p = Path("data/test")
    with CollectionSerializer(p) as c:
        c.reset()
        assert len(c) == 0
        c.append(dict(name="Pépé", age=42))
        c.append(dict(name="Bob", age=12))
        assert len(c) == 2

    with CollectionSerializer(p) as c:
        assert len(c) == 2
        c.append(dict(name="Charline", age=17))
        assert len(c) == 3

    with CollectionReader("data/test") as r:
        assert len(r) == 3
        assert json.loads(r[1])["name"] == "Bob"
