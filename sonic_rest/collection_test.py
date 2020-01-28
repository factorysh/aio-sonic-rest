import json
from .collection import CollectionSerializer, CollectionReader


def test_Collection():
    with CollectionSerializer("data/test") as c:
        c.mkdir()
        c.append(dict(name="Pépé", age=42))
        c.append(dict(name="Bob", age=12))

    with CollectionReader("data/test") as r:
        assert json.loads(r[1])["name"] == "Bob"
