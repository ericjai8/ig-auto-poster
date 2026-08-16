"""
Instagram Auto-Poster (Graph API) — GitHub Actions edition
============================================================

Reads IG_USER_ID and ACCESS_TOKEN from environment variables (set as
GitHub Actions secrets — never hardcoded here).

Images referenced in post_queue.json can be a relative path like
"generated_cards/fact_000.png" — this script resolves that into a public
raw.githubusercontent.com URL automatically, using the GITHUB_REPOSITORY
env var GitHub Actions provides for free. If media_url is already a full
http(s) URL, it's used as-is.

This script posts exactly ONE item per run — the workflow schedules how
often that happens (e.g. once or twice a day).
"""

import os
import sys
import json
import time
import requests

IG_USER_ID = os.environ["IG_USER_ID"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
GRAPH_API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

QUEUE_FILE = "post_queue.json"
BRANCH = os.environ.get("MEDIA_BRANCH", "main")
REPO = os.environ.get("GITHUB_REPOSITORY")  # e.g. "yourname/ig-auto-poster"


def resolve_media_url(media_url):
    if media_url.startswith("http://") or media_url.startswith("https://"):
        return media_url
    if not REPO:
        raise RuntimeError(
            "media_url is a relative path but GITHUB_REPOSITORY is not set — "
            "run this inside GitHub Actions, or use a full URL."
        )
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{media_url}"


def load_queue():
    try:
        with open(QUEUE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)


def create_media_container(item):
    url = f"{BASE_URL}/{IG_USER_ID}/media"
    params = {"caption": item["caption"], "access_token": ACCESS_TOKEN}
    resolved_url = resolve_media_url(item["media_url"])

    if item.get("media_type") == "REELS":
        params["media_type"] = "REELS"
        params["video_url"] = resolved_url
    else:
        params["image_url"] = resolved_url

    resp = requests.post(url, data=params)
    resp.raise_for_status()
    return resp.json()["id"]


def wait_for_container_ready(container_id, timeout=120):
    url = f"{BASE_URL}/{container_id}"
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(url, params={"fields": "status_code", "access_token": ACCESS_TOKEN})
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            raise RuntimeError(f"Container {container_id} failed processing")
        time.sleep(5)
    raise TimeoutError(f"Container {container_id} not ready after {timeout}s")


def publish_container(container_id):
    url = f"{BASE_URL}/{IG_USER_ID}/media_publish"
    params = {"creation_id": container_id, "access_token": ACCESS_TOKEN}
    resp = requests.post(url, data=params)
    resp.raise_for_status()
    return resp.json()


def post_next_in_queue():
    queue = load_queue()
    if not queue:
        print("Queue empty — nothing to post. Run the content-generation workflow to refill it.")
        return

    item = queue.pop(0)
    print(f"Posting: {item['caption'][:60]}...")

    try:
        container_id = create_media_container(item)
        if item.get("media_type") == "REELS":
            wait_for_container_ready(container_id)
        result = publish_container(container_id)
        print(f"Published. Media ID: {result.get('id')}")
        save_queue(queue)
    except Exception as e:
        print(f"FAILED: {e}")
        queue.insert(0, item)
        save_queue(queue)
        sys.exit(1)


if __name__ == "__main__":
    post_next_in_queue()
