from pathlib import Path
import shutil
import datetime

ROOT = Path(__file__).resolve().parents[1]

ARCHIVE = ROOT / "archive"
ARCHIVE.mkdir(exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = ARCHIVE / f"pre_cleanup_backup_{timestamp}"
backup_dir.mkdir(parents=True)

print("\n================================================")
print(" Arkansas Civics Repository Cleanup")
print("================================================\n")

print("Creating safety backup...")

# ------------------------------------------------
# Folders to archive
# ------------------------------------------------

folders_to_archive = [
    "arkansas_civics_engine",
    "engine_update",
    "backups"
]

# ------------------------------------------------
# Script patterns to archive
# ------------------------------------------------

script_patterns = [
    "generate_*",
    "seed_chapter_*",
    "scaffold_*"
]

scripts_dir = ROOT / "scripts"


# ------------------------------------------------
# Backup function
# ------------------------------------------------

def backup_item(path):

    if not path.exists():
        return

    target = backup_dir / path.name

    if path.is_dir():
        shutil.copytree(path, target)
    else:
        shutil.copy2(path, target)

    print(f"Backup created: {path}")


# ------------------------------------------------
# Archive function
# ------------------------------------------------

def archive_item(path):

    if not path.exists():
        return

    target = ARCHIVE / path.name

    if target.exists():
        target = ARCHIVE / f"{path.name}_{timestamp}"

    shutil.move(str(path), str(target))

    print(f"Archived: {path}")


# ------------------------------------------------
# Archive duplicate engine folders
# ------------------------------------------------

print("\nArchiving duplicate engine folders...\n")

for folder in folders_to_archive:

    p = ROOT / folder

    if p.exists():

        backup_item(p)
        archive_item(p)


# ------------------------------------------------
# Archive experimental scripts
# ------------------------------------------------

print("\nArchiving experimental scripts...\n")

for pattern in script_patterns:

    for file in scripts_dir.glob(pattern):

        backup_item(file)
        archive_item(file)


# ------------------------------------------------
# Summary
# ------------------------------------------------

print("\n================================================")
print(" CLEANUP COMPLETE")
print("================================================\n")

print("Backup created at:")
print(backup_dir)

print("\nArchived items located in:")
print(ARCHIVE)

print("\nRemaining core system:")

core_paths = [
    "engine/",
    "scripts/",
    "content/",
    "apps/editor-dashboard/",
    "exports/",
    "netlify/"
]

for p in core_paths:
    print("  ", p)

print("\nRepository cleanup successful.\n")