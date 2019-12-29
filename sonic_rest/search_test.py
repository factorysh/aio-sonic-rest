import pytest
from aiohttp import web

from search import Search


@pytest.fixture
async def app():
    app = web.Application()
    await Search(app, password="iuNg5Ri6daik2fe2Phoo6aig",
                 store="./data/store/collection")
    return app


async def test_query(aiohttp_client, app, loop):
    client = await aiohttp_client(app)
    resp = await client.get("/query?q=carotte")
    assert resp.status == 200
    j = await resp.json()
    print(j)
    assert len(j) == 1


async def test_suggest(aiohttp_client, app, loop):
    client = await aiohttp_client(app)
    resp = await client.get("/suggest?s=car")
    assert resp.status == 200
    j = await resp.json()
    print(j)
    assert len(j) == 1
    assert j[0] == "carottes"
