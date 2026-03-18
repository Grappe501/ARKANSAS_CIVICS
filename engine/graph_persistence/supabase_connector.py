from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

try:
    from supabase import Client, create_client
except Exception:  # pragma: no cover
    Client = Any  # type: ignore
    create_client = None  # type: ignore


@dataclass
class SupabaseSettings:
    url: str
    service_key: str
    schema: str = "public"

    @classmethod
    def from_env(cls) -> "SupabaseSettings":
        url = os.getenv("SUPABASE_URL", "").strip()
        service_key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
        schema = os.getenv("SUPABASE_DB_SCHEMA", "public").strip() or "public"

        missing = [
            name
            for name, value in {
                "SUPABASE_URL": url,
                "SUPABASE_SERVICE_KEY": service_key,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
        return cls(url=url, service_key=service_key, schema=schema)


class SupabaseConnector:
    def __init__(self, settings: SupabaseSettings | None = None) -> None:
        self.settings = settings or SupabaseSettings.from_env()
        if create_client is None:
            raise RuntimeError(
                "supabase package is not installed. Install with: pip install supabase python-dotenv"
            )
        self.client: Client = create_client(self.settings.url, self.settings.service_key)

    def upsert(self, table: str, records: list[dict[str, Any]], on_conflict: str) -> dict[str, Any]:
        if not records:
            return {"table": table, "rows": 0}
        result = self.client.table(table).upsert(records, on_conflict=on_conflict).execute()
        data = getattr(result, "data", None) or []
        return {"table": table, "rows": len(records), "returned": len(data)}

    def select_relationships(
        self,
        relationship_type: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        query = self.client.table("civic_edges").select("*").limit(limit)
        if relationship_type:
            query = query.eq("relationship_type", relationship_type)
        result = query.execute()
        return getattr(result, "data", None) or []

    def healthcheck(self) -> dict[str, Any]:
        result = self.client.table("civic_nodes").select("id", count="exact").limit(1).execute()
        return {
            "ok": True,
            "schema": self.settings.schema,
            "node_count": getattr(result, "count", None),
        }
