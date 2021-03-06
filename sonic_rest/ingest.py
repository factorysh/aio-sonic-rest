"""
Ingest stuff to sonic daemon.

It ingests an iterator of dictionnaries, stores some values,
index others values.
"""
import re

from .collection import CollectionSerializer

from sonic import IngestClient, ControlClient


class Ingestor:
    site = "site"

    def __init__(
        self,
        model,
        address="127.0.0.1",
        port=1491,
        password=None,
        path="./data/kv",
        lang="fra",
    ):
        self.lang = lang
        self.address = address
        self.port = port
        self.password = password
        self.collection = CollectionSerializer(path)
        self.stored = set(k for k, v in model.items() if v.get('stored'))
        self.indexed = set(k for k, v in model.items() if v.get('indexed'))
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
            for n, document in enumerate(documents):
                d = dict()
                for k in self.stored:
                    d[k] = document.get(k)
                self.collection.append(d)
                for k in self.indexed:
                    content = document.get(k)
                    if content is not None:
                        if isinstance(content, list):
                            content = " ".join(content)
                        content = content.translate(self.translate)
                        for chunk in split(content, 2048):
                            try:
                                p = ingestctl.push(
                                    self.site, k, str(n), chunk, self.lang
                                )
                                if not p:
                                    print("Oups: %s" % chunk)
                            except Exception as e:
                                self.collection.close()
                                raise
        self.collection.flush()
        with ControlClient(self.address, self.port, self.password) as ctl:
            assert ctl.ping()
            ctl.trigger("consolidate")


def split(txt: str, size: int = 1024):
    "split a text in chunks"
    poz = 0
    while poz < len(txt):
        chunk = txt[poz: poz + size]
        if len(chunk) < size:  # last token
            yield chunk
            return
        if txt[poz + size - 1] != " " and txt[poz + size] != " ":
            x = chunk.rfind(" ")
            if x == 0:
                poz += 1
                continue
            if x != -1:  # there is a space to split
                poz += x
                yield chunk[:x]
                continue
        poz += size
        yield chunk


def trans():
    return str.maketrans(dict((a, " ") for a in "[]{}(),?!;.:\n\r\t`'\"=><#|"))
