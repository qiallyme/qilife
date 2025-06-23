# text_extraction.py

import os
import re
import pytesseract
from PIL import Image
import docx
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from logging_utils import write_log
from utils import get_env_variable
import logging
import pdfplumber

# Initialize logging
logger = logging.getLogger(__name__)

# Configure pytesseract if needed (especially on Windows)
# For example, if Tesseract is not in your PATH, specify the path:
# pytesseract.pytesseract.tesseract_cmd = get_env_variable('TESSERACT_CMD')

def extract_text_from_image(image_path):
    """
    Extracts text from an image file using OCR.

    Parameters:
        image_path (str): Path to the image file.

    Returns:
        str: Extracted text or an empty string if extraction fails.
    """
    try:
        logger.info(f"Extracting text from image: {image_path}")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"Error processing image '{image_path}': {e}")
        write_log(f"Error processing image '{image_path}': {e}")
        return ""

def extract_text_from_pdf_with_ocr(file_path):
    """
    Extracts text from a PDF file using PDFPlumber and OCR for scanned pages.

    Parameters:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text or an empty string if extraction fails.
    """
    try:
        logger.info(f"Extracting text from PDF with OCR: {file_path}")

        def process_page(page):
            text = page.extract_text()
            if not text:
                # If no text is found, perform OCR on the page image
                image = page.to_image(resolution=150).original
                ocr_text = pytesseract.image_to_string(image)
                return ocr_text.strip()
            return text.strip()

        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                logger.warning(f"No pages found in PDF '{file_path}'")
                write_log(f"No pages found in PDF '{file_path}'")
                return ""
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(process_page, pdf.pages))

        return "\n".join(results)
    except Exception as e:
        logger.error(f"Error processing PDF '{file_path}': {e}")
        write_log(f"Error processing PDF '{file_path}': {e}")
        return ""

def extract_text_from_docx(docx_path):
    """
    Extracts text from a DOCX file.

    Parameters:
        docx_path (str): Path to the DOCX file.

    Returns:
        str: Extracted text or an empty string if extraction fails.
    """
    try:
        logger.info(f"Extracting text from DOCX: {docx_path}")
        doc = docx.Document(docx_path)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        return full_text.strip()
    except Exception as e:
        logger.error(f"Error processing DOCX '{docx_path}': {e}")
        write_log(f"Error processing DOCX '{docx_path}': {e}")
        return ""

def extract_text_from_txt(txt_path):
    """
    Extracts text from a TXT file.

    Parameters:
        txt_path (str): Path to the TXT file.

    Returns:
        str: Extracted text or an empty string if extraction fails.
    """
    try:
        logger.info(f"Extracting text from TXT: {txt_path}")
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        logger.error(f"Error processing TXT '{txt_path}': {e}")
        write_log(f"Error processing TXT '{txt_path}': {e}")
        return ""

def extract_text_from_html(html_path):
    """
    Extracts text from an HTML file by stripping HTML tags.

    Parameters:
        html_path (str): Path to the HTML file.

    Returns:
        str: Extracted text or an empty string if extraction fails.
    """
    try:
        logger.info(f"Extracting text from HTML: {html_path}")
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml')
            for script in soup(['script', 'style']):
                script.extract()
            text = soup.get_text(separator="\n")
            # Collapse multiple newlines
            text = re.sub(r'\n+', '\n', text)
            return text.strip()
    except Exception as e:
        logger.error(f"Error processing HTML '{html_path}': {e}")
        write_log(f"Error processing HTML '{html_path}': {e}")
        return ""

def extract_content(file_path):
    """
    Determines the file type based on its extension and extracts text accordingly.

    Parameters:
        file_path (str): Path to the file.

    Returns:
        str: Extracted text or an empty string if extraction fails or file type is unsupported.
    """
    extension = os.path.splitext(file_path)[1].lower()
    text = ""

    if extension == '.pdf':
        text = extract_text_from_pdf_with_ocr(file_path)
    elif extension in ['.jpg', '.jpeg', '.png']:
        text = extract_text_from_image(file_path)
    elif extension == '.docx':
        text = extract_text_from_docx(file_path)
    elif extension == '.txt':
        text = extract_text_from_txt(file_path)
    elif extension == '.html':
        text = extract_text_from_html(file_path)
    else:
        logger.warning(f"Unsupported file type: '{extension}' for file '{file_path}'")
        write_log(f"Unsupported file type: '{extension}' for file '{file_path}'")

    return text
