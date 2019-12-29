"""
REST API for Sonic, using an aiohttp application.

Sonic stores nothing, search returns just a collection of id.
Query return stored documents, already serialized.
"""
import asyncio

from collection import CollectionReader


from aiohttp import web
from asonic import Client
from asonic.enums import Channels


async def query(request):
    r = await request.app["sonic"].query(
        request.app["site"],
        request.query.get("bucket", "body"),
        request.query.get("q", ""),
    )
    resp = web.StreamResponse(
        status=200, reason="OK", headers={"Content-Type": "application/json"}
    )
    await resp.prepare(request)
    await resp.write(b"[")
    i = 1
    for id in r:
        await resp.write(request.app["collection"][int(id)])
        if i < len(r):
            await resp.write(b",")
        i += 1
        await resp.drain()
    await resp.write(b"]")
    return resp


async def suggest(request):
    s = request.query.get("s")
    if s is None:
        return web.json_response([])
    r = await request.app["sonic"].suggest(
        request.app["site"], request.query.get("bucket", "body"), s, 5
    )
    return web.json_response([j.decode("utf8") for j in r])


async def Search(
    app, host="127.0.0.1", port=1491, password=None, site="site", store="./data/kv"
):
    app["sonic"] = Client(host=host, port=port, password=password, max_connections=100)
    await app["sonic"].channel(Channels.SEARCH.value)
    app["site"] = site
    app["collection"] = CollectionReader(store)
    app.add_routes([web.get("/query", query), web.get("/suggest", suggest)])


if __name__ == "__main__":
    app = web.Application()
