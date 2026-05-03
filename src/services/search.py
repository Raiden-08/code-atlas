import numpy as np

from src.services.graph import build_call_graph

def build_payloads(functions):
    payloads = []

    for f in functions:
        name = f["name"]
        doc = f["docstring"] or ""
        code = f["code"]

        payload = (
            f"Function Name: {name}\n"
            f"{name} {name}\n\n"   # boost name
            f"Docstring: {doc}\n\n"
            f"Code:\n{code}"
        )

        payloads.append(payload)

    return payloads



def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def semantic_search(functions, query,top_k=3):
    
    from src.embedder import Embedder
    embedder = Embedder()

    payloads = build_payloads(functions)

    embeddings = embedder.embed_batch(payloads)
    query_embedding = embedder.embed_query(query)

    scores = []
    graph = build_call_graph(functions)
    
    for i, emb in enumerate(embeddings):
        name_match_bonus = 0

        if query.lower() in functions[i]["name"].lower():
            name_match_bonus = 0.1
        score = cosine(query_embedding, emb) + name_match_bonus

        
        if functions[i]["name"] in graph:
            if any(query.lower() in c.lower() for c in graph[functions[i]["name"]]["calls"]):
                score += 0.05

        scores.append((score, functions[i]))
    scores.sort(reverse=True, key=lambda x: x[0])

    return scores[:top_k]
