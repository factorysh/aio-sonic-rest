import pytest
from aiohttp import web

from .web import sonic_rest
from .search import Search
from .ingest import Ingestor


@pytest.fixture
async def app():
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
    app = web.Application()
    sonic_rest(
        app, Search("./data/store/collection", password="iuNg5Ri6daik2fe2Phoo6aig")
    )
    return app


async def test_query(aiohttp_client, app, loop):
    client = await aiohttp_client(app)
    resp = await client.get("/query?q=python")
    assert resp.status == 200
    j = await resp.json()
    j = j['results']
    assert len(j) == 2
    assert j[0]["name"] == "bob"


async def test_suggest(aiohttp_client, app, loop):
    client = await aiohttp_client(app)
    resp = await client.get("/suggest?s=car")
    assert resp.status == 200
    j = await resp.json()
    j = j['results']
    print(j)
    assert len(j) == 2
    assert "carottes" in j
    assert "carotte" in j
