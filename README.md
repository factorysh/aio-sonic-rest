AIO Sonic REST
==============

REST API for [Sonic](https://github.com/valeriansaliou/sonic) daemon.

It uses aiohttp, and documents are stored raw, read with mmap.
It's fast and doesn't eat all your memory.

Usage
-----

Index

```python
i = Ingestor(
    dict(
        name=dict(stored=True),
        body=dict(indexed=True),
        tags=dict(stored=True, indexed=True,),
    ),
    password="iuNg5Ri6daik2fe2Phoo6aig",
    path="./data/store/collection",
)
i.reset()
documents = [
    dict(name="alice", body="Elle a mangé des carottes.", tags=["carotte"]),
    dict(name="bob", body="Il fait du Django.", tags=["python", "django"]),
    dict(name="charly", body="Il a un python dans son vivarium.", tags=[]),
]
i.ingest(documents)
```

Search

```python
s = Search("./data/store/collection", password="iuNg5Ri6daik2fe2Phoo6aig")
size, results = await s.search("python", ["tags", "body"])
```

Rest it
```python
app = web.Application()
sonic_rest(app, s)
```

Query it
```python
resp = await client.get("/query?q=python")
resp = await client.get("/suggest?s=car")
```

All this code are in test files.

Tests
-----

Start the sonic daemon

    docker-compose up -d

Run tests

    pytest


Or, simpler:

    make test

Licence
-------

3 terms BSD licence, ©2019 Mathieu Lecarme
