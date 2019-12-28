import json
from collection import CollectionWriter, CollectionReader



def test_Collection():
    c = CollectionWriter("data_test")
    c.mkdir()
    c.write(json.dumps(dict(name="Pépé", age=42)).encode("utf8"))
    c.write(json.dumps(dict(name="Bob", age=12)).encode("utf8"))
    c.close()

    r = CollectionReader("data_test")
    assert json.loads(r[1])["name"] == "Bob"
    r.close()
