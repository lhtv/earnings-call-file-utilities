import os
import re
import pandas as pd
from collections import defaultdict
import datetime

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

        # Apply the same cleaning function to the Excel names:
        df["Company Name Clean"] = df["Company Name"].astype(str).apply(clean_company_name)

        return dict(zip(df["Company Name Clean"], df["Primary ISIN"]))
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return {}

def extract_transcript_info(transcript_folder):
    """
    Returns:
      transcript_info[company_clean][audio_date_str] = (year, quarter)
    where audio_date_str is YYYYMMDD derived from the transcript filename.
    """
    info = defaultdict(dict)
    for fn in os.listdir(transcript_folder):
        m = re.search(r'Q([1-4])\s*(\d{4})', fn, re.IGNORECASE)
        if not m:
            continue
        quarter = f"Q{m.group(1)}"
        year    = m.group(2)

        d = re.search(r'([A-Za-z]{3,9})[-\s]*(\d{1,2}),?[-\s]*(\d{4})', fn)
        if not d:
            continue
        mon, day, yr = d.groups()
        day = int(day)
        dt = None
        for fmt in ("%b", "%B"):
            try:
                dt = datetime.datetime.strptime(f"{mon} {day} {yr}", f"{fmt} %d %Y")
                break
            except ValueError:
                continue
        if not dt:
            continue
        date_str = dt.strftime("%Y%m%d")

        cm = re.match(r'^(.*?)(?=\s+Q[1-4])', fn)
        if not cm:
            continue
        comp = clean_company_name(cm.group(1))

        info[comp][date_str] = (year, quarter)
    return info

def extract_audio_metadata(fn):
    """
    Returns (company_clean, date_str) from an audio filename,
    where date_str is YYYYMMDD or None.
    """
    cm = re.match(r'(.+?)\s*\((?:NasdaqGS|NYSE|OTC|AMEX)[ _]?[A-Z]+\)', fn)
    if not cm:
        return None, None
    comp = clean_company_name(cm.group(1))

    d = re.search(r'([A-Za-z]{3,9})[-\s]*(\d{1,2}),?[-\s]*(\d{4})', fn)
    if not d:
        return comp, None
    mon, day, yr = d.groups()
    day = int(day)
    dt = None
    for fmt in ("%b", "%B"):
        try:
            dt = datetime.datetime.strptime(f"{mon} {day} {yr}", f"{fmt} %d %Y")
            break
        except ValueError:
            continue
    if not dt:
        return comp, None
    return comp, dt.strftime("%Y%m%d")

def rename_audio_files(audio_folder, transcript_info, isin_map):
    # list only files
    files = [f for f in sorted(os.listdir(audio_folder))
             if os.path.isfile(os.path.join(audio_folder, f))]

    # 1) collect and group by transcript-derived quarter/year
    groups = defaultdict(list)
    for fn in files:
        comp, date_str = extract_audio_metadata(fn)
        if not comp or not date_str:
            print(f"❌ Skipping '{fn}': can't parse company or date")
            continue

        mapping = transcript_info.get(comp, {})
        if date_str not in mapping:
            print(f"❌ Skipping '{fn}': no transcript for {comp} on {date_str}")
            continue
        year, quarter = mapping[date_str]

        groups[(comp, year, quarter)].append((fn, date_str))

    # 2) rename
    for (comp, year, quarter), items in groups.items():
        isin = isin_map.get(comp)
        if not isin:
            print(f"⚠️ No ISIN for '{comp}', skipping")
            continue

        multiple = len(items) > 1
        for fn, date_str in items:
            ext = os.path.splitext(fn)[1]
            if multiple:
                new_fn = f"{isin}_{year}_{quarter}_Earnings Call Audio_{date_str}{ext}"
            else:
                new_fn = f"{isin}_{year}_{quarter}_Earnings Call Audio{ext}"

            oldp = os.path.join(audio_folder, fn)
            newp = os.path.join(audio_folder, new_fn)
            if os.path.exists(newp):
                print(f"⚠️ Skipping, exists: {new_fn}")
                continue
            try:
                os.rename(oldp, newp)
                print(f"✅ {fn} → {new_fn}")
            except Exception as e:
                print(f"❌ Error renaming '{fn}': {e}")

# === Usage ===
excel_path   = r"D:\RA work\Company Screening Report.xlsx"
trans_folder = r"D:\RA work\Company file download\Processed data\189. DLR - Digital Realty Trust\Earnings Call Transcript"
audio_folder = r"D:\RA work\Company file download\Processed data\189. DLR - Digital Realty Trust\Earnings Call Audio"

isin_map   = load_isin_mapping(excel_path)
trans_info = extract_transcript_info(trans_folder)
rename_audio_files(audio_folder, trans_info, isin_map)
