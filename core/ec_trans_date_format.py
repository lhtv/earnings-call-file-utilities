import os
import re

def normalize_filenames(folder_path):
    """
    Renames all files in the folder to:
    1. Use the date format 'Aug 12, 2010' instead of 'Aug-12-2010'.
    2. Remove any double spaces in filenames.
    """
    if not os.path.isdir(folder_path):
        print("Error: The folder does not exist.")
        return

    files = os.listdir(folder_path)

    for filename in files:
        old_path = os.path.join(folder_path, filename)

        # Ensure it's a file
        if not os.path.isfile(old_path):
            continue

        new_filename = filename  # Start with the original filename

        # Match pattern for file names containing a date with a dash (e.g., "Aug-12-2010")
        date_match = re.search(r'([A-Za-z]+)-(\d{1,2})-(\d{4})', filename)
        if date_match:
            short_month, day, year = date_match.groups()
            new_date_format = f"{short_month} {int(day)}, {year}"  # Convert to 'Aug 12, 2010'
            new_filename = new_filename.replace(date_match.group(0), new_date_format)

        # Replace double spaces with a single space
        new_filename = re.sub(r'\s{2,}', ' ', new_filename)  # Fixes any double or extra spaces

        new_path = os.path.join(folder_path, new_filename)

        # Debugging prints to check what's happening
        # print(f"\n🔹 Processing: {filename}")
        # print(f"   Old Path: {old_path}")
        # print(f"   New Path: {new_path}")

        if old_path != new_path:
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} → {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")
        else:
            print("⚠ No renaming needed (filename already correct)")

# Example Usage
folder_path = r"D:\RA work\Company file download\Processed data\189. DLR - Digital Realty Trust\Earnings Call Transcript"
normalize_filenames(folder_path)
