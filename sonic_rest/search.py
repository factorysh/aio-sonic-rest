import json
from asyncio import ensure_future, gather

from asonic import Client
from asonic.enums import Channel

from .collection import CollectionReader


class Search:
    def __init__(self, store,
                 host="127.0.0.1", port=1491, password=None,
                 site="site"):
        self.client = Client(
            host=host, port=port, password=password, max_connections=100
        )
        self.site = site
        self.store = store
        self.collection = CollectionReader(self.store)
        self.channel = None

    async def set_search_channel(self):
        if self.channel is None:
            await self.client.channel(Channel.SEARCH)
            self.channel = True

    async def search_naked(self, query, fields):
        await self.set_search_channel()
        futures = {
            field: ensure_future(self.client.query(self.site, field, query))
            for field in fields
        }
        await gather(*futures.values())
        results = list()
        for field in fields:
            results.extend([
                int(id) for id in futures[field].result()
                if int(id) not in results
            ])
        r = [self.collection[id] for id in results]
        return len(results), r

    async def search(self, query, fields):
        size, results = await self.search_naked(query, fields)
        return size, (json.loads(r) for r in results)

    async def suggest(self, query, fields):
        await self.set_search_channel()
        futures = dict()
        futures = {
            field: ensure_future(
                self.client.suggest(self.site, field, query, 5))
            for field in fields
        }
        await gather(*futures.values())
        suggestions = list()
        for field in fields:
            suggestions.extend([
                a for a in futures[field].result()
                if a not in suggestions
            ])
        return suggestions
