---
# Earnings Call File Utilities

Python utilities for standardising earnings call audio and transcript filenames from inconsistent Capital IQ source data.

## Overview

Capital IQ earnings call datasets do not always follow a consistent naming convention. In practice, filenames can vary across:

- company naming formats
- date formats
- file prefixes and suffixes
- transcript and audio naming patterns
- manually edited or partially standardised source files

This repository was built to handle those inconsistencies in a practical workflow.

A key part of the process is that **transcript filenames are derived from audio filenames**.  
This means the audio standardisation step comes first, and transcript naming depends on the cleaned or matched audio file names.

---

## Filename Standardisation Logic

A key part of this project is the use of a **company screening report (Excel file)** containing ISIN codes to standardise filenames across both audio and transcript datasets.

The ISIN serves as the unique identifier to ensure consistent mapping between earnings call audio files and their corresponding transcripts.

---

### Source File Naming (Capital IQ)

The majority of the original files tend to follow inconsistent naming conventions:

**Audio files:**

`Company Name + Ticker + MMM-DD-YYYY - Audio`


Example:

`Apple Inc AAPL Jan-28-2023 - Audio`


**Transcript files:**

`Company Name + QX YYYY Earnings Call, MMM DD, YYYY`


Example:

`Apple Inc Q1 2023 Earnings Call, January 28, 2023`


---

### Standardised Naming Convention

Using the ISIN mapping from the company screening report, filenames are transformed into a consistent format:

**Audio:**

`ISIN_YYYY_QX_Earnings Call Audio`


Example:

`US0378331005_2023_Q1_Earnings Call Audio.mp3`


**Transcript:**

`ISIN_YYYY_QX_Earnings Call Transcript`


Example:

`US0378331005_2023_Q1_Earnings Call Transcript.txt`


---

### Why ISIN Mapping is Used

- Company names are not always consistent across files  
- Tickers may vary or be missing  
- Dates may be formatted differently  
- Audio and transcript files do not always align directly  

Using ISIN codes from the company screening report provides:
- a **stable, unique identifier**
- reliable matching between audio and transcript files
- consistent naming across the dataset

---

### Important Dependency

Transcript filename standardisation depends on the cleaned and standardised audio filenames.

As a result:
1. Audio files must be processed first  
2. Transcript files are then mapped and renamed using the corresponding audio filenames and ISIN mapping  

---

## Workflow Logic

The repository follows a linked workflow:

### Step 1: Standardise audio filenames
Audio files are cleaned first using the main audio scripts and, where needed, audio-specific exception-handling scripts.

### Step 2: Name transcript files based on audio filenames
Transcript filenames are then generated or corrected by relying on the standardised audio filenames as the reference.

### Step 3: Resolve exceptions
Because Capital IQ naming is inconsistent, additional scripts are included to fix edge cases such as:
- irregular date formats
- inconsistent company names
- prefix issues
- transcript and audio mismatches
- source-specific naming exceptions

---

## Naming Conventions Used in This Repository

The script names are kept in their original abbreviated form:

- `ec` = earnings call
- `audio` = audio file
- `trans` = transcript file
- `nc` = name change

Additional suffixes indicate the task performed by each script.

---

## Script Groups

### Core scripts
These scripts support the main workflow and should usually be run first.

- `ec_audio_nc.py`
- `ec_audio_nc_sf.py`
- `ec_trans_nc.py`

### Exception-handling scripts
These scripts are used when source data does not conform to the expected naming pattern.

#### Audio-related
- `ec_audio_date_format.py`
- `ec_audio_name_format.py`
- `ec_audio_prefix.py`

#### Transcript-related
- `ec_trans_date_format.py`
- `ec_trans_company_name_format.py`
- `ec_trans_name_format.py`
- `ec_trans_rename_company.py`

### Supporting utilities
Helper scripts used for generating names or reorganising folders.

- `ec_name_generator.py`
- `renumber_folder.py`

---

## Recommended Processing Order

### Audio processing
1. Run the main audio naming script
2. Inspect output for skipped or inconsistent files
3. Apply audio exception-handling scripts where necessary

### Transcript processing
1. Ensure audio filenames have already been standardised
2. Run transcript naming scripts using audio filenames as reference
3. Apply transcript exception-handling scripts for mismatches or naming errors

---

## Why transcript naming depends on audio filenames

In the source data, transcript files do not always contain enough consistent naming information on their own.  
The corresponding audio filenames provide the more reliable reference point for reconstructing or standardising transcript names.

Because of this dependency, transcript processing should not be treated as fully independent from audio processing.

---

## Why this project matters

Messy file naming is a real preprocessing problem in financial datasets.

This toolkit was built to reduce manual cleaning and make earnings call transcript and audio datasets more consistent and usable for downstream workflows such as:

- transcript-audio matching
- dataset organisation
- NLP preprocessing
- financial text analysis
- ESG-focused modelling workflows

---

## Future improvements

- convert hardcoded paths into command-line arguments
- add a dry-run mode before renaming files
- add logging for renamed, skipped, and failed files
- create a single wrapper script for the full workflow
- add validation checks between transcript and audio filenames
- add unit tests for key naming rules

---

## Tech stack

- Python
- pandas
- os
- pathlib
- regular expressions

---

## Author

Linh Vu

