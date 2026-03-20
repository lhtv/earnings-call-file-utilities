import os
import re
import pandas as pd

def clean_company_name(name):
    """Standardizes company names: removes punctuation, parentheses, and lowercases."""
    name = re.sub(r'\s*\(.*?\)', '', name)  # remove parentheses content
    name = re.sub(r'[^\w\s]', '', name)     # remove punctuation
    name = re.sub(r'\s+', ' ', name)        # normalize whitespace
    return name.lower().strip()

def load_isin_mapping(excel_path):
    """Loads ISIN data from Excel and cleans company names for lookup."""
    try:
        df = pd.read_excel(excel_path)

        # Strip all columns of extra space
        df.columns = df.columns.str.strip()

        if "Company Name" not in df.columns or "Primary ISIN" not in df.columns:
            raise KeyError("Required columns 'Company Name' or 'Primary ISIN' not found in the Excel file.")

        # Clean and normalize company names
        df["Company Name"] = df["Company Name"].astype(str).apply(clean_company_name)

        # Create dictionary {cleaned company name: Primary ISIN}
        company_to_isin = dict(zip(df["Company Name"], df["Primary ISIN"]))

        print("\n🔍 ISIN Mapping Keys (first 10):")
        for k in list(company_to_isin.keys())[:10]:
            print(f"'{k}'")

        return company_to_isin

    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return {}

def extract_transcript_info(transcript_folder):
    """Extracts quarter, year, and exact date from transcript files."""
    transcript_info = {}

    if not os.path.isdir(transcript_folder):
        print(f"❌ Error: Transcript folder '{transcript_folder}' does not exist.")
        return transcript_info

    transcript_files = sorted(os.listdir(transcript_folder))

    for filename in transcript_files:
        match = re.search(r'Q([1-4])\s*(\d{4})', filename, re.IGNORECASE)
        if not match:
            continue

        quarter, year = match.groups()
        quarter = f"Q{quarter}"

        # Extract date (e.g., Feb 6, 2008 or Feb-6-2008)
        date_match = re.search(r'([A-Za-z]{3,9})[-\s]*(\d{1,2}),?[-\s]*(\d{4})', filename)
        if not date_match:
            continue
        month, day, transcript_year = date_match.groups()
        transcript_date = f"{month}-{int(day):02d}-{transcript_year}".lower().strip()

        # Extract company name from beginning until a space before "QX"
        company_match = re.match(r'^(.*?)(?=\s+Q[1-4])', filename)
        company_name = company_match.group(1) if company_match else None

        if company_name:
            company_name_clean = clean_company_name(company_name)
            if company_name_clean not in transcript_info:
                transcript_info[company_name_clean] = {}
            transcript_info[company_name_clean][transcript_date] = (year, quarter)

    return transcript_info

def rename_audio_files(audio_folder, transcript_info, isin_mapping):
    """Renames audio files based on transcript quarter & ISIN mapping."""
    if not os.path.isdir(audio_folder):
        print(f"❌ Error: Audio folder '{audio_folder}' does not exist.")
        return

    audio_files = sorted(os.listdir(audio_folder))

    for filename in audio_files:
        # Extract company name from audio file
        company_match = re.match(r'(.+?)\s*\((NasdaqGS|NYSE|OTC|AMEX)[_ ]?[A-Z]+\)', filename)
        company_name = company_match.group(1) if company_match else None

        if not company_name:
            print(f"⚠️ Skipping {filename} (Company name not found)")
            continue

        company_name_clean = clean_company_name(company_name)
        print(f"\n🔎 Looking up ISIN for: '{company_name_clean}'")

        # Extract date from audio filename
        date_match = re.search(r'([A-Za-z]{3})-(\d{1,2})-(\d{4})', filename)
        if not date_match:
            print(f"⚠️ Skipping {filename} (No valid date found)")
            continue
        month, day, year_from_audio = date_match.groups()
        audio_date = f"{month}-{int(day):02d}-{year_from_audio}".lower().strip()

        # Check for matching transcript
        if company_name_clean not in transcript_info or audio_date not in transcript_info[company_name_clean]:
            print(f"❌ Skipping {filename} (No matching transcript found for {company_name} on {audio_date})")
            continue

        # Get year and quarter from transcript
        transcript_year, quarter = transcript_info[company_name_clean][audio_date]

        # Get ISIN
        primary_isin = isin_mapping.get(company_name_clean)
        if not primary_isin:
            print(f"⚠️ Skipping {filename} (ISIN not found for {company_name})")
            continue

        # Build new filename
        new_name = f"{primary_isin}_{transcript_year}_{quarter}_Earnings Call Audio{os.path.splitext(filename)[1]}"
        old_path = os.path.join(audio_folder, filename)
        new_path = os.path.join(audio_folder, new_name)

        if os.path.exists(new_path):
            print(f"⚠️ Skipping {filename} (Already correctly named)")
        else:
            try:
                os.rename(old_path, new_path)
                print(f"✅ Renamed: {filename} → {new_name}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")

# Define file paths
excel_path = r"D:\RA work\Company Screening Report.xlsx"
transcript_folder = r"D:\RA work\Company file download\Processed data\168. AFL - Aflac Incorporated\Earnings Call Transcript"
audio_folder = r"D:\RA work\Company file download\Processed data\168. AFL - Aflac Incorporated\Earnings Call Audio"

# Run the process
isin_mapping = load_isin_mapping(excel_path)
transcript_info = extract_transcript_info(transcript_folder)
rename_audio_files(audio_folder, transcript_info, isin_mapping)
