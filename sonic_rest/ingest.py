"""
Ingest stuff to sonic daemon.

It ingests an iterator of dictionnaries, stores some values, index others values.
"""
import re

from collection import CollectionSerializer

from sonic import IngestClient, ControlClient

NEWLINE = re.compile(r"\s+", re.MULTILINE)


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
        mkdir=True,
    ):
        self.address = address
        self.port = port
        self.password = password
        self.collection = CollectionSerializer(path)
        if mkdir:
            self.collection.mkdir()

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
                            ingestctl.push(self.site, k, str(n),
                                           NEWLINE.sub(" ", content),
                                           self.lang)
                        except Exception as e:
                            print(e, document)
            self.collection.close()

        with ControlClient(self.address, self.port, self.password) as controlcl:
            assert controlcl.ping()
            controlcl.trigger("consolidate")
