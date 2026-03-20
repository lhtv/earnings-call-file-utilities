import os

def add_affixes_to_files(directory, prefix, suffix):
    """
    Renames every file in `directory` by adding `prefix` before its base name
    and `suffix` after its base name (but before the file extension).
    E.g. '20230115.mp3' → 'PREFIX_20230115_SUFFIX.mp3'
    """
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        return

    for fname in sorted(os.listdir(directory)):
        old_path = os.path.join(directory, fname)
        if not os.path.isfile(old_path):
            continue

        base, ext = os.path.splitext(fname)
        new_name = f"{prefix}{base}{suffix}{ext}"
        new_path = os.path.join(directory, new_name)

        if os.path.exists(new_path):
            print(f"⚠️ Skipping '{fname}': '{new_name}' already exists.")
            continue

        try:
            os.rename(old_path, new_path)
            print(f"✅ Renamed: '{fname}' → '{new_name}'")
        except Exception as e:
            print(f"❌ Couldn’t rename '{fname}': {e}")

if __name__ == "__main__":
    # --- Customize these three lines ---
    directory = r"D:\RA work\Company file download\Raw data - DO NOT TOUCH\091. MMC - Marsh & McLennan Companies\Earnings Call Audio"
    prefix    = "Marsh & McLennan Companies Inc. (NYSE_MMC) "   # text to prepend
    suffix    = " - Audio"  # text to append before the extension
    # ------------------------------------
    add_affixes_to_files(directory, prefix, suffix)
