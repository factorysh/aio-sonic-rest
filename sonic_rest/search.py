import json
from asyncio import ensure_future, gather

from asonic import Client
from asonic.enums import Channels

from .collection import CollectionReader


class Search:
    def __init__(self, store, host="127.0.0.1", port=1491, password=None, site="site"):
        self.client = Client(
            host=host, port=port, password=password, max_connections=100
        )
        self.site = site
        self.collection = CollectionReader(store)

    async def search_naked(self, query, fields):
        await self.client.channel(Channels.SEARCH.value)
        futures = dict()
        for field in fields:
            futures[field] = ensure_future(self.client.query(self.site, field, query))
        await gather(*futures.values())
        already = set()
        results = list()
        for field in fields:
            ids = [int(id) for id in futures[field].result() if int(id) not in already]
            if len(ids) == 0:
                continue
            already = already.union(ids)
            results += ids
        return len(results), (self.collection[id] for id in results)

    async def search(self, query, fields):
        size, results = await self.search_naked(query, fields)
        return size, (json.loads(r) for r in results)

    async def suggest(self, query, fields):
        await self.client.channel(Channels.SEARCH.value)
        futures = dict()
        for field in fields:
            futures[field] = ensure_future(
                self.client.suggest(self.site, field, query, 5)
            )
        await gather(*futures.values())
        already = set()
        suggestions = list()
        for field in fields:
            suggestions += [a for a in futures[field].result() if a not in already]
            already = already.union(suggestions)
        return suggestions
