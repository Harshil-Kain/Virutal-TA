'''
This script loads text chunks and their sources from a chunks json file,
generates semantic embeddings using a pre-trained SentenceTransformer model, 
and builds a FAISS index for fast similarity search. It saves the index and 
corresponding metadata to disk for later retrieval.
'''

import os
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss

CHUNK_FILE = "data/chunks/chunks.json"
INDEX_FILE = "data/faiss/faiss_index.index"
METADATA_FILE = "data/metadata/faiss_metadata.json"

os.makedirs("data/", exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

with open(CHUNK_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [chunk["text"] for chunk in chunks]
metas = [chunk["source"] for chunk in chunks]

print("Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True)

embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, INDEX_FILE)
with open(METADATA_FILE, "w", encoding="utf-8") as f:
    json.dump(metas, f, indent=2, ensure_ascii=False)

print(f"FAISS index saved to {INDEX_FILE}")
print(f"Metadata saved to {METADATA_FILE}")