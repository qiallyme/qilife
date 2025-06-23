import os
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from typing import Optional

from a_core.a_fileflow.aa02_content_extractor import ContentExtractor
from a_core.d_ai.ad01_analyzer import AIAnalyzer
from a_core.a_fileflow.aa05_database import DatabaseManager
from a_core.a_fileflow import VectorStorage
from a_core.a_fileflow import ContextMemory
from a_core.e_utils import LoggingUtils

class FileEventHandler(FileSystemEventHandler):
    """Handle file system events for monitoring"""
    
    def __init__(self, file_monitor):
        self.file_monitor = file_monitor
        self.content_extractor = ContentExtractor()
        self.ai_analyzer = AIAnalyzer()
        self.logger = LoggingUtils()
        
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self.file_monitor.process_file(event.src_path, "created")
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self.file_monitor.process_file(event.src_path, "modified")
    
    def on_moved(self, event):
        """Handle file move/rename events"""
        if not event.is_directory:
            self.file_monitor.process_file(event.dest_path, "moved")

class FileMonitor:
    """Main file monitoring class"""
    
    def __init__(self, folder_path: str, db_manager: DatabaseManager, 
                 vector_storage: VectorStorage, context_memory: ContextMemory):
        self.folder_path = folder_path
        self.db_manager = db_manager
        self.vector_storage = vector_storage
        self.context_memory = context_memory
        self.observer = None
        self.is_monitoring = False
        self.content_extractor = ContentExtractor()
        self.ai_analyzer = AIAnalyzer()
        self.logger = LoggingUtils()
        
        # Supported file extensions
        self.supported_extensions = {
            '.pdf', '.docx', '.doc', '.txt', '.md',
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff'
        }
    
    def start_monitoring(self):
        """Start monitoring the selected folder"""
        try:
            self.is_monitoring = True
            
            # Process existing files first
            self._process_existing_files()
            
            # Set up file system watcher
            event_handler = FileEventHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, self.folder_path, recursive=True)
            self.observer.start()
            
            self.logger.log_activity(
                "monitoring_started",
                f"Started monitoring folder: {self.folder_path}",
                {"folder_path": self.folder_path}
            )
            
            # Keep monitoring until stopped
            while self.is_monitoring:
                time.sleep(1)
                
        except Exception as e:
            self.logger.log_activity(
                "monitoring_error",
                f"Error in file monitoring: {str(e)}",
                {"error": str(e), "folder_path": self.folder_path}
            )
            raise
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.logger.log_activity(
            "monitoring_stopped",
            f"Stopped monitoring folder: {self.folder_path}",
            {"folder_path": self.folder_path}
        )
    
    def _process_existing_files(self):
        """Process all existing files in the folder"""
        try:
            folder_path = Path(self.folder_path)
            for file_path in folder_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    self.process_file(str(file_path), "existing")
        except Exception as e:
            self.logger.log_activity(
                "existing_files_error",
                f"Error processing existing files: {str(e)}",
                {"error": str(e)}
            )
    
    def process_file(self, file_path: str, event_type: str):
        """Process a single file"""
        try:
            file_path_obj = Path(file_path)
            
            # Check if file extension is supported
            if file_path_obj.suffix.lower() not in self.supported_extensions:
                return
            
            # Check if file already processed recently
            if self._is_recently_processed(file_path):
                return
            
            # Extract content from file
            content_data = self.content_extractor.extract_content(file_path)
            if not content_data:
                return
            
            # Analyze content and generate naming suggestion
            analysis_result = self.ai_analyzer.analyze_file_content(
                content_data['content'],
                content_data['metadata'],
                self.context_memory
            )
            
            # Generate vector embedding
            embedding = self.ai_analyzer.generate_embedding(content_data['content'])
            
            # Store in vector database
            vector_id = self.vector_storage.store_embedding(
                embedding=embedding,
                content=content_data['content'],
                metadata={
                    'file_path': file_path,
                    'original_name': file_path_obj.name,
                    'suggested_name': analysis_result['suggested_name'],
                    'entities': analysis_result['entities'],
                    'event_type': event_type
                }
            )
            
            # Store in main database
            self.db_manager.store_file_analysis(
                file_path=file_path,
                original_name=file_path_obj.name,
                suggested_name=analysis_result['suggested_name'],
                content=content_data['content'],
                metadata=content_data['metadata'],
                entities=analysis_result['entities'],
                confidence=analysis_result['confidence'],
                reasoning=analysis_result['reasoning'],
                vector_id=vector_id,
                event_type=event_type
            )
            
            # Update context memory
            self.context_memory.update_context(
                entities=analysis_result['entities'],
                content=content_data['content'],
                file_path=file_path
            )
            
            # Log the activity
            self.logger.log_activity(
                "file_processed",
                f"Processed file: {file_path_obj.name}",
                {
                    "file_path": file_path,
                    "suggested_name": analysis_result['suggested_name'],
                    "entities": analysis_result['entities'],
                    "event_type": event_type
                }
            )
            
        except Exception as e:
            self.logger.log_activity(
                "file_processing_error",
                f"Error processing file {file_path}: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
    
    def _is_recently_processed(self, file_path: str) -> bool:
        """Check if file was recently processed to avoid duplicates"""
        try:
            return self.db_manager.is_file_recently_processed(file_path)
        except Exception:
            return False
