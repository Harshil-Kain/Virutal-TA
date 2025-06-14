'''
This code is used to scrape the TDS Discourse forum for topics created between 1 Jan 2025 and 14 Apr 2025.
It fetches the topic list, filters topics by date, and retrieves the content of each topic.
'''

import requests
import json
from datetime import datetime

url = "https://discourse.onlinedegree.iitm.ac.in/c/tds/34.json"

cookies = {
    #<add the cookies from the website here after login>
}


headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://discourse.onlinedegree.iitm.ac.in",
    "Accept": "application/json"
}

def is_within_date_range(date_str):
    """Check if a date is within 1 Jan 2025 to 14 Apr 2025"""
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return datetime(2025, 1, 1) <= dt <= datetime(2025, 4, 14)

def fetch_all_topics():
    print("Fetching topic list")
    topics = []
    page = 0

    while True:
        url = f"https://discourse.onlinedegree.iitm.ac.in/c/tds/34.json?page={page}"
        response = requests.get(url, headers=headers, cookies=cookies)

        if response.status_code != 200:
            print(f"Failed to fetch page {page} (Status: {response.status_code})")
            break

        data = response.json()
        page_topics = data.get('topic_list', {}).get('topics', [])
        if not page_topics:
            break  

        topics.extend(page_topics)
        print(f"Page {page}: Found {len(page_topics)} topics")
        page += 1

    return topics

def fetch_topic_details(topic_id):
    url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}.json"
    response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code == 200:
        return response.json()
    return None

def scrape_tds_posts():
    topics = fetch_all_topics()
    filtered_posts = []

    for topic in topics:
        if not is_within_date_range(topic['created_at']):
            continue

        topic_id = topic['id']
        print(f"Fetching topic ID: {topic_id}")

        topic_data = fetch_topic_details(topic_id)
        if not topic_data:
            print(f"Failed to fetch topic {topic_id}")
            continue

        post_data = {
            'topic_id': topic_id,
            'title': topic_data['title'],
            'created_at': topic_data['created_at'],
            'posts': []
        }

        for post in topic_data['post_stream']['posts']:
            if is_within_date_range(post['created_at']):
                post_data['posts'].append({
                    'username': post.get('username', 'unknown'),
                    'created_at': post['created_at'],
                    'raw': post.get('raw') or post.get('cooked') or ''
                })
                

        if post_data['posts']:
            filtered_posts.append(post_data)

    print(f"\n Found {len(filtered_posts)} topics with posts in the date range.")
    
    with open("tds_forum_posts.json", "w", encoding='utf-8') as f:
        json.dump(filtered_posts, f, indent=2)

    print("Saved to tds_forum_posts.json")

if __name__ == "__main__":
    scrape_tds_posts()