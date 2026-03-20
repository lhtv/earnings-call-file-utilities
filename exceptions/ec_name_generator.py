import os
import re
import pandas as pd
from datetime import datetime
from dateutil import parser

# Set the folder path where the PDF files are located
folder_path = r"D:\RA work\Company file download\Processed data\59. SPGI - S&P Global\Earnings Call Transcript"  # <-- change this to your folder

# Get all PDF files in the folder
file_list = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

# List to hold file name mappings
file_mappings = []

for file in file_list:
    # Remove the file extension
    name, ext = os.path.splitext(file)
    
    # Expecting a name like:
    # "Wells Fargo & Company Q1 2008 Earnings Call, Apr 16, 2008"
    # Split the string by commas from the right, expecting two commas for the date portion
    parts = name.rsplit(',', 2)
    if len(parts) < 3:
        print(f"Skipping file (unexpected format): {file}")
        continue

    # Reassemble the date string from the last two parts
    date_str = parts[-2].strip() + ", " + parts[-1].strip()
    # The remaining part before the date
    left = parts[0].strip()

    # Extract the company name using a regex that looks for text before " Q"
    company_match = re.search(r"^(.*?)\s+Q\d+", left)
    if company_match:
        company = company_match.group(1).strip()
    else:
        company = left.strip()

    # Attempt to parse the date string using dateutil for flexibility
    try:
        date_obj = parser.parse(date_str)
        new_date_str = date_obj.strftime("%b-%d-%Y")  # Format as e.g., Apr-16-2008
    except (ValueError, parser.ParserError) as e:
        print(f"Date conversion error for file: {file}\nError: {e}")
        new_date_str = date_str  # fallback to original string if parsing fails

    # Create the new file name with the desired format
    new_file_name = f"{company} (NYSE_WFC) {new_date_str} - Audio{ext}"
    
    # Append the mapping to the list
    file_mappings.append({
        "original_name": file,
        "new_name": new_file_name
    })

# Create a DataFrame from the mappings and save to CSV and Excel
df = pd.DataFrame(file_mappings)
excel_path = os.path.join(folder_path, "file_names.xlsx")
df.to_excel(excel_path, index=False)

print(f"Mapping saved to:\n{excel_path}")
