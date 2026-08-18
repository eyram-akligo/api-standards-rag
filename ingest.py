import os

from langchain_postgres import PGVector
from config import DB_CONNECTION_STRING, CONNECTION_NAME
from database import get_embedder, load_and_split_documents


def main():
    if not os.getenv("NVIDIA_API_KEY"):
        raise RuntimeError(
            "NVIDIA_API_KEY is not set in this terminal. Set it before running ingest.py."
        )

    docs = load_and_split_documents()
    print(f"Loaded {len(docs)} chunks from ./data")

    PGVector.from_documents(
        documents=docs,
        embedding=get_embedder(),
        collection_name=CONNECTION_NAME,
        connection=DB_CONNECTION_STRING,
        use_jsonb=True
    )
    print(f"Embeddings stored in pgvector collection '{CONNECTION_NAME}'.")


if __name__ == "__main__":
    main()
