#!/usr/bin/env python3
"""Create an admin user directly in the database (dev/local use only).

There's no signup flow for admins — POST /auth/register always creates a doctor.
This inserts a verified, active User with role=admin directly, bypassing the API.

Always run from the backend/ directory so Settings picks up backend/.env:

    cd backend
    uv run python scripts/create_admin.py --email admin@example.com --password "Some8Strong!Pass"
    uv run python scripts/create_admin.py --email admin@example.com --password "..." --yes
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


def _confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N]: ").strip().lower() == "y"


async def create_admin(email: str, password: str, yes: bool) -> None:
    if len(password) < 8:
        print("Password must be at least 8 characters.", file=sys.stderr)
        raise SystemExit(1)

    if not yes and not _confirm(f"This will create an admin account for '{email}'. Continue?"):
        print("Aborted.")
        return

    settings = get_settings()
    engine = create_async_engine(settings.database_url, future=True)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            existing = await session.execute(select(User).where(User.email == email))
            if existing.scalar_one_or_none() is not None:
                print(f"A user with email '{email}' already exists.", file=sys.stderr)
                raise SystemExit(1)

            admin = User(
                email=email,
                hashed_password=hash_password(password),
                role=UserRole.ADMIN,
                is_verified=True,
                is_active=True,
            )
            session.add(admin)
            await session.commit()

        print(f"Created admin '{email}'.")
    finally:
        await engine.dispose()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--email", required=True, help="Email for the new admin account.")
    parser.add_argument("--password", required=True, help="Password for the new admin account (min 8 chars).")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip the confirmation prompt.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    asyncio.run(create_admin(args.email, args.password, args.yes))


if __name__ == "__main__":
    main()
