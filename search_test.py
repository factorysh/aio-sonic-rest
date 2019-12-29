from search import Search
from aiohttp import web


async def test_query(aiohttp_client, loop):
    app = web.Application()
    await Search(app, password="iuNg5Ri6daik2fe2Phoo6aig")
    client = await aiohttp_client(app)
    resp = await client.get("/query?q=carotte")
    assert resp.status == 200
    j = await resp.json()
    print(j)
    assert len(j) == 1


async def test_suggest(aiohttp_client, loop):
    app = web.Application()
    await Search(app, password="iuNg5Ri6daik2fe2Phoo6aig")
    client = await aiohttp_client(app)
    resp = await client.get("/suggest?s=car")
    assert resp.status == 200
    j = await resp.json()
    print(j)
    assert len(j) == 1
    assert j[0] == "carottes"
