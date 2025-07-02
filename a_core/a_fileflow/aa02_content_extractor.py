import os
import base64
from pathlib import Path
from typing import Dict, Optional, Any
import mimetypes

# PDF processing
try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None

# Word document processing
try:
    from docx import Document
except ImportError:
    Document = None

# Image processing and OCR
try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

from a_core.e_utils.ae02_logging_utils import LoggingUtils

class ContentExtractor:
    """Extract content from various file formats"""
    
    def __init__(self):
        self.logger = LoggingUtils()
        self.supported_formats = {
            'pdf': self._extract_pdf,
            'docx': self._extract_docx,
            'doc': self._extract_docx,  # Attempt with docx library
            'txt': self._extract_text,
            'md': self._extract_text,
            'jpg': self._extract_image,
            'jpeg': self._extract_image,
            'png': self._extract_image,
            'bmp': self._extract_image,
            'tiff': self._extract_image,
        }
    
    def extract_content(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract content from a file based on its format"""
        try:
            file_path_obj = Path(file_path)
            
            # Check if file exists and is readable
            if not file_path_obj.exists() or not file_path_obj.is_file():
                return None
            
            # Get file extension
            extension = file_path_obj.suffix.lower().lstrip('.')
            
            # Get basic metadata
            stat = file_path_obj.stat()
            metadata = {
                'file_path': str(file_path_obj),
                'file_name': file_path_obj.name,
                'file_size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'extension': extension,
                'mime_type': mimetypes.guess_type(str(file_path_obj))[0] or 'unknown'
            }
            
            # Extract content based on file type
            if extension in self.supported_formats:
                content = self.supported_formats[extension](file_path_obj)
                if content:
                    return {
                        'content': content,
                        'metadata': metadata
                    }
            
            self.logger.log_activity(
                "unsupported_format",
                f"Unsupported file format: {extension}",
                {"file_path": str(file_path_obj), "extension": extension}
            )
            return None
            
        except Exception as e:
            self.logger.log_activity(
                "content_extraction_error",
                f"Error extracting content from {file_path}: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
            return None
    
    def _extract_pdf(self, file_path: Path) -> Optional[str]:
        """Extract text from PDF files"""
        try:
            # Try with pdfplumber first (better for complex layouts)
            if pdfplumber:
                with pdfplumber.open(file_path) as pdf:
                    text_content = []
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                    
                    if text_content:
                        return '\n\n'.join(text_content)
            
            # Fallback to PyPDF2
            if PyPDF2:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_content = []
                    
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                    
                    if text_content:
                        return '\n\n'.join(text_content)
            
            return None
            
        except Exception as e:
            self.logger.log_activity(
                "pdf_extraction_error",
                f"Error extracting PDF content: {str(e)}",
                {"file_path": str(file_path), "error": str(e)}
            )
            return None
    
    def _extract_docx(self, file_path: Path) -> Optional[str]:
        """Extract text from Word documents"""
        try:
            if not Document:
                return None
            
            doc = Document(file_path)
            text_content = []
            
            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_content.append(' | '.join(row_text))
            
            return '\n\n'.join(text_content) if text_content else None
            
        except Exception as e:
            self.logger.log_activity(
                "docx_extraction_error",
                f"Error extracting Word document content: {str(e)}",
                {"file_path": str(file_path), "error": str(e)}
            )
            return None
    
    def _extract_text(self, file_path: Path) -> Optional[str]:
        """Extract content from plain text files"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                        return content.strip() if content.strip() else None
                except UnicodeDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.log_activity(
                "text_extraction_error",
                f"Error extracting text content: {str(e)}",
                {"file_path": str(file_path), "error": str(e)}
            )
            return None
    
    def _extract_image(self, file_path: Path) -> Optional[str]:
        """Extract text from images using OCR"""
        try:
            if not Image or not pytesseract:
                return None
            
            # Open and process image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Perform OCR
                text = pytesseract.image_to_string(img, lang='eng')
                
                return text.strip() if text.strip() else None
                
        except Exception as e:
            self.logger.log_activity(
                "image_extraction_error",
                f"Error extracting text from image: {str(e)}",
                {"file_path": str(file_path), "error": str(e)}
            )
            return None
    
    def get_image_base64(self, file_path: str) -> Optional[str]:
        """Convert image to base64 for AI analysis"""
        try:
            with open(file_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.log_activity(
                "image_base64_error",
                f"Error converting image to base64: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
            return None
