import os
import re
import pandas as pd

def load_isin_mapping(excel_path):
    """
    Loads the Excel file and extracts a dictionary mapping cleaned company names to Primary ISINs.
    """
    try:
        df = pd.read_excel(excel_path)

        # Ensure column names are stripped of spaces
        df.columns = df.columns.str.strip()

        if "Company Name" not in df.columns or "Primary ISIN" not in df.columns:
            raise KeyError("Required columns 'Company Name' or 'Primary ISIN' not found in the Excel file.")

        # Create dictionary {cleaned company name: Primary ISIN}
        company_to_isin = dict(
            zip(df["Company Name"].str.replace(r'\s*\(.*?\)', '', regex=True).str.lower().str.strip(), 
                df["Primary ISIN"])
        )

        return company_to_isin

    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return {}

def extract_quarter_year(filename):
    """
    Extracts the quarter (Q1, Q2, Q3, Q4) and year (YYYY) from the filename.
    """
    match = re.search(r'Q([1-4])\s*(\d{4})', filename, re.IGNORECASE)
    if match:
        quarter, year = match.groups()
        return year, f"Q{quarter}"
    return None, None

def rename_files(directory, company_to_isin):
    """
    Renames transcript files based on extracted company name, year, quarter, and ISIN.
    """
    if not os.path.isdir(directory):
        print("Error: Directory does not exist.")
        return

    files = sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])

    for filename in files:
        print(f"\n🔍 Checking file: {filename}")  # Debug: Show filename being processed

        year, quarter = extract_quarter_year(filename)
        if not year or not quarter:
            print(f"❌ Skipping {filename} (No valid year/quarter found)")
            continue

        # Extract Company Name (everything before 'QX YYYY')
        company_match = re.match(r'(.+?)\s*Q[1-4]', filename)  # Adjusted regex pattern

        if not company_match:
            print(f"❌ Skipping {filename} (Company name not found - Regex failed)")
            continue

        company_name = company_match.group(1)
        print(f"✅ Extracted Company Name: {company_name}")  # Debugging output

        # Clean extracted company name for lookup
        company_name_clean = re.sub(r'\s*\(.*?\)', '', company_name).lower().strip()

        # Lookup ISIN using the cleaned company name
        primary_isin = company_to_isin.get(company_name_clean)

        if not primary_isin:
            print(f"❌ Skipping {filename} (No ISIN found for '{company_name_clean}')")
            continue

        ext = os.path.splitext(filename)[1]  # Get file extension
        new_name = f"{primary_isin}_{year}_{quarter}_Earnings Call Transcript{ext}"
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)

        try:
            os.rename(old_path, new_path)
            print(f"✅ Renamed: {filename} → {new_name}")
        except Exception as e:
            print(f"Error renaming {filename}: {e}")

# Example usage
directory_path = r"D:\RA work\Company file download\Processed data\082. COP - ConocoPhillips\Earnings Call Transcript"  # Change to your actual folder path
excel_path = r"D:\RA work\Company Screening Report.xlsx"  # Change to your actual Excel file

# Load ISIN mapping using Company Name
company_to_isin = load_isin_mapping(excel_path)

# Rename files based on ISIN lookup using Company Name
rename_files(directory_path, company_to_isin)
