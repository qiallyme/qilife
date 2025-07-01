import csv
import os

EXPECTED_COLUMNS = 7
CLEAN_HEADER = ["Password Name", "Password URL", "TOTP", "Notes", "Folder Name", "Username", "Password"]

def clean_password_csv(input_path, output_path):
    with open(input_path, "r", encoding="utf-8-sig") as infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write fixed header
        writer.writerow(CLEAN_HEADER)

        for row in reader:
            # Skip any bad or empty header rows
            if "Password URL" in row or all(not cell.strip() for cell in row):
                continue

            # Remove trailing blank columns
            while row and row[-1] == "":
                row.pop()

            # Pad or trim
            if len(row) < EXPECTED_COLUMNS:
                row += [""] * (EXPECTED_COLUMNS - len(row))
            elif len(row) > EXPECTED_COLUMNS:
                row = row[:EXPECTED_COLUMNS]

            writer.writerow(row)

    print(f"\n✅ Cleaned CSV written to:\n{os.path.abspath(output_path)}")

if __name__ == "__main__":
    print("🔐 Password CSV Cleaner")

    input_path = input("📥 Enter the path to your input CSV file: ").strip('"').strip()
    while not os.path.exists(input_path):
        input_path = input("⚠️ File not found. Try again: ").strip('"').strip()

    output_path = input("📤 Enter path for the cleaned output file: ").strip('"').strip()
    if not output_path.endswith(".csv"):
        output_path += ".csv"

    clean_password_csv(input_path, output_path)
