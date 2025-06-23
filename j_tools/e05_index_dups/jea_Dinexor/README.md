README.txt

# Dinexor: Directory Index Extractor & Organizer

**Description:**

Dinexor is a Python-based application designed to streamline directory management and create a searchable index of files. It automates several tasks, including:

* **Directory Mapping:** Generates a detailed log of the directory structure, including file paths.
* **Empty Folder Removal:** Identifies and moves empty folders to a specified location.
* **File Indexing:** Extracts text content from various file types (including OCR for images and PDFs) to create a JSON index.

This tool is particularly useful for organizing large file systems and preparing data for use with Large Language Models (LLMs).

**Directory Structure:**
Dinexor/
├── directory_mapper.py  # Main application logic (directory traversal, folder nixing, indexing)
├── text_extraction.py   # (Future) Functions for advanced text extraction and processing
├── text_processor.py    # (Future) Functions for summarizing and preparing text for LLMs
├── templates/
│   └── index.html       # HTML GUI for user interaction
├── start_app.bat        # Batch file to launch the application
└── README.md            # Documentation (this file)

**Requirements:**

* Python 3.6 or later
* Flask
* pytesseract
* Pillow (PIL)
* pdf2image
* schedule
* Tesseract OCR (installed separately)

# Dinexor: Directory Management and Indexing Tool

**Installation:**

1.  Ensure Python 3.6+ is installed.
2.  Run the `run_dinexor.bat` file. This will:
     * Check if `requirements.txt` is present.
     * Check if Python is installed and in the system's PATH.
     * Attempt to install all necessary Python libraries from `requirements.txt`.
     * Launch the Dinexor application.
3.  Install Tesseract OCR:
     * Download and install Tesseract OCR from a trusted source.
     * Ensure Tesseract is in your system's PATH, or configure the `pytesseract.pytesseract.tesseract_cmd` variable if necessary.

**Usage:**

1.  **Launch the application:**
    * Double-click the `start_app.bat` file.
    * This will start a local web server and open the Dinexor GUI in your default browser.

2.  **Interact with the GUI:**

    * **Run Default:** Click "Run Default" to process the pre-defined directories (C:\\ProgramData, C:\\Users, E:\\).
    * **Custom Run:**
        * Enter the "Source Directory" you want to process.
        * Optionally, enter a "Destination Directory" for empty folders (defaults to Downloads).
        * Check "Show Files" to include files in the directory log.
        * Set the "Max Depth" for directory traversal (1-10, or 'all' for unlimited).
        * Click "Run" to start processing.

3.  **Output:**

    * Log files are saved in the Downloads directory.
    * The JSON index is created in the root directory being processed.

**Future Enhancements:**

* Advanced text extraction and processing (in `text_extraction.py` and `text_processor.py`)
* Interactive HTML mind map visualization of the directory structure
* More robust error handling and user feedback
* Progress indication during processing
* Packaging into an executable

**Contributing:**

(Add contribution guidelines if you plan to open-source the project)

**License:**

(Add license information)

Explanation of Key Sections:

Description: Provides a concise overview of Dinexor's purpose and functionality.
Directory Structure: Clearly outlines the organization of the project's files and folders.
Requirements: Lists the necessary software and libraries for Dinexor to run.
Installation: Provides step-by-step instructions on how to set up Dinexor.
Usage: Explains how to launch and interact with the application, including both default and custom run options.
Output: Specifies where the generated log files and index are saved.
Future Enhancements: Briefly mentions planned features to give users and potential contributors an idea of the project's direction.
This README provides a solid foundation for your Dinexor project. You can further expand it with more detailed explanations, troubleshooting tips, and examples as needed.