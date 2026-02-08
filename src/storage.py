# src/storage.py
import chromadb
from chromadb.config import Settings
import hashlib

class VectorDB:
    def __init__(self, persist_path="./atlas_db"):
        
        self.client = chromadb.PersistentClient(path=persist_path)
        
        self.collection = self.client.get_or_create_collection(name="code_functions")
    
    def _strip_docstring(self, code):
        lines = code.splitlines()
        new_lines = []
        inside_docstring = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            new_lines.append(line)

        return "\n".join(new_lines)

     
    def normalize_code(self,code):
        lines = code.splitlines()
        cleaned = [line.rstrip() for line in lines]
        return "\n".join(cleaned).strip()

    
    def generate_id(self,filepath,full_code):
        normalized_code = self.normalize_code(full_code)
        without_doc = self._strip_docstring(normalized_code)
        hash_value = hashlib.sha256(without_doc.encode("utf-8")).hexdigest()
        return f"{filepath}::{hash_value}"

    def upsert_functions(self, functions, embeddings):
        ids = [
            self.generate_id(f['filepath'],f['code'])
            for f in functions 
        ]
        
        
        metadatas = [{
            "docstring": f["docstring"],
            "line": f["line"],
            "filepath": f["filepath"]
        } for f in functions]


        documents = [
            f"Function Name: {f['name']}\n\n"
            f"Docstring: {f['docstring'] or ''}\n\n"
            f"Code:\n{f['code']}"
            for f in functions
        ]
        if hasattr(embeddings, "tolist"):
                embeddings = embeddings.tolist()
        self.collection.upsert(
            ids=ids,
            embeddings= embeddings, 
            metadatas=metadatas,
            documents=documents
        )
        print(f"Saved {len(functions)} functions to Database.")

    def search(self, query_embedding, n_results=5):
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results