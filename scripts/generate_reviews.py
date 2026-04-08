from __future__ import annotations

import argparse
import json
import random
import uuid
from pathlib import Path


POSITIVE_COMMENTS = [
    "Great gameplay and solid mechanics.",
    "Very enjoyable experience, would recommend.",
    "Fun and engaging from start to finish.",
    "Interesting design and good replay value.",
    "A really polished and entertaining game.",
    "Loved the progression system and atmosphere.",
    "Good value for the price.",
    "One of the best games I tried recently."
]

NEGATIVE_COMMENTS = [
    "Could be improved in several areas.",
    "Not bad, but it gets repetitive quickly.",
    "Interesting idea, but execution is weak.",
    "I expected more content and polish.",
    "Some mechanics feel frustrating.",
    "Performance issues affected the experience.",
    "The game has potential, but needs improvement.",
    "Not really worth the current price."
]

MIXED_COMMENTS = [
    "Some good ideas, but not everything works well.",
    "Average experience overall.",
    "Enjoyable in parts, but inconsistent.",
    "Decent game with both strengths and weaknesses.",
    "It has potential, though it feels unbalanced.",
    "Worth trying, but not for everyone."
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic reviews dataset.")
    parser.add_argument(
        "--games-json",
        type=Path,
        default=Path("data/processed/games_cleaned.json"),
        help="Path to cleaned games JSON."
    )
    parser.add_argument(
        "--users-json",
        type=Path,
        default=Path("data/processed/users_seed.json"),
        help="Path to users seed JSON."
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("data/processed/reviews_seed.json"),
        help="Path to output reviews JSON."
    )
    parser.add_argument(
        "--num-reviews",
        type=int,
        default=1000,
        help="Number of reviews to generate."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility."
    )
    return parser.parse_args()


def load_json(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def choose_comment(rating: int, rng: random.Random) -> str:
    if rating >= 8:
        return rng.choice(POSITIVE_COMMENTS)
    if rating <= 4:
        return rng.choice(NEGATIVE_COMMENTS)
    return rng.choice(MIXED_COMMENTS)


def generate_reviews(
    games: list[dict],
    users: list[dict],
    num_reviews: int,
    rng: random.Random
) -> list[dict]:
    if not games:
        raise ValueError("Games list is empty.")
    if not users:
        raise ValueError("Users list is empty.")

    reviews = []
    used_pairs = set()

    available_game_ids = [game["appid"] for game in games]
    available_user_ids = [user["_id"] for user in users]

    max_possible = len(available_game_ids) * len(available_user_ids)
    if num_reviews > max_possible:
        raise ValueError(
            f"Requested {num_reviews} reviews, but maximum unique user-game pairs is {max_possible}."
        )

    while len(reviews) < num_reviews:
        appid = rng.choice(available_game_ids)
        user_id = rng.choice(available_user_ids)

        pair = (user_id, appid)
        if pair in used_pairs:
            continue

        used_pairs.add(pair)

        rating = rng.randint(1, 10)
        review = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "appid": appid,
            "rating": rating,
            "comment": choose_comment(rating, rng),
            "created_at": f"2025-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
            "updated_at": None
        }
        reviews.append(review)

    return reviews


def main() -> None:
    args = parse_args()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)

    games = load_json(args.games_json)
    users = load_json(args.users_json)

    reviews = generate_reviews(games, users, args.num_reviews, rng)

    with args.output_json.open("w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

    print("Reviews generation completed successfully.")
    print(f"Games loaded: {len(games)}")
    print(f"Users loaded: {len(users)}")
    print(f"Reviews generated: {len(reviews)}")
    print(f"Output file: {args.output_json}")


if __name__ == "__main__":
    main()
