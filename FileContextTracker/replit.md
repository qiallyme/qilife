# Second Brain - Intelligent File Management System

## Overview

The Second Brain is an AI-powered file management system built with Streamlit that automatically monitors folders, analyzes file content, and provides intelligent naming suggestions. The system uses vector embeddings for semantic search and maintains context across documents for consistent entity recognition.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **Layout**: Multi-component interface with sidebar navigation
- **Components**: Modular UI components for different functionalities
- **State Management**: Streamlit session state for persistent data

### Backend Architecture
- **Core Modules**: 
  - File monitoring with watchdog
  - Content extraction from multiple file formats
  - AI-powered analysis using OpenAI GPT-4o
  - Vector storage for semantic search
  - Context memory for entity consistency
- **Database**: SQLite for metadata and activity logging
- **Processing Pipeline**: Asynchronous file processing with threading

### AI Integration
- **Model**: OpenAI GPT-4o for content analysis and naming suggestions
- **Vector Storage**: ChromaDB primary, FAISS fallback, SQLite emergency fallback
- **Content Extraction**: Multi-format support (PDF, DOCX, images with OCR, text files)

## Key Components

### Core Modules
1. **FileMonitor** (`core/file_monitor.py`): Watches folder changes using watchdog
2. **ContentExtractor** (`core/content_extractor.py`): Extracts text from various file formats
3. **AIAnalyzer** (`core/ai_analyzer.py`): Analyzes content using OpenAI API
4. **DatabaseManager** (`core/database.py`): SQLite operations for metadata storage
5. **VectorStorage** (`core/vector_storage.py`): Semantic search capabilities
6. **ContextMemory** (`core/context_memory.py`): Maintains entity consistency

### UI Components
1. **FolderSelector** (`components/folder_selector.py`): Folder selection and monitoring controls
2. **FileReview** (`components/file_review.py`): Review and approve AI suggestions
3. **ActivityTimeline** (`components/activity_timeline.py`): System activity visualization
4. **LogExport** (`components/log_export.py`): Export system logs and data

### Utilities
1. **FileUtils** (`utils/file_utils.py`): File operations and metadata extraction
2. **LoggingUtils** (`utils/logging_utils.py`): Centralized logging system

## Data Flow

1. **File Detection**: FileMonitor detects new/modified files using watchdog
2. **Content Extraction**: ContentExtractor processes files based on format
3. **AI Analysis**: AIAnalyzer sends content to OpenAI for analysis and naming
4. **Vector Storage**: Content embeddings stored for semantic search
5. **Database Update**: Metadata and analysis results stored in SQLite
6. **Context Update**: ContextMemory updates entity consistency mappings
7. **User Review**: FileReview component presents suggestions for approval
8. **Activity Logging**: All operations logged for audit and debugging

## External Dependencies

### Required APIs
- **OpenAI API**: Content analysis and intelligent naming (GPT-4o model)

### Python Libraries
- **streamlit**: Web application framework
- **watchdog**: File system monitoring
- **openai**: OpenAI API client
- **chromadb**: Primary vector database
- **faiss-cpu**: Fallback vector storage
- **pdfplumber/PyPDF2**: PDF content extraction
- **python-docx**: Word document processing
- **pytesseract/Pillow**: OCR for image processing
- **numpy**: Numerical operations

### System Dependencies
- **Tesseract OCR**: Image text extraction
- **Various image libraries**: freetype, lcms2, libjpeg, etc.

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package manager
- **Deployment**: Autoscale deployment target
- **Port**: 5000 for Streamlit server
- **Workflow**: Parallel execution with shell commands

### File Structure
- **Data Directory**: `./data/` for SQLite database
- **Vector Database**: `./vector_db/` for embeddings
- **Logs**: Integrated into SQLite database

### Environment Setup
- OpenAI API key required via environment variable
- Image processing libraries pre-installed via Nix
- Streamlit configured for headless operation

## Changelog
- June 19, 2025. Initial setup
- June 19, 2025. Added bulk spreadsheet-style file approval interface with checkboxes, inline editing, and batch operations

## User Preferences

Preferred communication style: Simple, everyday language.
UI Preferences: Prefers spreadsheet-like bulk operations for efficiency over individual item processing.