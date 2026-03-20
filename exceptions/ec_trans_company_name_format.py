import os
import re

def extract_latest_company_name(folder_path):
    """
    Scans the folder to find the file with the largest year (4-digit number)
    that is either 2024 or 2025. From that file, it extracts the company name,
    assuming the company name is the portion before the quarter indicator (e.g., Q1, Q2, etc.).
    
    Args:
        folder_path (str): Path to the folder containing the files.
        
    Returns:
        str or None: The extracted company name if found; otherwise, None.
    """
    latest_year = 0
    latest_filename = None
    
    # Loop over all files in the folder.
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if not os.path.isfile(file_path):
            continue
        
        # Find all 4-digit numbers in the filename.
        years = re.findall(r'\b(\d{4})\b', filename)
        # Convert them to integers.
        years = [int(year) for year in years]
        if not years:
            continue
        
        max_year = max(years)
        # Consider only files whose latest year is 2024 or 2025.
        if max_year in (2024, 2025) and max_year > latest_year:
            latest_year = max_year
            latest_filename = filename

    if latest_filename:
        # Extract the company name from the start until a comma or space followed by a quarter indicator.
        # This regex looks for everything from the start until it sees optional comma/whitespace and Q1-Q4.
        match = re.search(r'^(.*?)(?=[,\s]*Q[1-4])', latest_filename)
        if match:
            company_name = match.group(1).strip()
            print(f"Max year found: {latest_year}")
            return company_name
    return None

def update_company_names(folder_path, new_company_name):
    """
    Renames files by:
      - Replacing the old company name (assumed to be at the start of the filename, up to the quarter indicator)
        with the new_company_name.
      - Normalizing the company name formatting by ensuring a comma is present before suffixes 
        (e.g., 'Inc.', 'Corp.', etc.) and by removing any extra comma before quarter/year designations.
    
    Args:
        folder_path (str): The folder containing the files.
        new_company_name (str): The company name to apply to all files.
    """
    if not os.path.isdir(folder_path):
        print("❌ Error: The folder does not exist.")
        return

    for filename in os.listdir(folder_path):
        old_path = os.path.join(folder_path, filename)
        if not os.path.isfile(old_path):
            continue

        new_filename = filename
        
        # Replace the portion before the quarter indicator using the same regex as extraction.
        new_filename = re.sub(
            r'^(.*?)(?=[,\s]*Q[1-4])', 
            new_company_name, 
            new_filename, 
            flags=re.IGNORECASE
        )
        
        # Normalize by ensuring there is a comma before company suffixes if missing.
        # Removed 'Group' from the list to avoid inserting an extra comma.
        new_filename = re.sub(
            r'(?<![,&])(\s+Inc\.|\s+Corp\.|\s+Ltd\.|\s+LLC|\s+Co\.|\s+S\.A\.)',
            r',\1',
            new_filename
        )
        
        # Remove any extra comma before quarter/year parts (e.g., turn ", Q1 2024" into " Q1 2024").
        new_filename = re.sub(
            r',\s*(Q[1-4])\s*(\d{4})', 
            r' \1 \2', 
            new_filename
        )
        
        new_path = os.path.join(folder_path, new_filename)
        if old_path != new_path:
            try:
                os.rename(old_path, new_path)
                print(f"✅ Renamed: {filename} → {new_filename}")
            except Exception as e:
                print(f"❌ Error renaming {filename}: {e}")
        else:
            print(f"⚠ No renaming needed for: {filename}")

def process_files(folder_path):
    """
    Orchestrates the process:
      - Extracts the latest company name from the file with the largest year (if it is 2024 or 2025).
      - Uses that company name to update all filenames in the folder.
    
    Args:
        folder_path (str): The folder containing the files.
    """
    new_company = extract_latest_company_name(folder_path)
    if new_company:
        print(f"Extracted company name: {new_company}")
        update_company_names(folder_path, new_company)
    else:
        print("❌ No file with year 2024 or 2025 found to extract a company name.")

# Example Usage:
folder_path = r"D:\RA work\Company file download\Processed data\80. AMAT - Applied Materials\Earnings Call Transcript"  # Update this path as needed
process_files(folder_path)
