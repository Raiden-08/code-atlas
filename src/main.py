
"""
Code Atlas - CLI Entry Point

This module provides command-line access to core functionality:
- Indexing a file or directory into the vector database
- Tracing function call relationships
- Performing semantic search with structural context

Design Principles:
- Keep main.py thin (only orchestration)
- Delegate logic to services (search, graph, parser, storage)
- Lazy-load heavy dependencies (Embedder) only when needed
"""

import sys
import os

from src.parser import get_functions_from_file
from src.storage import VectorDB
from src.services.search import semantic_search
from src.services.graph import (
    get_function_context,
    build_call_graph,
    get_multi_hop_calls,
    get_multi_hop_callers
)

# -----------------------------
# File Discovery Utilities
# -----------------------------

def get_python_files(root_path):
    """
    Recursively collect all Python files from a given path.

    Args:
        root_path (str): File or directory path

    Returns:
        list[str]: List of .py file paths
    """
    python_files = []

    # If single file → return directly
    if os.path.isfile(root_path):
        return [root_path]

    # Walk directory tree
    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            if file.endswith(".py"):
                python_files.append(os.path.join(dirpath, file))

    return python_files


def get_all_functions(path):
    """
    Parse all Python files and extract function metadata.

    Args:
        path (str): File or directory path

    Returns:
        list[dict]: List of function dictionaries
    """
    files = get_python_files(path)
    all_functions = []

    for file in files:
        try:
            funcs = get_functions_from_file(file)
            all_functions.extend(funcs)
        except Exception as e:
            print(f"Skipping {file}: {e}")

    return all_functions


# -----------------------------
# Indexing
# -----------------------------

def index_path(path):
    """
    Index functions from a file or directory into the vector database.

    - Extracts functions using AST parser
    - Generates embeddings
    - Stores them using ChromaDB (upsert)

    Args:
        path (str): File or directory path
    """
    from src.embedder import Embedder  # lazy import

    functions = get_all_functions(path)

    embedder = Embedder()
    db = VectorDB()

    payloads = [
        f"Function Name: {f['name']}\n\n"
        f"Docstring: {f['docstring'] or ''}\n\n"
        f"Code:\n{f['code']}"
        for f in functions
    ]

    embeddings = embedder.embed_batch(payloads)
    db.upsert_functions(functions, embeddings)

    print(f"Indexed {len(functions)} functions from {path}")


# -----------------------------
# Trace Command
# -----------------------------

def trace_function(path, target):
    functions = get_all_functions(path)
    graph = build_call_graph(functions)

    if target not in graph:
        print(f"Function '{target}' not found.")
        return

    print(f"\nFunction: {target}")

    # Multi-hop traversal
    hops = get_multi_hop_calls(graph, target, max_depth=2)

    print("\nCall Flow:")

    for depth, func in hops:
        indent = "  " * depth
        print(f"{indent}→ {func}")



# -----------------------------
# Explanation Layer
# -----------------------------

def explain_match(func, query):
    """
    Generate a simple explanation for why a function matched a query.

    Args:
        func (dict): Function metadata
        query (str): User query

    Returns:
        str: Explanation string
    """
    reasons = []

    name = func["name"].lower()
    query_lower = query.lower()

    if any(word in name for word in query_lower.split()):
        reasons.append("Name matches query")

    if func["docstring"] and any(word in func["docstring"].lower() for word in query_lower.split()):
        reasons.append("Docstring relevance")

    if not reasons:
        reasons.append("Semantic similarity")

    return ", ".join(reasons)


# -----------------------------
# Ask Command (Semantic Search)
# -----------------------------

def ask_question(path, query):
    functions = get_all_functions(path)
    graph = build_call_graph(functions)

    results = semantic_search(functions, query, top_k=3)

    print(f"\nQuery: {query}")

    for rank, (score, func) in enumerate(results, 1):
        reason = explain_match(func, query)

        print(f"\n--- Result {rank} ---")
        print(f"Function: {func['name']}")
        print(f"File: {func['filepath']}")
        print(f"Score: {score:.4f}")
        print(f"Reason: {reason}")

        # Multi-hop flow
        hops = get_multi_hop_calls(graph, func["name"], max_depth=2)

        print("\nCall Flow:")
        if not hops:
            print("  (no further calls)")
        else:
            for depth, f_name in hops:
                indent = "  " * depth
                print(f"{indent}→ {f_name}")
        callers = get_multi_hop_callers(graph, func["name"], max_depth=2)

        print("\nCalled By:")
        if not callers:
            print("  (no callers)")
        else:
            for depth, f_name in callers:
                indent = "  " * depth
                print(f"{indent}← {f_name}")

# -----------------------------
# CLI Entry Point
# -----------------------------

def main():
    """
    Command-line interface entry point.

    Supported commands:
    - index <path>
    - trace <path> <function_name>
    - ask <path> <query>
    """
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python main.py index <path>")
        print("  python main.py trace <path> <function_name>")
        print("  python main.py ask <path> <query>")
        return

    command = sys.argv[1]

    if command == "index":
        index_path(sys.argv[2])

    elif command == "trace":
        if len(sys.argv) != 4:
            print("Usage: python main.py trace <path> <function_name>")
        else:
            trace_function(sys.argv[2], sys.argv[3])

    elif command == "ask":
        if len(sys.argv) < 4:
            print("Usage: python main.py ask <path> <query>")
        else:
            query = " ".join(sys.argv[3:])
            ask_question(sys.argv[2], query)

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
