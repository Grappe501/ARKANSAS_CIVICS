import os
import shutil

SOURCE = r"C:\Users\User\Desktop\arkansas_civics\engine_update"
DEST = r"C:\Users\User\Desktop\arkansas_civics\ARKANSAS_CIVICS"

# folders we never overwrite automatically
PROTECTED_FOLDERS = {
    "content",
    "exports",
    "data",
    ".git",
    "tests"
}

def copy_tree(src, dst):
    for root, dirs, files in os.walk(src):

        rel_path = os.path.relpath(root, src)
        dest_path = os.path.join(dst, rel_path)

        folder_name = rel_path.split(os.sep)[0]

        if folder_name in PROTECTED_FOLDERS:
            print(f"⚠ Skipping protected folder: {folder_name}")
            continue

        os.makedirs(dest_path, exist_ok=True)

        for file in files:

            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_path, file)

            if os.path.exists(dst_file):
                print(f"⏩ Exists, skipping: {dst_file}")
            else:
                shutil.copy2(src_file, dst_file)
                print(f"✅ Copied: {dst_file}")


def main():
    print("\n--- Arkansas Civics Engine Merge ---\n")
    print(f"Source: {SOURCE}")
    print(f"Destination: {DEST}\n")

    if not os.path.exists(SOURCE):
        print("❌ Source folder does not exist.")
        return

    if not os.path.exists(DEST):
        print("❌ Destination folder does not exist.")
        return

    copy_tree(SOURCE, DEST)

    print("\n✔ Merge Complete\n")


if __name__ == "__main__":
    main()