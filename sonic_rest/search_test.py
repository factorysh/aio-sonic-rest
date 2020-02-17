import pytest

from .ingest import Ingestor
from .search import Search


@pytest.fixture
def search():
    i = Ingestor(
        dict(
            name=dict(stored=True),
            body=dict(indexed=True),
            tags=dict(stored=True, indexed=True,),
        ),
        password="iuNg5Ri6daik2fe2Phoo6aig",
        path="./data/store/collection",
    )
    i.reset()
    documents = [
        dict(name="alice", body="Elle a mangé des carottes.", tags=["carotte"]),
        dict(name="bob", body="Il fait du Django.", tags=["python", "django"]),
        dict(name="charly", body="Il a un python dans son vivarium.", tags=[]),
    ]
    i.ingest(documents)
    return Search("./data/store/collection", password="iuNg5Ri6daik2fe2Phoo6aig")


async def test_search(search):
    i = 0
    async for r in search.search("python", ["tags", "body"]):
        if i == 0:
            assert r["name"] == "bob"
        i += 1
