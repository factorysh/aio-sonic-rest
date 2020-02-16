from .ingest import Ingestor, split


def test_ingest():
    i = Ingestor(password="iuNg5Ri6daik2fe2Phoo6aig", path="./data/store/collection")
    i.ping()
    i.reset()
    documents = [
        dict(name="bob", body="Il fait beau et chaud.", tags=["beau", "chaud"]),
        dict(name="alice", body="Elle a mangé des carottes.", tags=["carotte"]),
    ]
    i.ingest(documents)


def test_split():
    groups = list(split("Je mange des carottes", 5))
    assert len(groups) == 5
    groups = list(split("Je mange des carottes", 2048))
    assert len(groups) == 1
