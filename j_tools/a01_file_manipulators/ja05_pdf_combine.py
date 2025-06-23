import os
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path # Added for a more robust way to get Downloads path

def get_download_path():
    """Returns the default downloads path for linux or windows."""
    if os.name == 'nt': # Windows
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        except Exception: # Fallback if the registry key is not found
            return str(Path.home() / "Downloads")
    else: # Linux and hopefully macOS
        return str(Path.home() / "Downloads")

# Get the path of the PDF files from the user
input_folder_path_raw = input("Please paste the full path to the folder containing your PDF files: ")

# Remove leading/trailing double quotes from the input path if they exist
input_folder_path = input_folder_path_raw.strip('"')

# Dynamically determine the output path in the Downloads directory
downloads_dir = get_download_path()
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir) # Create Downloads directory if it doesn't exist
output_file = os.path.join(downloads_dir, "merged.pdf")

# Create a PDF writer object
pdf_writer = PdfWriter()

# Check if the input path is a valid directory
if not os.path.isdir(input_folder_path):
    print(f"Error: The provided path '{input_folder_path}' is not a valid directory.")
else:
    # Get all PDF files from the input folder and sort them (modify sorting as needed)
    try:
        pdf_files = [f for f in os.listdir(input_folder_path) if f.lower().endswith('.pdf')]
        pdf_files.sort() # Sort alphabetically, you can change this if needed

        if not pdf_files:
            print(f"No PDF files found in '{input_folder_path}'.")
        else:
            print(f"Found the following PDF files to merge (in order):")
            for pdf_file in pdf_files:
                print(f"- {pdf_file}")
            print("\nStarting merge process...\n")

            # Loop through each PDF file and append its pages to the writer
            for pdf_file in pdf_files:
                pdf_path = os.path.join(input_folder_path, pdf_file)
                try:
                    pdf_reader = PdfReader(pdf_path)
                    for page_num, page in enumerate(pdf_reader.pages):
                        pdf_writer.add_page(page)
                    print(f"Merged '{pdf_file}' with {len(pdf_reader.pages)} pages.")
                except Exception as e:
                    print(f"Error processing '{pdf_file}': {e}")
                    print(f"Skipping this file due to error.")

            # Write the combined PDF to the output file
            if len(pdf_writer.pages) > 0:
                with open(output_file, 'wb') as out_pdf:
                    pdf_writer.write(out_pdf)
                print(f"\nPDF merged successfully into '{output_file}'")
            else:
                print("\nNo pages were added to the PDF. Output file not created.")

    except FileNotFoundError:
        print(f"Error: The directory '{input_folder_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")