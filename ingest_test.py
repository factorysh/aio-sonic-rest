from ingest import Ingestor


def test_ingest():
    documents = [
        dict(name="bob", body="Il fait beau et chaud."),
        dict(name="alice", body="Elle mange des carottes."),
    ]
    i = Ingestor(password="iuNg5Ri6daik2fe2Phoo6aig")
    i.ingest(documents)


if __name__ == '__main__':
    test_ingest()
