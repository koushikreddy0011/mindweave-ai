"""Database schema and table verification script for MindWeave AI."""

import asyncio
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import engine

EXPECTED_TABLES = [
    "users",
    "workspaces",
    "mindmaps",
    "nodes",
    "edges",
    "alembic_version",
]


async def verify_database_schema() -> int:
    """Verify presence of expected tables, foreign key cascades, and Alembic revision."""
    print("=" * 60)
    print("MindWeave AI — Database Schema Verification")
    print("=" * 60)

    try:
        async with engine.connect() as conn:
            # 1. Fetch all public tables
            table_query = text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
            )
            result = await conn.execute(table_query)
            existing_tables = {row[0] for row in result.fetchall()}

            print(f"\n[+] Connected to database: {engine.url.database} ({engine.url.host}:{engine.url.port})")
            print(f"[+] Total public tables found: {len(existing_tables)}\n")

            # 2. Check each expected table
            all_present = True
            for table in EXPECTED_TABLES:
                if table in existing_tables:
                    print(f"  [✓] Table '{table}' exists.")
                else:
                    print(f"  [✗] Table '{table}' is MISSING.")
                    all_present = False

            # 3. Check Alembic active migration revision
            if "alembic_version" in existing_tables:
                rev_query = text("SELECT version_num FROM alembic_version;")
                rev_result = await conn.execute(rev_query)
                row = rev_result.fetchone()
                current_rev = row[0] if row else "None (table empty)"
                print(f"\n[+] Current Alembic Revision: {current_rev}")
            else:
                print("\n[!] 'alembic_version' table not found. Migrations have not been applied.")

            # 4. Check foreign key cascade rules
            fk_query = text(
                """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.referential_constraints AS rc
                    ON tc.constraint_name = rc.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.column_name;
                """
            )
            fk_result = await conn.execute(fk_query)
            fk_rows = fk_result.fetchall()

            print(f"\n[+] Foreign Key Constraints & Cascade Rules ({len(fk_rows)} found):")
            for row in fk_rows:
                status = "[✓]" if row.delete_rule == "CASCADE" else "[!]"
                print(
                    f"  {status} {row.table_name}.{row.column_name} -> "
                    f"{row.foreign_table_name}.{row.foreign_column_name} (ON DELETE {row.delete_rule})"
                )

            print("\n" + "=" * 60)
            if all_present:
                print("[SUCCESS] All required domain tables and migrations are present.")
                print("=" * 60)
                return 0
            else:
                print("[FAILURE] Schema verification failed. Some required tables are missing.")
                print("=" * 60)
                return 1

    except Exception as exc:
        print(f"\n[ERROR] Failed to connect or verify schema: {exc}")
        print("\nTroubleshooting:")
        print("  1. Verify Docker PostgreSQL container is running: docker compose ps")
        print("  2. Verify credentials in backend/.env or backend/.env.example")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(verify_database_schema())
    sys.exit(exit_code)
