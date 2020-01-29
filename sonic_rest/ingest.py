"""
Ingest stuff to sonic daemon.

It ingests an iterator of dictionnaries, stores some values,
index others values.
"""
import re

from .collection import CollectionSerializer

from sonic import IngestClient, ControlClient
from sonic.client import quote_text


class Ingestor:
    indexed = ["body"]
    stored = ["name"]
    site = "site"
    lang = "fra"

    def __init__(
        self,
        address="127.0.0.1",
        port=1491,
        password=None,
        path="./data/kv",
    ):
        self.address = address
        self.port = port
        self.password = password
        self.collection = CollectionSerializer(path)

    def reset(self):
        with IngestClient(self.address, self.port, self.password) as ingestctl:
            assert ingestctl.ping()
            ingestctl.flush_collection(self.site)
        self.collection.reset()

    def close(self):
        self.collection.close()

    def ping(self):
        with IngestClient(self.address, self.port, self.password) as ingestctl:
            assert ingestctl.ping()

    def ingest(self, documents):
        with IngestClient(self.address, self.port, self.password) as ingestctl:
            assert ingestctl.ping()
            n = 0
            for document in documents:
                d = dict()
                for k in self.stored:
                    d[k] = document.get(k)
                self.collection.append(d)
                for k in self.indexed:
                    content = document.get(k)
                    if content is not None:
                        try:
                            p = ingestctl.push(
                                self.site, k, str(n),
                                quote_text(content),
                                self.lang)
                            if not p:
                                print("Oups: %s" % quote_text(content))
                        except Exception:
                            self.collection.close()
                            raise
                        else:
                            n += 1

        with ControlClient(self.address, self.port, self.password) as ctl:
            assert ctl.ping()
            ctl.trigger("consolidate")
