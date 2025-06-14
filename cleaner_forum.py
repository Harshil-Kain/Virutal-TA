'''
This code is used to clean and process the forum posts data from TDS Discourse Forum.
'''

import os
import json
from bs4 import BeautifulSoup
from pathlib import Path

RAW_FILE = "data/tds_forum_posts.json"
OUT_FILE = "data/processed/forum_posts_clean.json"

os.makedirs(Path(OUT_FILE).parent, exist_ok=True)

def clean_html(raw_html):
    return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()

def clean_forum_data():
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned_threads = []

    for thread in raw_data:
        title = thread.get("title", "Untitled").strip()
        posts = thread.get("posts", [])

        cleaned_posts = []
        for post in posts:
            user = post.get("username", "anonymous")
            text = clean_html(post.get("raw", ""))
            if text:
                cleaned_posts.append({"username": user, "text": text})

        if cleaned_posts:
            cleaned_threads.append({
                "title": title,
                "discussion": cleaned_posts
            })

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_threads, f, indent=2, ensure_ascii=False)

    print(f"Cleaned {len(cleaned_threads)} forum threads saved to {OUT_FILE}")

if __name__ == "__main__":
    clean_forum_data()
