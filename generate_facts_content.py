"""
Fact Card Generator
====================
Generates square Instagram image cards from a bank of facts, plus matching
captions, and appends them to post_queue.json (the same file ig_auto_post.py
reads from).

This handles content CREATION. It does not upload/host the images —
Instagram's API needs a public URL for each image, so after running this
you still need to upload the /generated_cards/ folder somewhere public
(S3, Cloudinary, Imgur API, your own site) and update media_url in
post_queue.json to point at the hosted versions.

Install deps:
    pip install Pillow --break-system-packages
"""

import json
import textwrap
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("generated_cards")
QUEUE_FILE = "post_queue.json"
CARD_SIZE = (1080, 1080)  # Instagram square

# ---------------------------------------------------------------------------
# FACT BANK — replace/expand this with your chosen niche.
# Swap this whole list out per-niche (psychology, space, history, etc.)
# ---------------------------------------------------------------------------
FACTS = [
    {
        "text": "Octopuses have three hearts, and two of them stop beating when it swims — which is why they prefer crawling.",
        "category": "Biology",
    },
    {
        "text": "A day on Venus is longer than a year on Venus. It rotates so slowly that one spin takes 243 Earth days.",
        "category": "Space",
    },
    {
        "text": "The Eiffel Tower grows about 6 inches taller in summer as the iron expands in the heat.",
        "category": "Physics",
    },
    {
        "text": "Sharks existed before trees. Sharks date back roughly 400 million years; the earliest trees appeared about 350 million years ago.",
        "category": "History",
    },
    {
        "text": "Your brain uses about 20% of your body's total energy, despite being only about 2% of your body weight.",
        "category": "Psychology",
    },
    {
        "text": "Honey never spoils. Edible honey has been found in Egyptian tombs over 3,000 years old.",
        "category": "Science",
    },
]

# Color palette pairs (background, text) — rotate per card for variety
PALETTES = [
    ("#0F172A", "#F8FAFC"),
    ("#1E1B4B", "#E0E7FF"),
    ("#111827", "#FDE68A"),
    ("#052E16", "#DCFCE7"),
]


def get_font(size, bold=False):
    # Falls back to default if no system fonts found — swap in your own .ttf for a real brand look
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render_card(fact, index):
    bg, fg = random.choice(PALETTES)
    img = Image.new("RGB", CARD_SIZE, bg)
    draw = ImageDraw.Draw(img)

    # Category tag top-left
    tag_font = get_font(36, bold=True)
    draw.text((60, 60), fact["category"].upper(), font=tag_font, fill=fg)

    # Wrapped fact text, centered vertically
    body_font = get_font(58, bold=True)
    wrapped = textwrap.fill(fact["text"], width=26)
    lines = wrapped.split("\n")
    line_height = 74
    total_height = line_height * len(lines)
    y = (CARD_SIZE[1] - total_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=body_font)
        line_width = bbox[2] - bbox[0]
        x = (CARD_SIZE[0] - line_width) // 2
        draw.text((x, y), line, font=body_font, fill=fg)
        y += line_height

    footer_font = get_font(28)
    draw.text((60, CARD_SIZE[1] - 80), "Follow for more", font=footer_font, fill=fg)

    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"fact_{index:03d}.png"
    img.save(path)
    return path


def build_caption(fact):
    tags = "#didyouknow #facts #" + fact["category"].lower().replace(" ", "")
    return f"{fact['text']}\n\n{tags}"


def load_queue():
    try:
        with open(QUEUE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)


def main():
    queue = load_queue()
    for i, fact in enumerate(FACTS):
        img_path = render_card(fact, i)
        queue.append({
            # Relative path — ig_auto_post.py resolves this into a public
            # raw.githubusercontent.com URL automatically at post time.
            "media_url": str(img_path),
            "caption": build_caption(fact),
            "media_type": "IMAGE",
        })
        print(f"Generated card: {img_path}")

    save_queue(queue)
    print(f"\nAdded {len(FACTS)} items to {QUEUE_FILE}.")
    print("These will be committed by the workflow — no manual upload needed.")


if __name__ == "__main__":
    main()
