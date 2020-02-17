import json

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
        already = set()
        for field in fields:
            r = await self.client.query(self.site, field, query,)
            ids = [int(id) for id in r if int(id) not in already]
            if len(ids) == 0:
                continue
            already = already.union(ids)
            for i, id in enumerate(ids):
                # yield raw document, is the last element of the list ?
                yield self.collection[id], i + 1 < len(ids)

    async def search(self, query, fields):
        async for r in self.search_naked(query, fields):
            yield json.loads(r[0])
