'''
In this code the FastAPI app provides an API endpoint that accepts a question, 
retrieves the top 5 most relevant text chunks using semantic search, 
and sends them to the OpenAI API to generate a clear, combined answer. 
It also extracts and returns any unique URLs found in the retrieved content.
'''

from fastapi import FastAPI
from pydantic import BaseModel
from retrieval import get_top_k_chunks
import os
import openai
from dotenv import load_dotenv
import re

load_dotenv()

AIPROXY_TOKEN = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_API_BASE")

client = openai.OpenAI(
    api_key=AIPROXY_TOKEN,
    base_url=OPENAI_BASE_URL
)

app = FastAPI(title="TDS QA API")

class QuestionRequest(BaseModel):
    question: str

@app.post("/api/")
def get_answer(req: QuestionRequest):
    question = req.question
    top_chunks = get_top_k_chunks(question, k=5)
    context = "\n\n".join([chunk['text'] for chunk in top_chunks])

    url_pattern = r"https?://\S+"
    seen = set()
    links = []
    for chunk in top_chunks:
        urls = re.findall(url_pattern, chunk['text'])
        for url in urls:
            clean_url = url.strip().rstrip('),.\n')
            if clean_url not in seen:
                seen.add(clean_url)
                links.append({"url": clean_url, "text": clean_url})

    prompt = f"""
You are a helpful teaching assistant for the \"Tools in Data Science\" course.
Here are some excerpts from course material and forum posts:

"""
    for i, chunk in enumerate(top_chunks):
        prompt += f"Excerpt {i+1}: \"{chunk['text']}\"\n\n"

    prompt += f"Please rephrase and combine the above excerpts to directly and clearly answer the following student question:\n\n{question}\n\nAnswer:"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"

    return {
        "question": question,
        "answer": answer,
        "links": links or []
    }
