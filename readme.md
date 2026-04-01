# food-diary-rag

RAG-based system for querying nutrition notes with semantic search and structured calculations.

## About the Project

`food-diary-rag` is a learning MVP project for working with daily nutrition notes.

The goal of the project is to:
- read nutrition notes from a local directory
- extract structured daily records from raw text
- store both note text and nutrition values separately
- generate embeddings for future semantic search
- prepare the foundation for a future RAG pipeline

At the current stage, the project already supports:
- loading `.md` notes from a directory
- parsing daily note records
- basic data validation
- saving processed records to JSON
- generating embeddings through the OpenAI API
- saving records together with embeddings

## Current Status

The current version includes:
- ingestion pipeline
- parsing and validation
- embedding generation

Not implemented yet:
- vector database
- query pipeline
- numeric query processing
- semantic retrieval
- response generation

## Project Structure

```text
food-diary-rag/
├─ config/
│  └─ settings.py
├─ data/
│  ├─ raw/
│  │  ├─ 2026-03-24.md
│  │  ├─ 2026-03-25.md
│  │  ├─ 2026-03-26.md
│  │  ├─ 2026-03-27.md
│  │  ├─ 2026-03-28.md
│  │  ├─ 2026-03-29.md
│  │  └─ 2026-03-30.md
│  └─ processed/
│     ├─ parsed_records.json
│     └─ records_with_embeddings.json
├─ scripts/
│  ├─ ingest_notes.py
│  └─ generate_embeddings.py
├─ src/
│  ├─ embeddings/
│  │  └─ embedder.py
│  ├─ ingestion/
│  │  ├─ file_loader.py
│  │  ├─ note_parser.py
│  │  └─ validator.py
│  └─ services/
│     ├─ embedding_service.py
│     └─ ingest_service.py
├─ .env.example
├─ .gitignore
├─ LICENSE
├─ pyproject.toml
└─ README.md
````

## Data Format

The project currently follows this approach:

* one note = one day
* one record contains:

  * `id`
  * `date`
  * `text`
  * `calories`
  * `protein`
  * `fat`
  * `carbs`

After embedding generation, each record is extended with:

* `embedding`

## Requirements

* Python 3.11+
* OpenAI API key

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install the project and dependencies:

```bash
pip install -e .
```

If `pyproject.toml` already includes the OpenAI dependency, the block should look like this:

```toml
dependencies = [
    "openai==2.30.0",
]
```

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
OPENAI_API_KEY=your_api_key_here
```

## Running the Ingestion Step

This step:

* reads notes from `data/raw`
* parses them
* validates them
* saves the result to `data/processed/parsed_records.json`

Command:

```bash
python scripts/ingest_notes.py
```

Expected result:

* `data/processed/parsed_records.json` is created

## Running the Embedding Step

This step:

* reads `parsed_records.json`
* creates embeddings for the `text` field
* saves the result to `data/processed/records_with_embeddings.json`

Command:

```bash
python scripts/generate_embeddings.py
```

Expected result:

* `data/processed/records_with_embeddings.json` is created

## Current Pipeline

### 1. Ingestion

* read files from `data/raw`
* extract date from the filename
* parse the raw note text
* extract calories, protein, fat, and carbs
* validate required fields

### 2. Embeddings

* read processed records
* prepare text for embedding
* call the OpenAI Embeddings API
* save records together with embedding vectors

## Example Workflow

1. Put daily nutrition notes into `data/raw`
2. Run the ingestion script
3. Check `parsed_records.json`
4. Add `OPENAI_API_KEY` to `.env`
5. Run the embedding generation script
6. Check `records_with_embeddings.json`

## Current Limitations

* the project is currently designed for a small local dataset
* parsing assumes a predictable note format
* embeddings are generated only for valid records
* vector search and user query handling are not implemented yet

## Next Steps

Planned improvements:

* connect a vector database
* add a storage layer
* implement numeric query processing
* implement semantic search
* build a hybrid query pipeline
* add response generation

## License

MIT
