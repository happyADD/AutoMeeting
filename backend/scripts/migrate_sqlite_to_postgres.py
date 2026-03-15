#!/usr/bin/env python3
"""
SQLite to PostgreSQL migration script for AutoMeeting.

Usage:
    # Export from SQLite
    python -m scripts.migrate_sqlite_to_postgres --export

    # Import to PostgreSQL
    python -m scripts.migrate_sqlite_to_postgres --import --target "postgresql+asyncpg://user:pass@host/dbname"

    # Full migration (export + import)
    python -m scripts.migrate_sqlite_to_postgres --migrate --target "postgresql+asyncpg://user:pass@host/dbname"
"""
import argparse
import asyncio
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.models.counselor import Counselor
from app.models.slot_template import SlotTemplate
from app.models.appointment import Appointment


class Base(DeclarativeBase):
    pass


class MigrationManager:
    """Manages SQLite to PostgreSQL migration."""

    def __init__(self, source_url: str, target_url: str = None):
        self.source_url = source_url or "sqlite+aiosqlite:///./automeeting.db"
        self.target_url = target_url
        self.data: Dict[str, List[Dict[str, Any]]] = {}

    async def export_from_sqlite(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all data from SQLite database."""
        print(f"Exporting from: {self.source_url}")

        engine = create_async_engine(self.source_url, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            # Export Counselors
            result = await session.execute(select(Counselor))
            counselors = result.scalars().all()
            self.data["counselors"] = [
                {
                    "id": c.id,
                    "employee_id": c.employee_id,
                    "name": c.name,
                    "email": c.email,
                    "is_active": c.is_active,
                }
                for c in counselors
            ]
            print(f"  Exported {len(counselors)} counselors")

            # Export SlotTemplates
            result = await session.execute(select(SlotTemplate))
            templates = result.scalars().all()
            self.data["slot_templates"] = [
                {
                    "id": t.id,
                    "period": t.period,
                    "hour": t.hour,
                }
                for t in templates
            ]
            print(f"  Exported {len(templates)} slot templates")

            # Export Appointments
            result = await session.execute(select(Appointment))
            appointments = result.scalars().all()
            self.data["appointments"] = [
                {
                    "id": a.id,
                    "counselor_id": a.counselor_id,
                    "appointment_date": a.appointment_date.isoformat() if a.appointment_date else None,
                    "period": a.period,
                    "hour": a.hour,
                    "content": a.content,
                    "contact_name": a.contact_name,
                    "contact_phone": a.contact_phone,
                    "contact_email": a.contact_email,
                    "status": a.status,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in appointments
            ]
            print(f"  Exported {len(appointments)} appointments")

        await engine.dispose()
        return self.data

    async def import_to_postgres(self, target_url: str = None):
        """Import data to PostgreSQL database."""
        target = target_url or self.target_url
        if not target:
            raise ValueError("Target database URL required")

        print(f"Importing to: {target}")

        engine = create_async_engine(target, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            # Create tables first
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Import Counselors
            for data in self.data.get("counselors", []):
                counselor = Counselor(
                    employee_id=data["employee_id"],
                    name=data["name"],
                    email=data["email"],
                    is_active=data["is_active"],
                )
                session.add(counselor)
            await session.commit()
            print(f"  Imported {len(self.data.get('counselors', []))} counselors")

            # Import SlotTemplates
            for data in self.data.get("slot_templates", []):
                template = SlotTemplate(
                    period=data["period"],
                    hour=data["hour"],
                )
                session.add(template)
            await session.commit()
            print(f"  Imported {len(self.data.get('slot_templates', []))} slot templates")

            # Import Appointments (need to map old IDs to new IDs)
            # First, get the max existing IDs
            result = await session.execute(select(Counselor))
            counselors = {c.employee_id: c.id for c in result.scalars().all()}

            for data in self.data.get("appointments", []):
                counselor_id = counselors.get(data.get("counselor_id"))
                if counselor_id:
                    appointment = Appointment(
                        counselor_id=counselor_id,
                        appointment_date=date.fromisoformat(data["appointment_date"]) if data.get("appointment_date") else None,
                        period=data["period"],
                        hour=data["hour"],
                        content=data["content"],
                        contact_name=data["contact_name"],
                        contact_phone=data.get("contact_phone"),
                        contact_email=data.get("contact_email"),
                        status=data.get("status", "confirmed"),
                        created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
                    )
                    session.add(appointment)
            await session.commit()
            print(f"  Imported {len(self.data.get('appointments', []))} appointments")

        await engine.dispose()
        print("Migration completed successfully!")

    async def migrate(self, target_url: str):
        """Full migration from SQLite to PostgreSQL."""
        await self.export_from_sqlite()
        await self.import_to_postgres(target_url)

    def save_to_file(self, filename: str = "migration_data.json"):
        """Save exported data to JSON file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to: {filename}")

    def load_from_file(self, filename: str = "migration_data.json"):
        """Load data from JSON file."""
        with open(filename, encoding="utf-8") as f:
            self.data = json.load(f)
        print(f"Data loaded from: {filename}")


async def main():
    parser = argparse.ArgumentParser(description="Migrate AutoMeeting database from SQLite to PostgreSQL")
    parser.add_argument("--export", action="store_true", help="Export SQLite data to JSON")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Import data to PostgreSQL")
    parser.add_argument("--migrate", action="store_true", help="Full migration (export + import)")
    parser.add_argument("--source", type=str, help="Source SQLite database URL")
    parser.add_argument("--target", type=str, help="Target PostgreSQL database URL")
    parser.add_argument("--file", type=str, default="migration_data.json", help="JSON file for export/import")

    args = parser.parse_args()

    manager = MigrationManager(args.source, args.target)

    if args.export:
        await manager.export_from_sqlite()
        manager.save_to_file(args.file)
    elif args.do_import:
        manager.load_from_file(args.file)
        await manager.import_to_postgres(args.target)
    elif args.migrate:
        if not args.target:
            print("Error: --target required for migration")
            sys.exit(1)
        await manager.migrate(args.target)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())