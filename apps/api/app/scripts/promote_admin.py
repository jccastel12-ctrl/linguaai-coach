"""Promote an existing user to administrator without embedding credentials.

Usage from apps/api:
    python -m app.scripts.promote_admin admin@example.com
"""
import argparse
import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.domains.users.models import User
from app.domains.users.service import normalize_email


async def promote(email: str) -> int:
    async with SessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == normalize_email(email)))
        if user is None:
            print(f"User not found: {email}")
            return 1
        user.is_superuser = True
        await db.commit()
        print(f"Administrator enabled for: {user.email}")
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote an existing LinguaAI user to administrator")
    parser.add_argument("email")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(promote(args.email)))


if __name__ == "__main__":
    main()
