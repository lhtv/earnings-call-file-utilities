import os 
import re
import pandas as pd
from collections import defaultdict
import datetime           # ← added

def clean_company_name(name):
    """Remove parentheses, punctuation; lowercase and trim."""
    name = re.sub(r'\s*\(.*?\)', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.lower().strip()

def load_isin_mapping(excel_path):
    """
    Loads the Excel file and returns {cleaned_company_name: ISIN}.
    Now uses clean_company_name() so '&' and other punctuation are removed.
    """
    try:
        df = pd.read_excel(excel_path)
        df.columns = df.columns.str.strip()
        if "Company Name" not in df.columns or "Primary ISIN" not in df.columns:
            raise KeyError("Required columns missing.")

        # Apply the same cleaning function to the Excel 'Company Name'
        df["Company Name Clean"] = df["Company Name"].astype(str).apply(clean_company_name)

        return dict(zip(df["Company Name Clean"], df["Primary ISIN"]))
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return {}

def extract_quarter_year(filename):
    """
    Returns (year, 'Qx') or (None, None).
    """
    m = re.search(r'Q([1-4])\s*(\d{4})', filename, re.IGNORECASE)
    return (m.group(2), f"Q{m.group(1)}") if m else (None, None)

def extract_pubdate(filename):
    """
    Returns date_str = 'YYYYMMDD' or None if not found.
    """
    m = re.search(r'([A-Za-z]{3,9})[-\s]*(\d{1,2}),?[-\s]*(\d{4})', filename)
    if not m:
        return None
    mon, day, yr = m.groups()
    day = int(day)
    # try abbreviated then full month name
    for fmt in ("%b", "%B"):
        try:
            dt = datetime.datetime.strptime(mon, fmt)
            month_num = dt.month
            return f"{yr}{month_num:02d}{day:02d}"
        except ValueError:
            continue
    return None

def rename_files(directory, company_to_isin):
    """
    1) Group all files by (company, year, quarter).
    2) Rename, appending date if group has ≥2 files.
    """
    if not os.path.isdir(directory):
        print("Error: Directory does not exist.")
        return

    # 1) Gather metadata
    groups = defaultdict(list)
    for fn in sorted(os.listdir(directory)):
        full = os.path.join(directory, fn)
        if not os.path.isfile(full):
            continue

        year, quarter = extract_quarter_year(fn)
        if not year:
            print(f"❌ Skipping {fn} (no quarter/year)")
            continue

        # extract and clean company
        comp_m = re.match(r'(.+?)\s*Q[1-4]', fn)
        if not comp_m:
            print(f"❌ Skipping {fn} (company not found)")
            continue
        comp_clean = clean_company_name(comp_m.group(1))

        date_str = extract_pubdate(fn)   # now YYYYMMDD or None
        groups[(comp_clean, year, quarter)].append((fn, date_str))

    # 2) Rename
    for (comp, year, quarter), files in groups.items():
        isin = company_to_isin.get(comp)
        if not isin:
            print(f"⚠️ No ISIN for '{comp}'")
            continue

        multiple = len(files) > 1
        for fn, date_str in files:
            base, ext = os.path.splitext(fn)
            if multiple and date_str:
                new = f"{isin}_{year}_{quarter}_Earnings Call Transcript_{date_str}{ext}"
            else:
                new = f"{isin}_{year}_{quarter}_Earnings Call Transcript{ext}"

            oldp = os.path.join(directory, fn)
            newp = os.path.join(directory, new)
            if os.path.exists(newp):
                print(f"⚠️ Skipping rename; target exists: {new}")
                continue
            try:
                os.rename(oldp, newp)
                print(f"✅ {fn} → {new}")
            except Exception as e:
                print(f"❌ Error renaming {fn}: {e}")

# Usage
directory_path = r"D:\RA work\Company file download\Processed data\189. DLR - Digital Realty Trust\Earnings Call Transcript"
excel_path     = r"D:\RA work\Company Screening Report.xlsx"

company_to_isin = load_isin_mapping(excel_path)
rename_files(directory_path, company_to_isin)
