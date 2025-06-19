# fileflow/core/processor.py

import os
from .analyze import extract_metadata
from .rename import generate_filename
from .filer import move_file_to_destination
from .folders_create import ensure_folder_exists
# from notion_logger import log_to_notion  # future step

def run_full_pipeline(file_path):
    if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"🚀 Starting pipeline for: {file_path}")

    # Step 1: Analyze
    metadata = extract_metadata(file_path)
    if not metadata:
        print("⚠️ Failed to extract metadata.")
        return

    # Step 2: Rename
    new_filename = generate_filename(file_path, metadata)
    new_path = os.path.join(os.path.dirname(file_path), new_filename)
    os.rename(file_path, new_path)
    print(f"✏️ Renamed to: {new_filename}")

    # Step 3: Classify
    destination_folder = metadata.get("suggested_path")
    if not destination_folder:
        destination_folder = "intermediate_files/to_review"

    # Step 4: Create folder if needed
    ensure_folder_exists(destination_folder)

    # Step 5: Move file
    final_path = move_file_to_destination(new_path, destination_folder)
    print(f"📁 Moved to: {final_path}")

    # Step 6: Log to Notion (placeholder)
    # log_to_notion(metadata, final_path)

    print("✅ Pipeline complete.")

