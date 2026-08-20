import os
import hashlib
from pathlib import Path

from langchain_postgres import PGVector
from sqlalchemy import create_engine, text
from config import DB_CONNECTION_STRING, CONNECTION_NAME
from database import get_embedder, load_and_split_documents


EMBEDDING_BATCH_SIZE = 50
DATABASE_BATCH_SIZE = 100


def normalize_source(source):
    return Path(source).name.lower()


def get_chunk_id(document):
    source = normalize_source(document.metadata.get("source", ""))
    page = document.metadata.get("page", "")
    value = f"{source}|{page}|{document.page_content}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def get_indexed_sources():
    engine = create_engine(DB_CONNECTION_STRING)
    query = text(
        """
        SELECT DISTINCT e.cmetadata->>'source'
        FROM langchain_pg_embedding AS e
        JOIN langchain_pg_collection AS c ON e.collection_id = c.uuid
        WHERE c.name = :collection_name
        """
    )

    try:
        with engine.connect() as connection:
            rows = connection.execute(
                query, {"collection_name": CONNECTION_NAME}
            )
            return {
                normalize_source(row[0])
                for row in rows
                if row[0]
            }
    except Exception as error:
        if "does not exist" in str(error):
            return set()
        raise


def main():
    if not os.getenv("NVIDIA_API_KEY"):
        raise RuntimeError(
            "NVIDIA_API_KEY is not set in this terminal. Set it before running ingest.py."
        )

    docs = load_and_split_documents()
    indexed_sources = get_indexed_sources()
    new_docs = [
        document
        for document in docs
        if normalize_source(document.metadata.get("source", ""))
        not in indexed_sources
    ]

    print(f"Loaded {len(docs)} chunks from ./data")
    print(f"Skipping {len(docs) - len(new_docs)} chunks from already-indexed documents")

    if not new_docs:
        print("No new documents to ingest.")
        return

    embedder = get_embedder()
    vector_store = PGVector(
        embeddings=embedder,
        collection_name=CONNECTION_NAME,
        connection=DB_CONNECTION_STRING,
        use_jsonb=True,
    )

    for start in range(0, len(new_docs), EMBEDDING_BATCH_SIZE):
        embedding_batch = new_docs[start:start + EMBEDDING_BATCH_SIZE]
        embeddings = embedder.embed_documents(
            [document.page_content for document in embedding_batch]
        )

        for database_start in range(0, len(embedding_batch), DATABASE_BATCH_SIZE):
            database_batch = embedding_batch[
                database_start:database_start + DATABASE_BATCH_SIZE
            ]
            batch_embeddings = embeddings[
                database_start:database_start + DATABASE_BATCH_SIZE
            ]
            vector_store.add_embeddings(
                texts=[document.page_content for document in database_batch],
                embeddings=batch_embeddings,
                metadatas=[document.metadata for document in database_batch],
                ids=[get_chunk_id(document) for document in database_batch],
            )

        processed = min(start + EMBEDDING_BATCH_SIZE, len(new_docs))
        print(f"Processed {processed}/{len(new_docs)} new chunks")

    print(f"Embeddings stored in pgvector collection '{CONNECTION_NAME}'.")


if __name__ == "__main__":
    main()
