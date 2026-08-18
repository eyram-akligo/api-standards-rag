from langchain_postgres import PGVector
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import (
    EMBEDDING_MODEL, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    DB_CONNECTION_STRING, 
    CONNECTION_NAME, 
    RETRIEVAL_K
)


def get_embedder():
    return NVIDIAEmbeddings(model=EMBEDDING_MODEL)


def load_and_split_documents(directory_path="./data"):
    # Load PDF documents from the specified directory (skip unreadable/encrypted files)
    loader = DirectoryLoader(directory_path, glob="**/*.pdf",
                             loader_cls=PyPDFLoader, silent_errors=True)
    raw_docs = loader.load()

    # Chunk the data (raw_docs are already Document objects, so split them directly)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return text_splitter.split_documents(raw_docs)


def get_vector_store():
    # Connect to the existing PGVector collection without re-ingesting documents
    return PGVector(
        embeddings=get_embedder(),
        collection_name=CONNECTION_NAME,
        connection=DB_CONNECTION_STRING,
        use_jsonb=True
    )


def get_retriever():
    return get_vector_store().as_retriever(
        search_kwargs={"k": RETRIEVAL_K}
    )