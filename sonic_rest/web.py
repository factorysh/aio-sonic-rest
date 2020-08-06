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
    await resp.prepare(request)
    query = request.query.get('q')
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
    query = request.query.get("s")
    if not query:
        return web.json_response({"error": "no query provided"})
    suggestions = await request.app["search"].suggest(
            query, request.app["fields"])
    return web.json_response({
        "results": [j.decode("utf8") for j in suggestions]
    })


def sonic_rest(app, search, fields=['tags', 'body'], root="/"):
    app["search"] = search
    app["fields"] = fields
    app.add_routes([
        web.get("%squery" % root, query),
        web.get("%ssuggest" % root, suggest),
    ])


if __name__ == '__main__':
    from .search import Search
    import os

    search = Search(os.getenv('SONIC_STORE', "/tmp/store"),
                    host=os.getenv('SONIC_HOST', '127.0.0.1'),
                    password=os.getenv('SONIC_PASSWORD')
                    )
    app = web.Application()
    sonic_rest(app, search)
    web.run_app(app)
