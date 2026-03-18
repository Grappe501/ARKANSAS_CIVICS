from pathlib import Path
import json
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import time


class MigrationEngine:

    def __init__(self, project_root):
        self.project_root = Path(project_root)

        self.config_path = self.project_root / "config" / "database.json"
        self.migrations_dir = self.project_root / "database" / "migrations"

        if not self.config_path.exists():
            raise RuntimeError(f"Database config missing: {self.config_path}")

        if not self.migrations_dir.exists():
            raise RuntimeError(f"Migration directory missing: {self.migrations_dir}")

        self.db_config = self._load_config()

    # -----------------------------------------------------
    # Config
    # -----------------------------------------------------

    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -----------------------------------------------------
    # Database connection
    # -----------------------------------------------------

    def connect(self):

        retries = 3

        for attempt in range(retries):

            try:

                if "uri" in self.db_config:
                    return psycopg2.connect(
                        self.db_config["uri"],
                        cursor_factory=DictCursor,
                        connect_timeout=10
                    )

                return psycopg2.connect(
                    host=self.db_config["host"],
                    port=self.db_config.get("port", 5432),
                    dbname=self.db_config["database"],
                    user=self.db_config["user"],
                    password=self.db_config["password"],
                    sslmode=self.db_config.get("sslmode", "require"),
                    cursor_factory=DictCursor,
                    connect_timeout=10
                )

            except psycopg2.OperationalError:

                if attempt == retries - 1:
                    raise

                print("[WARN] Database connection failed, retrying...")
                time.sleep(2)

    # -----------------------------------------------------
    # Migration table
    # -----------------------------------------------------

    def ensure_migration_table(self, conn):

        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        with conn.cursor() as cur:
            cur.execute(query)

        conn.commit()

    # -----------------------------------------------------
    # Applied migrations
    # -----------------------------------------------------

    def applied_migrations(self, conn):

        with conn.cursor() as cur:
            cur.execute("SELECT migration_name FROM schema_migrations")
            rows = cur.fetchall()

        return {row["migration_name"] for row in rows}

    # -----------------------------------------------------
    # Apply migration
    # -----------------------------------------------------

    def apply_migration(self, conn, name, sql_script):

        print(f"Applying migration: {name}")

        try:

            with conn.cursor() as cur:

                cur.execute(sql_script)

                cur.execute(
                    "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
                    (name,)
                )

            conn.commit()

            print(f"[OK] Migration applied: {name}")

        except Exception:

            conn.rollback()

            print(f"[ERROR] Migration failed: {name}")

            raise

    # -----------------------------------------------------
    # Run migrations
    # -----------------------------------------------------

    def run(self):

        start = datetime.now()

        conn = self.connect()

        try:

            self.ensure_migration_table(conn)

            applied = self.applied_migrations(conn)

            migration_files = sorted(self.migrations_dir.glob("*.sql"))

            if not migration_files:
                print("[INFO] No migration files found.")
                return

            for file in migration_files:

                name = file.name

                if name in applied:
                    continue

                sql_script = file.read_text(encoding="utf-8")

                self.apply_migration(conn, name, sql_script)

            duration = (datetime.now() - start).total_seconds()

            print("\n--------------------------------------------")
            print(" DATABASE MIGRATIONS COMPLETE")
            print("--------------------------------------------")
            print(f"[INFO] Completed in {duration:.2f} seconds")

        finally:
            conn.close()