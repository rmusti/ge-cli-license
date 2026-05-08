# Gemini Enterprise CLI

This CLI tool allows you to interact with Google Cloud Discovery Engine (Vertex AI Agent Builder) to list engines and agents, and retrieve detailed agent configurations.

## Features

-   List all engines (apps) in a project.
-   List all agents within a specific engine.
-   Get the detailed JSON configuration of a specific agent.
-   Uses Application Default Credentials (ADC).
-   Supports configuration via `.env` file.

## Prerequisites

-   Python 3
-   `gcloud` CLI installed and authenticated.
-   Discovery Engine API enabled in your GCP project.

## Setup

1.  **Clone or copy the files** to your working directory.
2.  **Create a virtual environment** and install dependencies:
    ```bash
    python3 -m venv venv
    ./venv/bin/pip install requests google-auth python-dotenv
    ```
3.  **Configure Environment Variables**:
    Create a `.env` file in the same directory and set your Project ID and default Engine ID:
    ```env
    PROJECT_ID=your-gcp-project-id
    ENGINE_ID=your-default-engine-id
    ```

## Authentication & Quota Project

This tool uses Application Default Credentials (ADC). To authenticate, run:
```bash
gcloud auth application-default login
```

The Discovery Engine API requires a quota project for billing. You can set it globally for ADC:
```bash
gcloud auth application-default set-quota-project your-gcp-project-id
```
Alternatively, you can pass it via the `--quota-project` flag to the script.

## Usage

You can use the shell script wrapper `ge_cli.sh` or call the Python script directly from the virtual environment.

### 1. List Engines

Lists all engines in the project specified in `.env`.

Using shell script:
```bash
./ge_cli.sh
```
or
```bash
./ge_cli.sh engines
```

Using Python directly:
```bash
./venv/bin/python ge_cli.py engines
```

### 2. List Agents in an Engine

Lists all agents within a specific engine. If `ENGINE_ID` is set in `.env`, it will be used as default.

Using shell script:
```bash
./ge_cli.sh agents list
```

Using Python directly:
```bash
./venv/bin/python ge_cli.py agents list
```

Or override engine:
```bash
./ge_cli.sh agents list --engine YOUR_ENGINE_ID
```

### 3. Get Detailed Agent Configuration

Retrieves the detailed JSON configuration of a specific agent.

Using shell script:
```bash
./ge_cli.sh agents get YOUR_AGENT_ID
```

Using Python directly:
```bash
./venv/bin/python ge_cli.py agents get YOUR_AGENT_ID
```

### 4. Get Agent IAM Policy

Retrieves the IAM policy of a specific agent (experimental).

Using shell script:
```bash
./ge_cli.sh agents get-iam YOUR_AGENT_ID
```

Using Python directly:
```bash
./venv/bin/python ge_cli.py agents get-iam YOUR_AGENT_ID
```

## Datastores Commands

### 1. List Datastores

Lists all datastores in the project specified in `.env`.

Using shell script:
```bash
./ge_cli.sh datastores list
```

Using Python directly:
```bash
./venv/bin/python ge_cli.py datastores list
```

### 2. Get Datastore Details

Retrieves the detailed JSON configuration of a specific datastore.

Using shell script:
```bash
./ge_cli.sh datastores get YOUR_DATASTORE_ID
```

Using Python directly:
```bash
./venv/bin/python ge_cli.py datastores get YOUR_DATASTORE_ID
```

## Options

-   `--project`: Override the GCP Project ID.
-   `--location`: Set the location (default: `global`).
-   `--collection`: Set the collection (default: `default_collection`).
-   `--quota-project`: Set the quota project for billing.
-   `--assistant`: Set the assistant ID (default: `default_assistant`).
