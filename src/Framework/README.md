
## Overview

RegulAItor is a comprehensive framework designed to process FDA warning letters and generate corrective action plans. The application leverages advanced language models and a multi-agent system to analyze warning letters, extract violations, retrieve relevant regulations, and generate detailed recommendations and corrective actions.

## Features

- **Multi-Agent System**: Utilizes a collection of specialized agents to handle different tasks in the processing pipeline.
- **Violation Extraction**: Extracts detailed regulatory violations from FDA warning letters.
- **Regulation Retrieval**: Provides full texts of specific regulations based on their citations.
- **Similarity Search**: Retrieves similar past violations using vector embeddings and a Qdrant vector database.
- **Recommendation Generation**: Generates recommendations to address each extracted violation.
- **Corrective Action Plan Drafting**: Drafts a comprehensive corrective action plan using a provided template.
- **Validation Agents**: Validates both the warning letter and the corrective action plan for compliance, accuracy, and completeness.
- **Web Interface**: Simple web interface for uploading warning letters and templates.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Agents](#agents)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Directory Structure

```
└── Framework
    ├── agents
    │   ├── __init__.py
    │   ├── agent_manager.py
    │   ├── conversation_workflow.py
    │   ├── corrective_action_agent.py
    │   ├── corrective_action_validation_agent.py
    │   ├── FDAWarningLetterValidator.py
    │   ├── input_validation_agent.py
    │   ├── recommendation_agent.py
    │   ├── regulation_content_agent.py
    │   ├── regulation_extraction_agent.py
    │   ├── similarity_search_agent.py
    │   ├── validation_agent.py
    │   └── violation_extraction_agent.py
    ├── data
    │   └── regulatoin_format
    │       └── main.py
    ├── RAG
    │   └── scripts
    │       ├── embed_data.py
    │       └── rag_agent.py
    ├── templates
    │   ├── index.html
    │   └── result.html
    ├── config.py
    ├── main.py
    ├── orchestrator.py
    ├── settings.py
    └── state_machine_controller.py
```

## Prerequisites

- **Python** 3.7 or higher
- **OpenAI API Key**: Required for language model interactions.
- **Qdrant Vector Database**: For similarity search functionality.
- **Virtual Environment** (recommended): To manage dependencies.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/regulAItor.git
cd regulAItor/Framework
```

### 2. Create a Virtual Environment

```bash
Follow the instructions to create your Environment
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the `Framework` directory with the following content:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

Replace `your_openai_api_key` with your actual OpenAI API key.

### 5. Set Up Qdrant Vector Database

- **Install Qdrant**: Follow the [Qdrant quick start guide](https://qdrant.tech/documentation/quick_start/).
- **Run Qdrant**: Ensure it's running on the host and port specified in your `.env` file.

### 6. Prepare Data for Similarity Search

Navigate to the `RAG/scripts` directory and run the data embedding script:

```bash
cd RAG/scripts
python embed_data.py
```

This script embeds violation data and uploads it to the Qdrant database.

### 7. Prepare Regulation Data

- **Obtain XML Files**: Get the XML versions of CFR Title 21 Parts 210 and 211.
- **Modify File Paths**: Update the file paths in `data/regulatoin_format/main.py` to point to your XML files.
- **Run the Script**: Parse and save regulations to JSON.

```bash
cd ../../data/regulatoin_format
python main.py
```

## Usage

### 1. Start the Application

From the `Framework` directory, run:

```bash
python main.py
```

This starts the Flask web application on `http://0.0.0.0:8000`.

### 2. Access the Web Interface

Open your web browser and navigate to `http://localhost:8000`.

### 3. Upload Files

- **Warning Letter**: Upload the FDA warning letter (supports `.txt`, `.pdf`, `.docx`).
- **Template**: Upload the corrective action plan template.

### 4. Process the Warning Letter

Click on **Process** to start the analysis. The application will:

- Validate the warning letter.
- Extract violations and recommendations.
- Retrieve relevant regulation texts.
- Perform similarity search for past cases.
- Generate recommendations.
- Draft a corrective action plan.
- Validate the corrective action plan for compliance.

### 5. View the Results

The generated corrective action plan will be displayed on the result page.

## Agents

The application utilizes a multi-agent system, with each agent performing a specific role:

- **InputValidationAgent**: Validates the uploaded warning letter.
- **ViolationExtractionAgent**: Extracts violations and recommendations from the warning letter.
- **ValidationAgent**: Validates extracted violations and recommendations against the original warning letter.
- **SimilaritySearchAgent**: Retrieves similar past violations for reference.
- **RegulationContentAgent**: Provides the full text of regulations based on citations.
- **RecommendationAgent**: Generates recommendations to address each violation.
- **CorrectiveActionAgent**: Drafts a corrective action plan using the provided template.
- **CorrectiveActionValidationAgent**: Validates the corrective action plan for compliance, accuracy, and completeness.
- **FDAWarningLetterValidator**: Ensures the warning letter meets FDA criteria.

## Architecture

### Main Components

- **Flask Server (`main.py`)**: Hosts the web interface and handles HTTP requests.
- **Agent Manager (`agents/agent_manager.py`)**: Manages agent instantiation and interactions.
- **Conversation Workflow (`agents/conversation_workflow.py`)**: Orchestrates the sequence of agent communications.
- **State Machine Controller (`state_machine_controller.py`)**: Controls state transitions during processing.

### Data Processing

- **Regulation Parsing (`data/regulatoin_format/main.py`)**: Parses XML files of regulations and saves them in JSON format.
- **Embedding Data (`RAG/scripts/embed_data.py`)**: Embeds violation data and uploads it to Qdrant for similarity search.

### Multi-Agent System

Agents communicate using the `GroupChat` and `GroupChatManager` classes, allowing for asynchronous and coordinated processing.

## Configuration

### Settings

- **Environment Variables (`.env`)**: API keys and service configurations.
- **Settings File (`settings.py`)**: Contains data classes for configuration.
- **Qdrant Config (`config.py`)**: Configurations for the Qdrant vector database.

### Adjusting Configurations

Modify the `.env` file and settings in `settings.py` and `config.py` to suit your environment and preferences.

## Logging

- **Logging Module**: Uses Python's built-in `logging` module.
- **Log File**: Runtime logs are saved to `runtime.log`.
- **Logging Levels**: Configured to `DEBUG` for detailed information.
