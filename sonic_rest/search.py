"""
REST API for Sonic, using an aiohttp application.

Sonic stores nothing, search returns just a collection of id.
Query return stored documents, already serialized.
"""
from aiohttp import web
from asonic import Client
from asonic.enums import Channels

from .collection import CollectionReader


async def query(request):
    resp = web.StreamResponse(
        status=200, reason="OK", headers={"Content-Type": "application/json"}
    )
    await resp.prepare(request)
    await resp.write(b"[")
    already = set()
    for field in request.app["fields"]:
        r = await request.app["sonic"].query(
            request.app["site"],
            field,
            request.query.get("q", ""),
        )
        ids = [int(id) for id in r if int(id) not in already]
        if len(ids) == 0:
            continue
        if len(already) > 0:
            await resp.write(b",")
        already = already.union(ids)
        for i, id in enumerate(ids):
            await resp.write(request.app["collection"][id])
            if i+1 < len(ids):
                await resp.write(b",")
            await resp.drain()
    await resp.write(b"]")
    return resp


async def suggest(request):
    s = request.query.get("s")
    if s is None:
        return web.json_response([])
    already = set()
    suggestions = list()
    for field in request.app["fields"]:
        r = await request.app["sonic"].suggest(
            request.app["site"], field, s, 5
        )
        suggestions += [a for a in r if a not in already]
        already = already.union(r)

    return web.json_response([j.decode("utf8") for j in suggestions])


async def Search(
    app, host="127.0.0.1", port=1491, password=None, site="site", store="./data/kv"
):
    app["sonic"] = Client(host=host, port=port, password=password, max_connections=100)
    await app["sonic"].channel(Channels.SEARCH.value)
    app["site"] = site
    app["fields"] = ["tags", "body"]
    app["collection"] = CollectionReader(store)
    app.add_routes([web.get("/query", query), web.get("/suggest", suggest)])
