import json
import shutil
import pytest
from pathlib import Path
from .collection import CollectionSerializer, CollectionReader


@pytest.fixture
def p(request):
    p = Path('data/test')
    yield p
    shutil.rmtree('data/test')


def test_append(p):
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


def test_reader(p):
    with CollectionSerializer(p) as c:
        c.reset()
        assert len(c) == 0
        c.append(dict(name="Pépé", age=42))
        c.append(dict(name="Bob", age=12))
        c.append(dict(name="Charline", age=17))

    with CollectionReader(p) as r:
        assert len(r) == 3
        assert json.loads(r[1])["name"] == "Bob"
        shutil.rmtree(str(p))
        with CollectionSerializer(p) as c:
            c.reset()
            assert len(c) == 0
            c.append(dict(name="Pépé", age=42))
            c.append(dict(name="Bobby", age=12))
            assert len(c) == 2
        assert len(r) == 2
        assert json.loads(r[1])["name"] == "Bobby"
