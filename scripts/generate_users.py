from __future__ import annotations

import argparse
import json
import random
import uuid
from pathlib import Path


FIRST_NAMES = [
    "Luca", "Marco", "Giulia", "Sara", "Alessandro", "Martina", "Davide", "Elena",
    "Federico", "Chiara", "Matteo", "Francesca", "Simone", "Valentina", "Andrea",
    "Sofia", "Giorgio", "Alice", "Stefano", "Beatrice"
]

LAST_NAMES = [
    "Rossi", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco", "Bruno",
    "Gallo", "Conti", "De Luca", "Mancini", "Costa", "Giordano", "Rinaldi",
    "Moretti", "Barbieri", "Lombardi", "Ferrari", "Esposito"
]

DOMAINS = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "example.com"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic users dataset.")
    parser.add_argument(
        "--num-users",
        type=int,
        default=200,
        help="Number of synthetic users to generate."
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("data/processed/users_seed.json"),
        help="Path to output JSON file."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility."
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "")
        .replace("'", "")
    )


def generate_unique_username(existing: set[str], first_name: str, last_name: str) -> str:
    base = f"{slugify(first_name)}.{slugify(last_name)}"
    username = base
    counter = 1

    while username in existing:
        username = f"{base}{counter}"
        counter += 1

    existing.add(username)
    return username


def generate_users(num_users: int, rng: random.Random) -> list[dict]:
    users = []
    usernames = set()
    emails = set()

    for _ in range(num_users):
        first_name = rng.choice(FIRST_NAMES)
        last_name = rng.choice(LAST_NAMES)
        username = generate_unique_username(usernames, first_name, last_name)

        domain = rng.choice(DOMAINS)
        email = f"{username}@{domain}"
        while email in emails:
            email = f"{username}{rng.randint(1, 999)}@{domain}"
        emails.add(email)

        user = {
            "_id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "display_name": f"{first_name} {last_name}",
            "favorite_genres": rng.sample(
                ["Action", "Adventure", "RPG", "Simulation", "Strategy", "Sports", "Indie", "Casual"],
                k=rng.randint(1, 3)
            ),
            "created_at": f"2024-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
        }
        users.append(user)

    return users


def main() -> None:
    args = parse_args()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    users = generate_users(args.num_users, rng)

    with args.output_json.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    print("Users generation completed successfully.")
    print(f"Users generated: {len(users)}")
    print(f"Output file: {args.output_json}")


if __name__ == "__main__":
    main()