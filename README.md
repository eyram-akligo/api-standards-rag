# API Standards RAG Agent

This project builds a retrieval-augmented generation (RAG) service for API standards and technical documentation using NVIDIA models and a PostgreSQL pgvector database.

It is designed for use with American Petroleum Institute (API) standards, technical inspection documents, and related engineering references. The app loads PDF documents, splits them into manageable chunks, creates embeddings with NVIDIA embeddings, stores them in pgvector, and then answers questions by retrieving the most relevant text segments.

The project includes a FastAPI HTTP service and Docker Compose configuration for deployment.

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
- `api.py` – FastAPI service with `/health` and `/ask` endpoints
- `Dockerfile` – container definition for the API service
- `docker-compose.yml` – starts the API service and PostgreSQL pgvector database
- `.env.example` – safe template for local configuration values
- `data/` – folder for your local PDF documents
- `start-vector-db.ps1` – starts the Docker pgvector database container

## Requirements

- Docker Desktop
- NVIDIA API key
- API PDF documents in your local `data` folder

Python 3.12 is required only when running ingestion or the command-line agent outside Docker.

## Environment setup

Create and activate the virtual environment:

```powershell
python -m venv .venv

.venv\Scripts\Activate.ps1
```

Install required packages:

```powershell
python -m pip install -r requirements.txt
```

## NVIDIA setup

For local command-line usage, set your NVIDIA API key in the terminal before running the app:

```powershell
$env:NVIDIA_API_KEY = "your_nvidia_api_key_here"
```

For Docker Compose deployment, use `.env` as described in the deployment section below. The code uses the NVIDIA-hosted embedding and chat models configured in `config.py`.

## Database setup

This project expects a PostgreSQL database with the pgvector extension, running in Docker.

Start the database container:

```powershell
.\start-vector-db.ps1
```

The connection string is defined in `config.py` and is expected to match your local PostgreSQL setup:

```python
DB_CONNECTION_STRING = "postgresql+psycopg://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>"
```

If the local PostgreSQL service on your machine is already using port 5432, stop or disable it before starting the Docker database to avoid port conflicts.

## Data folder

This project expects your API PDFs to be placed in a local `data` folder inside the project root.

Example:

```text
<project_root>/
  data/
    API 650.pdf
    API 570.pdf
    API 653.pdf
```

This folder is intentionally local to your machine. The repository does not include the actual licensed PDFs.

Important: do not add proprietary PDF files to a public GitHub repository. This project assumes you will add your licensed documents locally and keep them out of source control.

The project is intentionally designed so that users can place their own purchased or licensed PDF documents in `data/` without committing them to Git.

If you clone this project and want to use it, place your own PDFs in `data/` before running `ingest.py`.

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

## Docker deployment

Create a local configuration file from the tracked template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and set the values below. Never commit this file.

```env
NVIDIA_API_KEY=your_nvidia_api_key
POSTGRES_PASSWORD=choose_a_long_unique_password
MODEL_NAME=nvidia/nvidia-nemotron-nano-9b-v2
EMBEDDING_MODEL=nvidia/nv-embedqa-e5-v5
CONNECTION_NAME=api_docs
RETRIEVAL_K=6
```

Build and start the API and database services:

```powershell
docker compose up --build -d
```

The API becomes available at `http://localhost:8000`.

Check that the service can reach PostgreSQL:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Ask a question:

```powershell
$body = @{ question = "What does API 570 require for piping inspection?" } | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/ask `
  -ContentType "application/json" `
  -Body $body
```

Interactive API documentation is at `http://localhost:8000/docs`.

The initial document ingestion must run in an environment with access to the local PDFs. Start PostgreSQL, then use the local Python environment:

```powershell
docker compose up -d postgres
.\rag_env\Scripts\Activate.ps1
$env:NVIDIA_API_KEY = "your_nvidia_api_key"
$env:DB_CONNECTION_STRING = "postgresql+psycopg://myuser:your_postgres_password@localhost:5432/ragdb"
python .\ingest.py
```

The Docker volume `pgvector-data` persists the embeddings across container restarts.

To inspect or stop the deployment:

```powershell
docker compose ps
docker compose logs -f api
docker compose down
```

## Production guidance

- Put the API behind HTTPS and add authentication before exposing `/ask` publicly.
- Store the NVIDIA key and database password in the deployment provider's secret manager.
- Back up the pgvector volume or use managed PostgreSQL with pgvector for durable production data.
- Restrict database network access to the API service.
- Keep proprietary documents in controlled storage and ingest only in a trusted environment.

## Notes about proprietary PDFs

The project is built around API standards that are often licensed or proprietary. Because of that, the PDF files themselves should not be committed to GitHub unless you have a repository policy or licensing arrangement that allows it.

The intended workflow is:

1. Purchase or legally obtain the documentation
2. Store the PDFs locally in the `data` folder
3. Run the ingestion script
4. Keep the raw PDF files out of version control
5. Share only the source code, not the proprietary standards themselves

This repository is meant to contain the application logic, not the purchased PDF documents.

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
