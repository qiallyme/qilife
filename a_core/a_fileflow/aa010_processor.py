# fileflow/core/processor.py

import os
from a_core.a_fileflow.aa07_filer import move_file
from a_core.a_fileflow.aa08_folders_create import create_folders_by_type
from a_core.a_fileflow.aa02_content_extractor import ContentExtractor
from a_core.d_ai.ad01_analyzer import AIAnalyzer
# from notion_logger import log_to_notion  # future step

def run_full_pipeline(file_path):
    if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"🚀 Starting pipeline for: {file_path}")

    # Step 1: Analyze
    metadata = ContentExtractor().extract_content(file_path)
    if not metadata:
        print("⚠️ Failed to extract metadata.")
        return

    # Step 2: Rename
    new_filename = AIAnalyzer().analyze_file_content(file_path, metadata)
    new_path = os.path.join(os.path.dirname(file_path), new_filename)
    os.rename(file_path, new_path)
    print(f"✏️ Renamed to: {new_filename}")

    # Step 3: Classify
    destination_folder = metadata.get("suggested_path")
    if not destination_folder:
        destination_folder = "intermediate_files/to_review"

    # Step 4: Create folder if needed
    create_folders_by_type(destination_folder)

    # Step 5: Move file
    final_path = move_file(new_path, destination_folder)
    print(f"📁 Moved to: {final_path}")

    # Step 6: Log to Notion (placeholder)
    # log_to_notion(metadata, final_path)

    print("✅ Pipeline complete.")

