import os

from dotenv import load_dotenv


load_dotenv()


MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nvidia-nemotron-nano-9b-v2")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nvidia/nv-embedqa-e5-v5")

CHUNK_SIZE =  int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", 6))

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", "postgresql+psycopg://myuser:admin@localhost:5432/ragdb")
CONNECTION_NAME = os.getenv("CONNECTION_NAME", "api_docs")

DATA_DIR = os.getenv("DATA_DIR", "./data")
