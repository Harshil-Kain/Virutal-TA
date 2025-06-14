'''
This script loads a pre-built FAISS index, metadata, and text chunks, 
then defines a function to retrieve the top-k most relevant chunks for 
a given query using semantic search. It returns both the matching text and its 
source, and demonstrates usage with a sample question if run directly.
'''

import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_FILE = "data/faiss/faiss_index.index"
METADATA_FILE = "data/metadata/faiss_metadata.json"
CHUNK_FILE = "data/chunks/chunks.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index(INDEX_FILE)

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

with open(CHUNK_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

assert len(metadata) == len(chunks), "Metadata and chunks length mismatch"

index_to_chunk = {i: chunks[i]["text"] for i in range(len(chunks))}
index_to_source = {i: metadata[i] for i in range(len(metadata))}

def get_top_k_chunks(query: str, k=3):
    query_vec = model.encode([query]).astype("float32")
    D, I = index.search(query_vec, k)
    results = []

    for idx in I[0]:
        results.append({
            "source" : index_to_source[idx],
            "text": index_to_chunk[idx],
        })
    
    return results

# Used an example to check the retrieval functionality
if __name__ == "__main__":
    question = "What is Docker and how is it used in the course?"
    top_chunks = get_top_k_chunks(question, k=3)
    for i, chunk in enumerate(top_chunks):
        print(f"\nResult {i+1} [source: {chunk['source']}]:\n{chunk['text']}")