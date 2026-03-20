import os
import re

def update_company_name_to_latest(folder_path):
    """
    Replace the beginning of filenames with the cleaned company name from a 2025 file.
    Preserves all commas and special characters in the company name.
    Preserves the rest of the filename (including commas in dates).
    """
    if not os.path.isdir(folder_path):
        print("❌ Folder does not exist.")
        return

    files = os.listdir(folder_path)
    new_company_name = None

    # Step 1: Extract company name from a 2025 file (including commas & &)
    for filename in files:
        match = re.search(r'^(.+?)\s*,?\s*Q[1-4]\s+2025', filename)
        if match:
            raw_name = match.group(1)
            new_company_name = raw_name.strip()  # <--- Keep commas & ampersand here!
            print(f"✅ Using company name from 2025 file: '{new_company_name}'")
            break

    if not new_company_name:
        print("❌ No 2025 file found. Cannot proceed.")
        return

    # Step 2: Rename all files with the new company name
    for filename in files:
        old_path = os.path.join(folder_path, filename)
        if not os.path.isfile(old_path):
            continue

        # Match files with company name and QX YYYY pattern
        match = re.search(r'^(.+?)\s*,?\s*(Q[1-4]\s+\d{4}.*)', filename)
        if not match:
            print(f"⚠️ Skipping unrecognized format: {filename}")
            continue

        old_company_part, rest_of_filename = match.groups()

        new_filename = f"{new_company_name} {rest_of_filename}"
        new_path = os.path.join(folder_path, new_filename)

        if filename == new_filename:
            print(f"✅ Already correct: {filename}")
            continue

        try:
            os.rename(old_path, new_path)
            print(f"🔄 Renamed: {filename} → {new_filename}")
        except Exception as e:
            print(f"❌ Error renaming {filename}: {e}")

# Example usage
folder_path = r"D:\RA work\Company file download\Processed data\189. DLR - Digital Realty Trust\Earnings Call Transcript"
update_company_name_to_latest(folder_path)
