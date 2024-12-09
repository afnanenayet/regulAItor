# Compliance Assistant

## Overview
A compliance assistant that uses Qdrant vector database, sentence embeddings, and OpenAI's GPT model to provide compliance recommendations according to the input violated term from FDA warning letter.

## Prerequisites
- Use UV as the package manager


## Configuration
Create a `.env` file in the `root` directory:
```
QDRANT_HOST=localhost
QDRANT_PORT=6333
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

## Data Preparation
1. Add `violations_data.json` to the `Framework/RAG/data` directory

2. Start Qdrant (optional, via Docker):
```bash
docker run -p 6333:6333 qdrant/qdrant
```

3. Run data preparation script:
```bash
python scripts/prepare_data.py
```

## Running the Assistant
Run the assistant:
```bash
python scripts/run_agent.py
```

## Usage
Enter compliance-related queries when prompted. The assistant will retrieve and provide violated terms and recommendations.

## Troubleshooting
- Verify OpenAI API key
- Check Qdrant connection
- Ensure `violations_data.json` is correctly formatted
- Verify all packages are installed