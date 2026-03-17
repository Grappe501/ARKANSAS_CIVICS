import time
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"

BUILD_SCRIPT = ROOT / "scripts" / "build_all.py"


class ContentChangeHandler(FileSystemEventHandler):

    def on_modified(self, event):

        if event.is_directory:
            return

        if event.src_path.endswith(".md"):

            print("\n📄 Content change detected:")
            print(event.src_path)

            print("\n🔄 Rebuilding Arkansas Civics platform...\n")

            try:
                subprocess.run(
                    [sys.executable, BUILD_SCRIPT],
                    check=True
                )

                print("\n✅ Build complete\n")

            except subprocess.CalledProcessError:
                print("\n❌ Build failed\n")


def main():

    print("\n====================================")
    print(" Arkansas Civics Watch Mode")
    print("====================================\n")

    print("Watching content folder for changes:")
    print(CONTENT_DIR)
    print("\nEdit any segment file to trigger rebuild.\n")

    event_handler = ContentChangeHandler()
    observer = Observer()

    observer.schedule(event_handler, str(CONTENT_DIR), recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()