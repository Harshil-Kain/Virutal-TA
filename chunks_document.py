'''
This code is used to process the course content and forum data, splitting the content into
manageable approx 300 chunks and tags each chunk with the tag of course or forum
 for further analysis or storage.
'''

import os
import json
import re
from pathlib import Path

RAW_COURSE_FILE = "data/processed/course_content_clean.json"
RAW_FORUM_FILE = "data/processed/forum_posts_clean.json"
CHUNK_FILE = "data/chunks/chunks.json"

os.makedirs(Path(CHUNK_FILE).parent, exist_ok=True)

MAX_WORDS = 300
OVERLAP_WORDS = 50

def split_into_chunks(text, max_words=MAX_WORDS, overlap=OVERLAP_WORDS):
    words = text.split()
    chunks = []
    i = 0

    while i < len(words):
      chunk = words[i:i + max_words]
      chunks.append(" ".join(chunk))
      i += max_words - overlap

    return chunks

def load_course_chunks():
    with open(RAW_COURSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []

    for item in data:
        title = item.get("title", "Untitled")
        slug = item.get("slug", "")
        content = item.get("content", "")
        section_chunks = split_into_chunks(content)

        for i, chunk in enumerate(section_chunks):
            chunks.append({
                "source": f"course:{title}#{i}",
                "text": chunk
            })

    return chunks

def load_forum_chunks():
    with open(RAW_FORUM_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []

    for thread in data:
        title = thread.get("title", "Untitled")
        discussion = thread.get("discussion", [])
        all_text = "\n".join([f"{p['username']}: {p['text']}" for p in discussion if p['text']])
        thread_chunks = split_into_chunks(all_text)

        for i, chunk in enumerate(thread_chunks):
            chunks.append({
                "source": f"forum:{title}#{i}",
                "text": chunk
            })

    return chunks

def main():
    course_chunks = load_course_chunks()
    forum_chunks = load_forum_chunks()
    all_chunks = course_chunks + forum_chunks

    with open(CHUNK_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"Created {len(all_chunks)} chunks and saved to {CHUNK_FILE}")

if __name__ == "__main__":
    main()
