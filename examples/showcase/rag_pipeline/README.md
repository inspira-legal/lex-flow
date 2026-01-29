# RAG Pipeline with LexFlow

A complete Retrieval-Augmented Generation (RAG) pipeline built with LexFlow workflows, using Qdrant for vector storage and Google Vertex AI for embeddings and generation.

## Overview

This pipeline enables you to:

1. **Ingest PDFs** - Extract text, chunk it, generate embeddings, and store in Qdrant
2. **Search documents** - Find relevant passages using semantic similarity
3. **Ask questions** - Get AI-powered answers grounded in your documents (RAG)

## Architecture

```
                         INGESTION PIPELINE
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  PDFs   │───▶│ Extract │───▶│  Chunk  │───▶│  Embed  │───▶│ Qdrant  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                                  │
                                                                  ▼
                           QUERY PIPELINE                    ┌─────────┐
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    │ Vector  │
│  Query  │───▶│  Embed  │───▶│ Search  │◀───│ Context │◀───│  Store  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                   │
                                                   ▼
                              ┌─────────┐    ┌─────────┐
                              │   AI    │───▶│ Answer  │
                              │ (LLM)   │    │         │
                              └─────────┘    └─────────┘
```

## Prerequisites

### 1. Docker and Docker Compose

Install Docker and Docker Compose for running Qdrant:
- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

### 2. Google Cloud Platform Setup

This pipeline uses Vertex AI for embeddings and text generation.

1. Create or select a GCP project
2. Enable the Vertex AI API:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```
3. Authenticate:
   ```bash
   gcloud auth application-default login
   ```

### 3. Install LexFlow with RAG Dependencies

```bash
pip install lexflow[rag]
```

This installs:
- `qdrant-client` - Vector database client
- `pymupdf` - PDF text extraction
- `pydantic-ai` - AI model integration
- `google-cloud-aiplatform` - Vertex AI SDK

## Quick Start

### 1. Start Qdrant

```bash
cd examples/showcase/rag_pipeline
docker-compose up -d
```

Verify Qdrant is running:
```bash
curl http://localhost:6333/health
# Should return: {"status":"ok"}
```

### 2. Add Your Documents

Place your PDF files in the `documents/` directory:
```bash
cp /path/to/your/*.pdf ./documents/
```

### 3. Ingest Documents

```bash
lexflow ingest.yaml \
  --input pdf_dir=./documents \
  --input project=YOUR_GCP_PROJECT
```

### 4. Search Documents

```bash
lexflow search.yaml \
  --input query="What is the main topic?" \
  --input project=YOUR_GCP_PROJECT
```

### 5. Ask Questions (RAG)

```bash
lexflow ask.yaml \
  --input question="Explain the key concepts in these documents" \
  --input project=YOUR_GCP_PROJECT
```

## Workflows Reference

### `ingest.yaml` - Document Ingestion

Processes PDF files and stores them in the vector database.

**Inputs:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| `pdf_dir` | Directory containing PDF files | `./documents` |
| `project` | GCP project ID | (required) |
| `location` | GCP region | `us-central1` |
| `collection` | Qdrant collection name | `documents` |
| `chunk_size` | Characters per chunk | `1000` |
| `chunk_overlap` | Overlap between chunks | `200` |

**Example:**
```bash
lexflow ingest.yaml \
  --input pdf_dir=./documents \
  --input project=my-project \
  --input chunk_size=500 \
  --input chunk_overlap=100
```

### `search.yaml` - Semantic Search

Finds relevant document passages for a query.

**Inputs:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query | (required) |
| `project` | GCP project ID | (required) |
| `location` | GCP region | `us-central1` |
| `collection` | Qdrant collection name | `documents` |
| `top_k` | Number of results | `5` |

**Example:**
```bash
lexflow search.yaml \
  --input query="machine learning basics" \
  --input project=my-project \
  --input top_k=10
```

### `ask.yaml` - RAG Question Answering

Answers questions using retrieved context from your documents.

**Inputs:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| `question` | Question to answer | (required) |
| `project` | GCP project ID | (required) |
| `location` | GCP region | `us-central1` |
| `collection` | Qdrant collection name | `documents` |
| `top_k` | Context passages to retrieve | `5` |
| `model` | Vertex AI model | `gemini-1.5-flash` |

**Example:**
```bash
lexflow ask.yaml \
  --input question="What are the main conclusions?" \
  --input project=my-project \
  --input model=gemini-1.5-pro
```

## Configuration Options

### Chunking Strategy

Adjust chunk size and overlap based on your documents:

- **Small chunks (300-500 chars)**: Better for precise retrieval, FAQ-style content
- **Medium chunks (500-1000 chars)**: Good balance for most documents
- **Large chunks (1000-2000 chars)**: Better for complex topics needing more context

```bash
# Smaller chunks for FAQs
lexflow ingest.yaml --input chunk_size=400 --input chunk_overlap=50

# Larger chunks for technical documents
lexflow ingest.yaml --input chunk_size=1500 --input chunk_overlap=300
```

### Search Tuning

- **Low top_k (3-5)**: More focused, higher precision
- **High top_k (10-20)**: More comprehensive, higher recall

### Model Selection

Available Vertex AI models:
- `gemini-1.5-flash` - Fast, cost-effective (default)
- `gemini-1.5-pro` - More capable, better reasoning
- `gemini-1.0-pro` - Previous generation

## Troubleshooting

### Qdrant Connection Issues

**Error:** `Connection refused to localhost:6333`

1. Check if Qdrant is running:
   ```bash
   docker-compose ps
   ```

2. If not running, start it:
   ```bash
   docker-compose up -d
   ```

3. Check logs for errors:
   ```bash
   docker-compose logs qdrant
   ```

**Error:** `Collection not found`

Run the ingestion workflow first to create the collection:
```bash
lexflow ingest.yaml --input pdf_dir=./documents --input project=YOUR_PROJECT
```

### GCP Authentication Issues

**Error:** `Could not automatically determine credentials`

1. Run authentication:
   ```bash
   gcloud auth application-default login
   ```

2. Verify authentication:
   ```bash
   gcloud auth application-default print-access-token
   ```

**Error:** `Permission denied` or `403`

1. Check project ID is correct
2. Verify Vertex AI API is enabled:
   ```bash
   gcloud services list --enabled | grep aiplatform
   ```
3. Ensure your account has the `Vertex AI User` role

### Memory Issues with Large PDFs

**Error:** `MemoryError` or system becomes unresponsive

1. Process fewer PDFs at a time:
   ```bash
   # Move some PDFs to a separate folder temporarily
   mkdir ./documents/batch2
   mv ./documents/large_*.pdf ./documents/batch2/
   ```

2. Use smaller chunk sizes to reduce memory per document:
   ```bash
   lexflow ingest.yaml --input chunk_size=500 --input project=YOUR_PROJECT
   ```

3. Increase Docker memory limits in Docker Desktop settings

### PDF Extraction Issues

**Error:** `Unable to extract text from PDF`

Some PDFs may be scanned images without text. Options:
1. Use OCR to convert scanned PDFs to text first
2. Skip problematic PDFs and process others

**Error:** `Encrypted PDF`

Remove password protection from PDFs before processing.

## Stopping the Services

```bash
# Stop Qdrant (preserves data)
docker-compose stop

# Stop and remove containers (preserves data in volume)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

## Next Steps

- Customize the workflows for your specific use case
- Add preprocessing steps for document cleaning
- Implement hybrid search (keyword + semantic)
- Add metadata filtering for more precise retrieval
- Build a web interface using the LexFlow API
