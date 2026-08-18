# API Standards RAG Agent

This project builds a retrieval-augmented generation (RAG) agent for API standards and technical documentation using NVIDIA models and a PostgreSQL pgvector database.

It is designed for use with American Petroleum Institute (API) standards, technical inspection documents, and related engineering references. The app loads PDF documents, splits them into manageable chunks, creates embeddings with NVIDIA embeddings, stores them in pgvector, and then answers questions by retrieving the most relevant text segments.

## What this project does

- Reads PDF files from a local `data` folder
- Splits long documents into smaller chunks
- Creates vector embeddings using NVIDIA embedding models
- Stores those embeddings in PostgreSQL with the pgvector extension
- Uses a chat model to answer questions using the retrieved context
- Lets you ask questions about API standards and inspection guidance

## Project structure

- `config.py` – project settings such as model names, chunk size, and database connection string
- `database.py` – document loading, chunking, embedding, and retrieval logic
- `ingest.py` – loads PDFs, creates embeddings, and stores them in pgvector
- `main.py` – runs the agent and asks a question
- `tools.py` – wraps the retrieval system as a tool for the agent
- `data/` – folder for your local PDF documents
- `start-vector-db.ps1` – starts the Docker pgvector database container
- `rag_env/` – local Python environment for the project

## Requirements

- Python 3.12
- Docker Desktop
- NVIDIA API key
- A running PostgreSQL pgvector container
- API PDF documents in your local `data` folder

## Environment setup

From the project root, activate the virtual environment:

```powershell
.\rag_env\Scripts\Activate.ps1
```

Install any required packages if needed:

```powershell
python -m pip install -r requirements.txt
```

If you do not yet have a `requirements.txt`, create one from your environment:

```powershell
python -m pip freeze > requirements.txt
```

## NVIDIA setup

Set your NVIDIA API key in the terminal before running the app:

```powershell
$env:NVIDIA_API_KEY = "your_nvidia_api_key_here"
```

The code uses the NVIDIA-hosted embedding and chat models configured in `config.py`.

## Database setup

This project expects a PostgreSQL database with the pgvector extension, running in Docker.

Start the database container:

```powershell
.\start-vector-db.ps1
```

The connection string is defined in `config.py` and is expected to match your local PostgreSQL setup:

```python
DB_CONNECTION_STRING = "postgresql+psycopg://myuser:admin@localhost:5432/ragdb"
```

If the local PostgreSQL service on your machine is already using port 5432, stop or disable it before starting the Docker database to avoid port conflicts.

## Data folder

This project expects your API PDFs to be placed in a local `data` folder inside the project root.

Example:

```text
api_rag/
  data/
    API 650.pdf
    API 570.pdf
    API 653.pdf
```

Important: do not add proprietary PDF files to a public GitHub repository. This project assumes you will add your licensed documents locally and keep them out of source control.

The project is intentionally designed so that users can place their own purchased or licensed PDF documents in `data/` without committing them to Git.

## Ingesting the documents

Once your PDFs are in `data/`, run:

```powershell
python .\ingest.py
```

The script does the following:

- loads all PDF files from `data/`
- chunks the content into smaller sections
- creates embeddings with the NVIDIA embedding model
- stores the vectors in the pgvector database

Note: some PDFs may be encrypted or protected by proprietary DRM. Those files will be skipped when they cannot be read by the PDF loader. If you later obtain passwords or accessible copies for those files, you can add them and rerun the ingestion step.

## Running the agent

After the documents have been ingested, run:

```powershell
python .\main.py
```

The app will create a retrieval tool and ask a question about the API standards stored in the database.

## Notes about proprietary PDFs

The project is built around API standards that are often licensed or proprietary. Because of that, the PDF files themselves should not be committed to GitHub unless you have a repository policy or licensing arrangement that allows it.

The intended workflow is:

1. Purchase or legally obtain the documentation
2. Store the PDFs locally in the `data` folder
3. Run the ingestion script
4. Keep the raw PDF files out of version control

## Typical workflow

```powershell
.\rag_env\Scripts\Activate.ps1
$env:NVIDIA_API_KEY = "your_nvidia_api_key_here"
.\start-vector-db.ps1
python .\ingest.py
python .\main.py
```

## Future improvements

These are good next steps for the project:

- add an interactive question loop
- return source and page metadata with answers
- improve retrieval by adjusting chunk size and retrieval count
- add better handling for proprietary or encrypted PDFs
- add a cleanup script for resetting the vector collection
- create a more polished front end or API layer

## License

This project is for local research and engineering use. It does not include any proprietary API standards documents. Those must be obtained separately and stored locally in the `data` folder.
