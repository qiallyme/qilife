import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import mimetypes

class FileUtils:
    """Utility functions for file operations"""
    
    @staticmethod
    def get_file_hash(file_path: str) -> Optional[str]:
        """Generate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def is_file_accessible(file_path: str) -> bool:
        """Check if file exists and is accessible"""
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and os.access(path, os.R_OK)
        except Exception:
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            
            return {
                'name': path.name,
                'stem': path.stem,
                'suffix': path.suffix,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'accessed_time': stat.st_atime,
                'created_date': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'mime_type': mimetypes.guess_type(str(path))[0] or 'unknown',
                'is_readable': os.access(path, os.R_OK),
                'is_writable': os.access(path, os.W_OK),
                'absolute_path': str(path.absolute()),
                'parent_dir': str(path.parent)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def safe_rename_file(old_path: str, new_name: str) -> bool:
        """Safely rename a file, handling conflicts"""
        try:
            old_path_obj = Path(old_path)
            if not old_path_obj.exists():
                return False
            
            # Clean the new name
            new_name = FileUtils.sanitize_filename(new_name)
            
            # Create new path in the same directory
            new_path = old_path_obj.parent / new_name
            
            # Handle naming conflicts
            counter = 1
            original_new_path = new_path
            while new_path.exists():
                stem = original_new_path.stem
                suffix = original_new_path.suffix
                new_path = original_new_path.parent / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Perform the rename
            old_path_obj.rename(new_path)
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitze filename for filesystem compatibility"""
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            max_name_length = 255 - len(ext)
            filename = name[:max_name_length] + ext
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure not empty
        if not filename:
            filename = f"unnamed_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return filename
    
    @staticmethod
    def copy_file_safely(src_path: str, dst_path: str) -> bool:
        """Safely copy a file"""
        try:
            src = Path(src_path)
            dst = Path(dst_path)
            
            if not src.exists():
                return False
            
            # Create destination directory if it doesn't exist
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(src, dst)
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def get_directory_size(directory_path: str) -> int:
        """Get total size of directory in bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, IOError):
                        continue
            return total_size
        except Exception:
            return 0
    
    @staticmethod
    def count_files_in_directory(directory_path: str, extensions: set = None) -> int:
        """Count files in directory, optionally filtered by extensions"""
        try:
            count = 0
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if extensions is None:
                        count += 1
                    else:
                        file_ext = Path(file).suffix.lower()
                        if file_ext in extensions:
                            count += 1
            return count
        except Exception:
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """Check if file is an image"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
        return Path(file_path).suffix.lower() in image_extensions
    
    @staticmethod
    def is_document_file(file_path: str) -> bool:
        """Check if file is a document"""
        document_extensions = {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt'}
        return Path(file_path).suffix.lower() in document_extensions
    
    @staticmethod
    def get_file_category(file_path: str) -> str:
        """Get file category based on extension"""
        ext = Path(file_path).suffix.lower()
        
        if ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}:
            return 'image'
        elif ext in {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt'}:
            return 'document'
        elif ext in {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}:
            return 'audio'
        elif ext in {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}:
            return 'video'
        elif ext in {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}:
            return 'archive'
        elif ext in {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php'}:
            return 'code'
        else:
            return 'other'
