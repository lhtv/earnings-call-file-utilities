import os
import re
import pandas as pd

def load_isin_mapping(excel_path):
    """
    Loads the Excel file and extracts a dictionary mapping cleaned company names to Primary ISINs.
    Cleans 'Company Name' by removing stock market symbols like (NasdaqGS:AAPL).
    """
    try:
        df = pd.read_excel(excel_path)

        # Clean 'Company Name' column (remove stock symbols)
        df['Cleaned Company Name'] = df['Company Name'].str.replace(r'\s*\(.*?\)', '', regex=True).str.lower().str.strip()

        # Create a mapping {cleaned_company_name: Primary ISIN}
        return dict(zip(df['Cleaned Company Name'], df['Primary ISIN']))

    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return {}

def extract_transcript_info(transcript_folder):
    """
    Reads transcript filenames and extracts the quarter, year, and formatted date.
    """
    transcript_info = {}

    if not os.path.isdir(transcript_folder):
        print("Error: Transcript folder does not exist.")
        return transcript_info

    transcript_files = [f for f in os.listdir(transcript_folder) if f.endswith(".pdf")]

    for filename in transcript_files:
        # Extract company name
        company_match = re.match(r'(.+?),\s*Q([1-4])\s*(\d{4})', filename)
        if not company_match:
            continue  # Skip if company or quarter/year is missing

        company_name, quarter, year = company_match.groups()
        quarter = f"Q{quarter}"

        # Extract date (fix formatting issue)
        date_match = re.search(r'([A-Za-z]{3})\s*(\d{1,2}),\s*(\d{4})', filename)
        if not date_match:
            continue  # Skip if no valid date

        short_month, day, year = date_match.groups()
        formatted_date = f"{short_month}-{day}-{year}"  # Store with DASH

        company_name_clean = company_name.lower().strip()
        if company_name_clean not in transcript_info:
            transcript_info[company_name_clean] = {}

        transcript_info[company_name_clean][formatted_date] = (year, quarter, short_month, day)

    return transcript_info


def rename_audio_files(audio_folder, transcript_info, isin_mapping):
    """
    Renames only audio files to match transcript data.
    Ensures correct quarter and year are applied based on transcript dates.
    """
    if not os.path.isdir(audio_folder):
        print("Error: Audio folder does not exist.")
        return

    audio_files = sorted([f for f in os.listdir(audio_folder) if os.path.isfile(os.path.join(audio_folder, f))])

    for filename in audio_files:
        # Extract company name from audio file
        company_match = re.match(r'(.+?)\s*\(NasdaqGS[_ ]?[A-Z]+\)', filename)
        company_name = company_match.group(1) if company_match else None

        if not company_name:
            print(f"Skipping {filename} (Company name not found)")
            continue

        company_name_clean = company_name.lower().strip()

        # Extract date from audio filename (e.g., "Jan-28-2020")
        date_match = re.search(r'([A-Za-z]{3})-(\d{1,2})-(\d{4})', filename)
        if not date_match:
            print(f"Skipping {filename} (No valid date found)")
            continue
        audio_date = f"{date_match.group(1)} {date_match.group(2)}, {date_match.group(3)}"

        # Ensure transcript exists for this company & date
        if company_name_clean not in transcript_info or audio_date not in transcript_info[company_name_clean]:
            print(f"Skipping {filename} (No matching transcript found for {company_name} on {audio_date})")
            continue

        # Extract correct year & quarter from matching transcript
        year, quarter = transcript_info[company_name_clean][audio_date]
        primary_isin = isin_mapping.get(company_name_clean)

        if not primary_isin:
            print(f"Skipping {filename} (ISIN not found for {company_name})")
            continue

        ext = os.path.splitext(filename)[1]  # Get file extension
        base_new_name = f"{primary_isin}_{year}_{quarter}_Earnings Call Audio"

        # Ensure unique file names
        new_name = base_new_name + ext
        new_path = os.path.join(audio_folder, new_name)
        counter = 1

        while os.path.exists(new_path):  # If file exists, add _1, _2, etc.
            new_name = f"{base_new_name}_{counter}{ext}"
            new_path = os.path.join(audio_folder, new_name)
            counter += 1

        old_path = os.path.join(audio_folder, filename)

        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} → {new_name}")
        except Exception as e:
            print(f"Error renaming {filename}: {e}")
    

# Example usage
transcript_folder = r"C:\Users\admin\Downloads\Company file download\Processed data\NVIDIA\Earnings Call Transcript"  # Change to actual transcript folder
audio_folder = r"C:\Users\admin\Downloads\Company file download\Processed data\NVIDIA\Earnings Call Audio"  # Change to actual audio folder
excel_path = r"C:\Users\admin\Downloads\Company Screening Report.xlsx"  # Change to your actual Excel file

# Load ISIN mapping
isin_mapping = load_isin_mapping(excel_path)

# Extract transcript information (quarter & year by date)
transcript_info = extract_transcript_info(transcript_folder)

# Rename only audio files based on transcript data
rename_audio_files(audio_folder, transcript_info, isin_mapping)

