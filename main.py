import sys
from src.parser import get_functions_from_file
from src.embedder import Embedder
from src.storage import VectorDB


def index_file(file_path):
    functions = get_functions_from_file(file_path)

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

    print(f"Indexed {len(functions)} functions from {file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <python_file>")
    else:
        index_file(sys.argv[1])
