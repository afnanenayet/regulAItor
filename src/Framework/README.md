# RegulAItor

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
- **Web Interfaces**: Offers both Flask and Streamlit web interfaces for user interaction.

## Table of Contents

- [RegulAItor](#regulaitor)
  - [Overview](#overview)
  - [Features](#features)
  - [Table of Contents](#table-of-contents)
  - [Directory Structure](#directory-structure)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create a Virtual Environment](#2-create-a-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Set Up Environment Variables](#4-set-up-environment-variables)
    - [5. Set Up Qdrant Vector Database](#5-set-up-qdrant-vector-database)
    - [6. Prepare Data for Similarity Search](#6-prepare-data-for-similarity-search)
    - [7. Prepare Regulation Data](#7-prepare-regulation-data)
  - [Usage](#usage)
    - [Running with `main.py` (Flask Web Application)](#running-with-mainpy-flask-web-application)
    - [Running with `main_1.py` (Command-Line Interface)](#running-with-main_1py-command-line-interface)
    - [Running with `main_streamlit.py` (Streamlit Web Application)](#running-with-main_streamlitpy-streamlit-web-application)
  - [Agents](#agents)
  - [Architecture](#architecture)
    - [Main Components](#main-components)
    - [Data Processing](#data-processing)
    - [Multi-Agent System](#multi-agent-system)
  - [Configuration](#configuration)
    - [Settings](#settings)
    - [Adjusting Configurations](#adjusting-configurations)
  - [Logging](#logging)

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
    │   ├── Initiating_agent.py
    │   ├── input_validation_agent.py
    │   ├── recommendation_agent.py
    │   ├── regulation_content_agent.py
    │   ├── regulation_extraction_agent.py
    │   ├── similar_case_agent.py
    │   ├── similarity_search_agent.py
    │   ├── validation_agent.py
    │   └── violation_extraction_agent.py
    ├── data
    │   ├── regulatoin_format
    │   │   └── main.py
    │   └── full_regulations.json
    ├── RAG
    │   └── scripts
    │       ├── embed_data.py
    │       └── rag_agent.py
    ├── templates
    │   ├── index.html
    │   ├── result.html
    │   └── reupload.html
    ├── config.py
    ├── main.py
    ├── main_1.py
    ├── main_streamlit.py
    ├── orchestrator.py
    ├── README.md
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
git clone https://github.com/yourusername/RegulAItor.git
cd RegulAItor/Framework
```

### 2. Create a Virtual Environment

```bash
uv venv
source .venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
```

### 3. Install Dependencies

```bash
UV sync
```

### 4. Set Up Environment Variables

Create a `.env` file in the `root` directory with the following content:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
QDRANT_HOST=localhost
QDRANT_PORT=6333
OPENAI_MODEL_Corrective_Action_Model=gpt-4o
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

This will create `full_regulations.json` in the `data` directory.

## Usage

The application can be run in different modes depending on your preference:

### Running with `main.py` (Flask Web Application)

This mode runs a Flask web application that provides a web interface to upload files and process them.

1. **Start the Application**

   From the `Framework` directory, run:

   ```bash
   python main.py
   ```

   This starts the Flask web application on `http://0.0.0.0:8000`.

2. **Access the Web Interface**

   Open your web browser and navigate to `http://localhost:8000`.

3. **Upload Files**

   - **Warning Letter**: Upload the FDA warning letter (supports `.txt`, `.pdf`, `.docx`).
   - **Template**: Upload the corrective action plan template.

4. **Process the Warning Letter**

   Click on **Process** to start the analysis. The application will:

   - Validate the warning letter and template.
   - Extract violations and recommendations.
   - Retrieve relevant regulation texts.
   - Perform similarity search for past cases.
   - Generate recommendations.
   - Draft a corrective action plan.
   - Validate the corrective action plan for compliance.

5. **View the Results**

   The generated corrective action plan will be displayed on the result page.

### Running with `main_1.py` (Command-Line Interface)

This mode runs the application via command line, suitable for integration into scripts or for users comfortable with terminal operations.

1. **Modify Input**

   Edit `main_1.py` and replace the `warning_letter` and `template` variables with your own content.

2. **Start the Application**

   From the `Framework` directory, run:

   ```bash
   python main_1.py
   ```

3. **View the Results**

   The results will be printed to the console or handled as per the script's implementation.

### Running with `main_streamlit.py` (Streamlit Web Application)

This mode provides an alternative web interface using Streamlit, which can be more interactive and easier to use.

1. **Install Streamlit (if not already installed)**

   ```bash
   pip install streamlit
   ```

2. **Start the Streamlit Application**

   From the `Framework` directory, run:

   ```bash
   streamlit run main_streamlit.py
   ```

3. **Access the Streamlit Interface**

   The script will provide a local URL (usually `http://localhost:8501`) where you can access the application.

4. **Upload Files**

   - **Warning Letter**: Upload the FDA warning letter (supports `.txt`, `.pdf`, `.docx`).
   - **Template**: Upload the corrective action plan template.

5. **Process the Warning Letter**

   Click on **Start Processing** to begin. The application will:

   - Validate the warning letter and template.
   - Extract violations and recommendations.
   - Retrieve relevant regulation texts.
   - Perform similarity search for past cases.
   - Generate recommendations.
   - Draft a corrective action plan.
   - Validate the corrective action plan for compliance.

6. **View and Download the Results**

   The application will display the corrective action plan and provide an option to download it as a Word document.

## Agents

The application utilizes a multi-agent system, with each agent performing a specific role:

- **InitiatingAgent**: Starts the conversation workflow upon receiving the warning letter and template.
- **InputValidationAgent**: Validates the uploaded warning letter and template.
- **ViolationExtractionAgent**: Extracts violations and recommendations from the warning letter.
- **ValidationAgent**: Validates extracted violations and recommendations against the original warning letter.
- **SimilaritySearchAgent**: Retrieves similar past violations for reference.
- **SimilarCaseAgent**: Filters and extracts recommendations from similar cases.
- **RegulationContentAgent**: Provides the full text of regulations based on citations.
- **RecommendationAgent**: Generates recommendations to address each violation.
- **CorrectiveActionAgent**: Drafts a corrective action plan using the provided template.
- **CorrectiveActionValidationAgent**: Validates the corrective action plan for compliance, accuracy, and completeness.
- **FDAWarningLetterValidator**: Ensures the warning letter meets FDA criteria.

## Architecture

### Main Components

- **Flask Server (`main.py`)**: Hosts the web interface and handles HTTP requests.
- **Streamlit App (`main_streamlit.py`)**: Provides an alternative interface using Streamlit.
- **Command-Line Interface (`main_1.py`)**: Allows running the application via the terminal.
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

- **Logging Module**: Uses:
    -  from autogen import runtime_logging

      log_file_path = "autogen_logs/runtime.log"
      if os.path.exists(log_file_path):
          os.remove(log_file_path)


      logging_session_id = runtime_logging.start(logger_type="file", config={"filename": "runtime.log"})


      runtime_logging.stop()


