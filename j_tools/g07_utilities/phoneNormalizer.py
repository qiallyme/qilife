#!/usr/bin/env python3
"""
interactive_phone_normalizer.py
─────────────────────────────────────────────
• Prompts for folder and CSV file
• Normalizes Mobile  → +1##########
• Normalizes other phone fields → ##########
• Writes Contacts_normalized.csv
"""

import re, sys, pathlib, pandas as pd

# ---- CONFIG -----------------------------------------------------------------
MOBILE_FIELDS   = ["Mobile"]                                # treated as E.164
OTHER_FIELDS    = ["Phone", "Other Phone", "Assistant Phone",
                   "Secondary Phone"]                       # 10-digit clean
# -----------------------------------------------------------------------------

def digits_only(raw: str) -> str:
    """Strip everything except digits."""
    return re.sub(r"[^\d]", "", str(raw)) if pd.notna(raw) else ""

def clean_10(raw: str) -> str:
    """Return 10-digit US number ('' if invalid)."""
    d = digits_only(raw)
    return d[-10:] if len(d) >= 10 else ""

def mobile_e164(raw: str) -> str:
    """Return +1########## ('' if invalid)."""
    d10 = clean_10(raw)
    return f"+1{d10}" if d10 else ""

def choose_csv(root: pathlib.Path) -> pathlib.Path:
    csvs = sorted(root.glob("*.csv"))
    if not csvs:
        print(f"No CSV files found in {root}")
        sys.exit(1)
    print("\nCSV files found:")
    for i, f in enumerate(csvs, 1):
        print(f"  [{i}] {f.name}")
    idx = int(input("\nSelect a file number to normalize: "))
    if idx < 1 or idx > len(csvs):
        print("Invalid choice."); sys.exit(1)
    return csvs[idx - 1]

def main():
    root = pathlib.Path(input("Enter folder path containing your CSV: ").strip()).expanduser()
    if not root.exists():
        print("Folder does not exist."); sys.exit(1)

    csv_path = choose_csv(root)
    print(f"\n→ Processing {csv_path.name} …")
    df = pd.read_csv(csv_path)

    # Normalize Mobile columns
    for col in MOBILE_FIELDS:
        if col in df.columns:
            df[f"{col}_e164"] = df[col].apply(mobile_e164)

    # Normalize other phone-type columns
    for col in OTHER_FIELDS:
        if col in df.columns:
            df[f"{col}_clean"] = df[col].apply(clean_10)

    out_path = csv_path.with_name("Contacts_normalized.csv")
    df.to_csv(out_path, index=False)
    print(f"\n✅  Done!  Cleaned file saved as:\n    {out_path}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
