"""
REST API for Sonic, using an aiohttp application.

Sonic stores nothing, search returns just a collection of id.
Query return stored documents, already serialized.
"""
from aiohttp import web


async def query(request):
    resp = web.StreamResponse(
        status=200, reason="OK", headers={"Content-Type": "application/json"}
    )
    query = request.query.get('q')
    await resp.prepare(request)
    if not query:
        await resp.write(b'{"error": "no query provided"}')
    else:
        await resp.write(b'{"results": [')
        size, results = await request.app["search"].search_naked(
            query, request.app["fields"]
        )
        for i, r in enumerate(results):
            await resp.write(r)
            if i + 1 < size:
                await resp.write(b",")
        await resp.write(b"]}")
    await resp.drain()
    return resp


async def suggest(request):
    s = request.query.get("s")
    if s is None:
        return web.json_response([])
    suggestions = await request.app["search"].suggest(s, request.app["fields"])
    return web.json_response([j.decode("utf8") for j in suggestions])


def sonic_rest(app, search, fields=['tags', 'body'], root="/"):
    app["search"] = search
    app["fields"] = fields
    app.add_routes([
        web.get("%squery" % root, query),
        web.get("%ssuggest" % root, suggest),
    ])
