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
        self.translate = trans()

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
                        content = content.translate(self.translate)
                        for chunk in split(content, 2048):
                            try:
                                p = ingestctl.push(
                                    self.site, k, str(n),
                                    chunk,
                                    self.lang)
                                if not p:
                                    print("Oups: %s" % chunk)
                            except Exception as e:
                                self.collection.close()
                                raise
                        n += 1

        with ControlClient(self.address, self.port, self.password) as ctl:
            assert ctl.ping()
            ctl.trigger("consolidate")


def split(txt: str, size:int=1024):
    "split a text in chunks"
    poz = 0
    while poz < len(txt):
        chunk = txt[poz:poz+size]
        if len(chunk) < size:
            yield chunk
            return
        if txt[poz+size-1] != " " and txt[poz+size] != " ":
            x = chunk.rfind(" ")
            if x != -1:
                poz += x
                yield chunk[:x]
                continue
        poz += size
        yield chunk


def trans():
    return str.maketrans(dict(
        (a, " ") for a in "[]{}(),?!;.:\n\r\t`'\"=><#|"))
