"""
Synthetic Instagram Data Generator
Creates 90 days of account metrics and 100 posts aligned with Instagram Graph API fields.
"""

import json
import random
import string
import datetime
from pathlib import Path
from typing import List, Dict, Any


def random_post_id() -> str:
    """Generate an 18-digit numeric string for consistency with IG media IDs."""
    return ''.join(random.choices(string.digits, k=18))


def generate_dates(num_days: int = 90) -> List[datetime.date]:
    """Generate the last N days from today (ascending)."""
    today = datetime.date.today()
    return [today - datetime.timedelta(days=i) for i in range(num_days)][::-1]


def generate_account_metrics() -> List[Dict[str, Any]]:
    """
    Generate 90 days of synthetic IG account-level metrics with weekday spikes and soft growth.
    """
    dates = generate_dates(90)

    followers_start = 100_000
    followers_end = 102_800
    followers_growth = (followers_end - followers_start) / len(dates)

    account_metrics = []
    for i, d in enumerate(dates):
        followers = int(followers_start + followers_growth * i)

        # Seasonality: stronger Tue/Thu/Sun, softer Mon/Wed
        base_impressions = random.randint(30_000, 60_000)
        if d.weekday() in [1, 3, 6]:  # Tue/Thu/Sun
            base_impressions = int(base_impressions * random.uniform(1.25, 1.5))
        elif d.weekday() in [0, 2]:  # Mon/Wed
            base_impressions = int(base_impressions * random.uniform(0.85, 0.95))

        # Light upward drift to mimic growth
        growth_bump = int(i * random.uniform(12, 25))
        base_impressions = max(10_000, base_impressions + growth_bump)

        reach = int(base_impressions * random.uniform(0.68, 0.74))
        profile_views = random.randint(950, 2100)
        website_clicks = random.randint(180, 520)

        account_metrics.append({
            "date": d.isoformat(),
            "followers": followers,
            "impressions": base_impressions,
            "reach": reach,
            "profile_views": profile_views,
            "website_clicks": website_clicks
        })

    return account_metrics


def random_caption() -> str:
    """Generate realistic Portuguese captions with emojis and hashtags."""
    starts = [
        "Hoje foi intenso! ",
        "Refletindo sobre a jornada... ",
        "Vocês pediram e eu entreguei! ",
        "Confesso que esse post foi especial 💛 ",
        "Nem acredito que isso aconteceu 😭 ",
        "Pequenos momentos, grandes histórias ✨ ",
        "Que dia! ",
        "Minha versão favorita de mim mesma 🖤 ",
    ]

    middles = [
        "Cada passo importa.",
        "Estou vivendo meu sonho e sendo muito grata.",
        "Nada supera essa sensação.",
        "A estética de hoje está forte.",
        "Eu precisava compartilhar isso.",
        "Essa luz estava simplesmente perfeita.",
        "Quem aí se identifica?",
        "Esse momento merece ficar registrado.",
    ]

    hashtags = [
        "#rotinanomade", "#viagens", "#nomadlife", "#digitalnomad",
        "#buenosaires", "#paris", "#italytrip", "#europeansummer",
        "#travelgirl", "#creatorlife", "#conteudo",
        "#marketingdigital", "#mulheresviajantes"
    ]

    cap = random.choice(starts) + random.choice(middles) + " " + \
        " ".join(random.sample(hashtags, k=4)) + " " + random.choice(["✨", "💛", "🔥", "🌍", "📸"])
    return cap


def generate_posts() -> List[Dict[str, Any]]:
    """
    Generate 100 synthetic IG posts with realistic performance, viral spikes, and varied media types.
    """
    posts = []

    dates = generate_dates(90)
    possible_times = ["18:12", "19:03", "19:44", "20:15", "20:55", "21:07"]

    media_types = (
        ["IMAGE"] * 60 +
        ["CAROUSEL_ALBUM"] * 30 +
        ["VIDEO"] * 10
    )

    viral_posts_idx = set(random.sample(range(100), 12))

    for i in range(100):
        date = random.choice(dates)
        time = random.choice(possible_times)
        timestamp = f"{date.isoformat()}T{time}:00+0000"

        media_type = random.choice(media_types)

        # Base performance
        impressions = random.randint(8000, 25000)
        reach = int(impressions * random.uniform(0.70, 0.80))
        likes = random.randint(500, 5000)
        comments = random.randint(20, 200)
        shares = random.randint(0, 50)
        saves = random.randint(30, 300)

        # Viral posts
        if i in viral_posts_idx:
            multiplier = random.uniform(1.8, 3.0)
            impressions = int(impressions * multiplier)
            reach = int(reach * multiplier)
            likes = int(likes * multiplier)
            comments = int(comments * multiplier)
            shares = int(shares * multiplier)
            saves = int(saves * multiplier)

        posts.append({
            "id": random_post_id(),
            "caption": random_caption(),
            "media_type": media_type,
            "timestamp": timestamp,
            "impressions": impressions,
            "reach": reach,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves
        })

    return posts


def main():
    output = {
        "account_metrics": generate_account_metrics(),
        "posts": generate_posts()
    }

    project_dir = Path(__file__).resolve().parent.parent
    output_path = project_dir / "data" / "synthetic_instagram_data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Synthetic Instagram dataset created -> {output_path}")


if __name__ == "__main__":
    main()
