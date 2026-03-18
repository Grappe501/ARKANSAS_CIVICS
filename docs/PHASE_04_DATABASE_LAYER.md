
Phase 04 — Database Infrastructure

This phase introduces:

• PostgreSQL support
• migration engine
• schema versioning
• API server scaffold
• production database configuration

Install Steps

1. Copy files into project directories.
2. Install dependencies:

pip install psycopg2-binary flask

3. Create database:

createdb arkansas_civics

4. Run migration:

python scripts/build_phase_04_database.py

This will automatically apply schema migrations.
