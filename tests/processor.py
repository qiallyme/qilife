# file_processing/processor.py
import os
import logging
from typing import List, Dict, Any
from .file_handler import FileHandler
from .ai_service import AIService
from .folder_manager import FolderManager

class FileProcessor:
    def __init__(self, openai_api_key=None, log_level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        self.file_handler = FileHandler()
        self.ai_service = AIService(openai_api_key)
        self.folder_manager = FolderManager()

    def process_file(self, file_urls, folder_template, user_notes='', batch=False) -> Dict[str, Any]:
        results = []
        try:
            files = self.file_handler.download_and_extract_files(file_urls, batch)

            for file_path in files:
                try:
                    content = self.file_handler.extract_content(file_path)
                    if not content:
                        results.append({
                            "file": file_path,
                            "status": "Error",
                            "message": "Unsupported or empty file type"
                        })
                        continue

                    new_name = self.ai_service.generate_descriptive_name(content)
                    target_folder = self.folder_manager.categorize_file(content, folder_template)

                    os.makedirs(target_folder, exist_ok=True)
                    new_file_path = os.path.join(target_folder, f"{new_name}.txt")

                    with open(new_file_path, 'w', encoding='utf-8') as renamed_file:
                        renamed_file.write(content)

                     # Rename and move the original file
                    original_file_extension = os.path.splitext(file_path)[1]
                    new_original_file_path = os.path.join(target_folder, f"{new_name}{original_file_extension}")
                    os.rename(file_path, new_original_file_path)

                    results.append({
                        "file": file_path,
                        "status": "Success",
                        "new_file_name": new_name,
                        "folder": target_folder
                    })
                except Exception as file_error:
                    self.logger.error(f"Error processing {file_path}: {file_error}")
                    results.append({
                        "file": file_path,
                        "status": "Error",
                        "message": str(file_error)
                    })

            return {"status": "Completed", "results": results}
        except Exception as e:
            self.logger.exception("Critical error during file processing")
            return {"status": "Error", "message": str(e)}
        finally:
            self.file_handler.cleanup()
