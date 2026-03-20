import os
import re

def rename_dates_in_audio_files(folder_path):
    if not os.path.isdir(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return
    
    for filename in os.listdir(folder_path):
        # Match pattern: "Oct 26, 2023"
        # We'll look for a 3-letter or more month, then space, then day, comma, space, year
        date_pattern = r'([A-Za-z]{3,9}) (\d{1,2}), (\d{4})'
        
        match = re.search(date_pattern, filename)
        if match:
            month, day, year = match.groups()
            # Create new date format: "Oct-26-2023"
            new_date = f"{month}-{int(day):02d}-{year}"
            
            # Replace old date with new date in filename
            new_filename = re.sub(date_pattern, new_date, filename)
            
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            # Rename the file if new name is different
            if new_filename != filename:
                if os.path.exists(new_path):
                    print(f"⚠️ Cannot rename '{filename}' because '{new_filename}' already exists.")
                else:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed '{filename}' → '{new_filename}'")
        else:
            print(f"Skipping '{filename}' (no matching date pattern)")

# Example usage:
audio_folder = r"D:\RA work\Company file download\Processed data\111. DUK - Duke Energy Corporation\Earnings Call Audio"
rename_dates_in_audio_files(audio_folder)
