from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run sanity checks on cleaned games, users, and reviews datasets."
    )
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
        "--reviews-json",
        type=Path,
        default=Path("data/processed/reviews_seed.json"),
        help="Path to reviews seed JSON."
    )
    return parser.parse_args()


def load_json(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected a list of documents in {path}, got {type(data).__name__}")

    return data


def check_duplicate_ids(documents: list[dict], id_field: str, label: str) -> list[str]:
    ids = [doc.get(id_field) for doc in documents]
    counts = Counter(ids)
    duplicates = [doc_id for doc_id, count in counts.items() if count > 1]

    if duplicates:
        return [f"{label}: found {len(duplicates)} duplicate values in '{id_field}'"]
    return []


def check_games(games: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(check_duplicate_ids(games, "appid", "games"))

    for game in games:
        if not isinstance(game.get("appid"), int):
            errors.append(f"games: invalid appid type for record {game!r}")
            continue

        for field in ["platforms", "categories", "genres", "steamspy_tags"]:
            if field in game and not isinstance(game[field], list):
                errors.append(f"games: field '{field}' is not a list for appid={game['appid']}")

        if "price" in game and not isinstance(game["price"], (int, float)):
            errors.append(f"games: invalid price type for appid={game['appid']}")

        if "release_date" in game and game["release_date"] is None:
            warnings.append(f"games: missing release_date for appid={game['appid']}")

    return errors, warnings


def check_users(users: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(check_duplicate_ids(users, "_id", "users"))
    errors.extend(check_duplicate_ids(users, "username", "users"))
    errors.extend(check_duplicate_ids(users, "email", "users"))

    for user in users:
        if not isinstance(user.get("_id"), str) or not user["_id"].strip():
            errors.append(f"users: invalid _id for user {user!r}")

        if not isinstance(user.get("username"), str) or not user["username"].strip():
            errors.append(f"users: invalid username for user_id={user.get('_id')}")

        if not isinstance(user.get("email"), str) or "@" not in user["email"]:
            errors.append(f"users: invalid email for user_id={user.get('_id')}")

        if "favorite_genres" in user and not isinstance(user["favorite_genres"], list):
            errors.append(f"users: favorite_genres is not a list for user_id={user.get('_id')}")

    return errors, warnings


def check_reviews(reviews: list[dict], valid_game_ids: set[int], valid_user_ids: set[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(check_duplicate_ids(reviews, "_id", "reviews"))

    seen_pairs: set[tuple[str, int]] = set()

    for review in reviews:
        review_id = review.get("_id")
        user_id = review.get("user_id")
        appid = review.get("appid")
        rating = review.get("rating")

        if not isinstance(review_id, str) or not review_id.strip():
            errors.append(f"reviews: invalid _id in review {review!r}")

        if not isinstance(user_id, str) or user_id not in valid_user_ids:
            errors.append(f"reviews: invalid or missing user_id for review_id={review_id}")

        if not isinstance(appid, int) or appid not in valid_game_ids:
            errors.append(f"reviews: invalid or missing appid for review_id={review_id}")

        if not isinstance(rating, int) or not (1 <= rating <= 10):
            errors.append(f"reviews: invalid rating for review_id={review_id}")

        pair = (user_id, appid)
        if pair in seen_pairs:
            errors.append(
                f"reviews: duplicate user-game pair found for user_id={user_id}, appid={appid}"
            )
        else:
            seen_pairs.add(pair)

        if not isinstance(review.get("comment"), str) or not review["comment"].strip():
            warnings.append(f"reviews: empty comment for review_id={review_id}")

    return errors, warnings


def main() -> None:
    args = parse_args()

    games = load_json(args.games_json)
    users = load_json(args.users_json)
    reviews = load_json(args.reviews_json)

    game_errors, game_warnings = check_games(games)
    user_errors, user_warnings = check_users(users)

    valid_game_ids = {game["appid"] for game in games if isinstance(game.get("appid"), int)}
    valid_user_ids = {user["_id"] for user in users if isinstance(user.get("_id"), str)}

    review_errors, review_warnings = check_reviews(reviews, valid_game_ids, valid_user_ids)

    errors = game_errors + user_errors + review_errors
    warnings = game_warnings + user_warnings + review_warnings

    print("Sanity check completed.")
    print(f"Games loaded:   {len(games)}")
    print(f"Users loaded:   {len(users)}")
    print(f"Reviews loaded: {len(reviews)}")
    print()

    if warnings:
        print("Warnings:")
        for warning in warnings[:20]:
            print(f"- {warning}")
        if len(warnings) > 20:
            print(f"- ... and {len(warnings) - 20} more warnings")
        print()
    else:
        print("Warnings: none")
        print()

    if errors:
        print("Errors:")
        for error in errors[:20]:
            print(f"- {error}")
        if len(errors) > 20:
            print(f"- ... and {len(errors) - 20} more errors")
        print()
        raise SystemExit(1)

    print("All sanity checks passed successfully.")


if __name__ == "__main__":
    main()