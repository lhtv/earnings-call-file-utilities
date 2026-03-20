import os
import re

def normalize_audio_filenames(folder_path):
    """
    Renames audio files to:
    - Add a comma before 'Inc.', 'Corp.', 'Ltd.', 'LLC', 'S.A.', etc. (if missing).
    - Avoids inserting commas before parts of the company name like 'Group'.
    """
    if not os.path.isdir(folder_path):
        print("Error: The folder does not exist.")
        return

    files = os.listdir(folder_path)

    for filename in files:
        old_path = os.path.join(folder_path, filename)

        if not os.path.isfile(old_path) or not filename.lower().endswith(('.mp3', '.wav')):
            continue

        new_filename = filename

        # Fix: match only if suffix is not already preceded by a comma and is at a word boundary
        new_filename = re.sub(
            r'(?<!,\s)(?<=\b)(?P<name>.*?)\s+(?P<suffix>Inc\.|Corp\.|Ltd\.|LLC|S\.A\.)',
            lambda m: f"{m.group('name')}, {m.group('suffix')}",
            new_filename
        )

        new_path = os.path.join(folder_path, new_filename)

        if old_path != new_path:
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} → {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")
        else:
            print(f"⚠ No renaming needed for: {filename}")

# Example usage
folder_path = r"D:\RA work\Company file download\Processed data\189. DLR - Digital Realty Trust\Earnings Call Audio"
normalize_audio_filenames(folder_path)
