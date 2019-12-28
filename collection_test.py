import json
from collection import CollectionSerializer, CollectionReader



def test_Collection():
    with CollectionSerializer("data_test") as c:
        c.mkdir()
        c.append(dict(name="Pépé", age=42))
        c.append(dict(name="Bob", age=12))

    with CollectionReader("data_test") as r:
        assert json.loads(r[1])["name"] == "Bob"
