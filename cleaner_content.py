'''
This code is used to clean and process the course content data from TDS (The Data Science) course.
'''


import os
import json
import re
from pathlib import Path

RAW_FILE = "data/tds_all_content.json"
OUT_FILE = "data/processed/course_content_clean.json"

os.makedirs(Path(OUT_FILE).parent, exist_ok=True)

def clean_text_block(block):
    lines = []

    if "heading" in block:
        lines.append(f"## {block['heading'].strip()}")

    if "paragraphs" in block:
        for p in block["paragraphs"]:
            text = p.strip()
            if text:
                lines.append(text)

    for key in ["ordered_list", "unordered_list"]:
        if key in block:
            for item in block[key]:
                symbol = "-" if key == "unordered_list" else "1."
                lines.append(f"{symbol} {item.strip()}")

    return "\n".join(lines)

def clean_tds_content():
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned_data = []

    for item in raw_data:
        slug = item.get("page", "").replace("#/2025-01/", "").strip("/")
        blocks = item.get("blocks", [])
        section_texts = [clean_text_block(b) for b in blocks if isinstance(b, dict)]
        full_text = "\n\n".join(filter(None, section_texts))

        if full_text:
            cleaned_data.append({
                "title": blocks[0].get("heading", "Untitled") if blocks else "Untitled",
                "slug": slug,
                "content": full_text.strip()
            })

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"Cleaned {len(cleaned_data)} course content items saved to {OUT_FILE}")

if __name__ == "__main__":
    clean_tds_content()
