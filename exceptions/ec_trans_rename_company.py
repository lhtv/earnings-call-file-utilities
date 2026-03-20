import os

# === Configuration ===
folder_path = r"D:\RA work\Company file download\Processed data\092. ETN - Eaton Corporation\Earnings Call Transcript"  # <- Change this to your folder
old_company_name = "Marsh McLennan Companies, Inc."
new_company_name = "Marsh & McLennan Companies, Inc."

# === Renaming Logic ===
for filename in os.listdir(folder_path):
    if old_company_name in filename:
        new_filename = filename.replace(old_company_name, new_company_name)
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)
        os.rename(old_file_path, new_file_path)
        print(f"Renamed: {filename} -> {new_filename}")
