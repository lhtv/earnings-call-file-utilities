import os
import re

def pad_subfolder_names(root_dir):
    """
    Renames all immediate subfolders in `root_dir` by padding their leading number
    to three digits. E.g. "1. Foo" → "001. Foo", "80. Bar" → "080. Bar".
    Does not modify folder contents.
    """
    # Regex to capture leading number, the dot, and the rest of the name
    pattern = re.compile(r'^\s*(\d+)\.\s*(.+)$')

    for name in sorted(os.listdir(root_dir)):
        old_path = os.path.join(root_dir, name)
        if not os.path.isdir(old_path):
            continue

        m = pattern.match(name)
        if not m:
            # Skip any folder without a leading number-dot format
            continue

        num, rest = m.groups()
        padded = num.zfill(3)                # pad to 3 digits
        new_name = f"{padded}. {rest}"
        new_path = os.path.join(root_dir, new_name)

        if old_path != new_path:
            try:
                os.rename(old_path, new_path)
                print(f"✅ Renamed: '{name}' → '{new_name}'")
            except Exception as e:
                print(f"❌ Error renaming '{name}': {e}")

if __name__ == "__main__":
    # --- Customize this path to your parent folder ---
    parent_folder = r"D:\RA work\Company file download\Raw data - DO NOT TOUCH"
    # -----------------------------------------------
    pad_subfolder_names(parent_folder)
