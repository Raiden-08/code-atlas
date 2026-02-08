# Code Atlas

![Status](https://img.shields.io/badge/status-alpha-orange)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**A local, offline RAG (Retrieval-Augmented Generation) tool for querying codebases using natural language.**

---

## Overview

**Code Atlas** is a developer productivity tool designed to enable semantic search across local repositories. Unlike traditional `grep` or IDE search tools which rely on exact keyword matching, I tried to use **Abstract Syntax Trees (ASTs)** to parse code structure and **Vector Embeddings** to understand intent.

allowing us to query codebases using natural language queries and receive context aware results, even if the specific keywords do not appear in the source code.

to help understand both structural code analysis and semantic understanding, enabling code exploration while remaining fully local and offline.

## Key Features

* **AST-Based Parsing**: Utilizes `tree-sitter` to extract structured elements like functions and docstrings, filtering out syntax noise and formatting variations.
* **Local Vector Search**: Runs entirely offline using ChromaDB and Sentence-Transformers, ensuring full code privacy with zero external API dependencies.
* **Semantic Understanding**: Transforms raw code into vector embeddings that map implementation logic to natural language meaning.
* **Persistent Indexing**: Builds a reusable vector index that persists to disk, enabling incremental indexing and fast retrieval across sessions.

## Architecture

The system is designed with a modular architecture and separation of tasks:

* **`parser.py`**: Handles AST-based structural extraction.
* **`embedder.py`**: Manages the embedding generation layer using local transformer models.
* **`storage.py`**: Handles vector persistence, identity management, and database interactions.
* **`main.py`**: Serves as the CLI entry point for user interaction.

## Current Version: v0.1

Version 0.1 just the architecture for semantic indexing and retrieval.

**Implemented Capabilities:**
* Function-level AST parsing using `tree-sitter`.
* Extraction of function metadata (name, docstring, source code, file path, line number).
* Local embedding generation using `Sentence-Transformers`.
* Persistent vector storage with `ChromaDB`.
* Incremental indexing via stable structural identity hashing.
* file-level indexing.

## Technology Stack

* **Language**: Python 3.10+
* **Parsing**: Tree-sitter (Python bindings)
* **ML/AI**: Sentence-Transformers (`all-MiniLM-L6-v2`), NumPy
* **Database**: ChromaDB (Persistent Vector Store)

## Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/code-atlas.git](https://github.com/yourusername/code-atlas.git)
    cd code-atlas
    ```

2.  **Set up a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To index a Python file and add it to the local vector database, run the following command from the project root:

```bash
python main.py path/to/your/file.py
