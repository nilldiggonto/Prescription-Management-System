#!/usr/bin/env python3
"""Database maintenance CLI (dev/local use only).

Always run from the backend/ directory so Settings picks up backend/.env:

    cd backend
    uv run python scripts/db_clean.py list
    uv run python scripts/db_clean.py truncate email_verification_tokens
    uv run python scripts/db_clean.py truncate users --cascade
    uv run python scripts/db_clean.py delete-user --email doctor@example.com
    uv run python scripts/db_clean.py reset --yes
    uv run python scripts/db_clean.py reset --test-db --yes
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.exc import DBAPIError  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine  # noqa: E402

import app.models  # noqa: E402, F401  registers all models on Base.metadata
from app.core.config import get_settings  # noqa: E402
from app.core.database import Base  # noqa: E402

ALL_TABLES = [t.name for t in Base.metadata.sorted_tables]


def _confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N]: ").strip().lower() == "y"


def _quote(table: str) -> str:
    return f'"{table}"'


async def cmd_list() -> None:
    print("Tables managed by this app:")
    for name in ALL_TABLES:
        print(f"  - {name}")


async def cmd_truncate(engine: AsyncEngine, table: str, cascade: bool, yes: bool) -> None:
    if table not in ALL_TABLES:
        print(f"Unknown table '{table}'. Known tables: {', '.join(ALL_TABLES)}", file=sys.stderr)
        raise SystemExit(1)

    verb = "TRUNCATE ... CASCADE (also wipes dependent rows in related tables)" if cascade else "TRUNCATE"
    if not yes and not _confirm(f"This will {verb} on table '{table}'. Continue?"):
        print("Aborted.")
        return

    stmt = f"TRUNCATE TABLE {_quote(table)} RESTART IDENTITY" + (" CASCADE" if cascade else "")
    try:
        async with engine.begin() as conn:
            await conn.execute(text(stmt))
    except DBAPIError as exc:
        print(f"Truncate failed: {exc.orig}\nHint: if this is a foreign-key error, retry with --cascade.", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Truncated '{table}'{' (cascaded)' if cascade else ''}.")


async def cmd_delete_user(engine: AsyncEngine, email: str, yes: bool) -> None:
    if not yes and not _confirm(
        f"This will delete user '{email}' and all rows referencing it (via ON DELETE CASCADE). Continue?"
    ):
        print("Aborted.")
        return

    async with engine.begin() as conn:
        result = await conn.execute(text("DELETE FROM users WHERE email = :email"), {"email": email})

    if result.rowcount == 0:
        print(f"No user found with email '{email}'.")
    else:
        print(f"Deleted user '{email}' and related rows.")


async def cmd_reset(engine: AsyncEngine, yes: bool) -> None:
    if not yes and not _confirm(f"This will TRUNCATE ALL {len(ALL_TABLES)} application table(s). Continue?"):
        print("Aborted.")
        return

    quoted_tables = ", ".join(_quote(t) for t in ALL_TABLES)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {quoted_tables} RESTART IDENTITY CASCADE"))

    print(f"Reset {len(ALL_TABLES)} table(s): {', '.join(ALL_TABLES)}")


def build_parser() -> argparse.ArgumentParser:
    # Shared options so they can be passed either before or after the subcommand,
    # e.g. both `db_clean.py --yes delete-user ...` and `db_clean.py delete-user --yes ...` work.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--test-db", action="store_true", help="Target the test database instead of the dev one.")
    common.add_argument("--database-url", help="Override the database URL entirely.")
    common.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts.")

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[common]
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List all tables managed by this app.", parents=[common])

    truncate_parser = subparsers.add_parser("truncate", help="Truncate a single table.", parents=[common])
    truncate_parser.add_argument("table", help="Table name to truncate.")
    truncate_parser.add_argument(
        "--cascade", action="store_true", help="Also wipe rows in tables that have a FK referencing this one."
    )

    delete_user_parser = subparsers.add_parser(
        "delete-user", help="Delete one user (and related rows) by email.", parents=[common]
    )
    delete_user_parser.add_argument("--email", required=True, help="Email of the user to delete.")

    subparsers.add_parser("reset", help="Truncate ALL application tables (full reset).", parents=[common])

    return parser


async def async_main() -> None:
    args = build_parser().parse_args()
    settings = get_settings()

    if args.database_url:
        database_url = args.database_url
    elif args.test_db:
        if not settings.test_database_url:
            print("TEST_DATABASE_URL is not configured.", file=sys.stderr)
            raise SystemExit(1)
        database_url = settings.test_database_url
    else:
        database_url = settings.database_url

    engine = create_async_engine(database_url, future=True)
    try:
        if args.command == "list":
            await cmd_list()
        elif args.command == "truncate":
            await cmd_truncate(engine, args.table, args.cascade, args.yes)
        elif args.command == "delete-user":
            await cmd_delete_user(engine, args.email, args.yes)
        elif args.command == "reset":
            await cmd_reset(engine, args.yes)
    finally:
        await engine.dispose()


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()