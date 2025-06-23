# text_processing.py
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from utils import write_log, sanitize_filename, generate_fallback_name, get_env_variable
import logging
from openai import OpenAI
import openai
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

if not api_key:
    logger.error("OpenAI API key not found in environment variables.")
    raise ValueError("OpenAI API key not found.")

def determine_file_type(content):
    """
    Determines the category of the file based on its content using keyword frequency.

    Parameters:
        content (str): The text content extracted from the file.

    Returns:
        str: The determined category name or "Default" if no match is found.
    """
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(content.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Define keywords for each category
    category_keywords = {
        "Financial_Invoices": ["invoice", "payment", "receipt"],
        "Financial_Payroll": ["payroll", "salary", "wage"],
        "Financial_Tax": ["tax", "filing", "deduction"],
        "Financial_Reports_Expenses": ["report", "expense", "financial"],
        "HR_Records_Policies": ["employee", "policy", "record"],
        "HR_Training": ["training", "development", "course"],
        "Sales_Contracts_Clients": ["contract", "client", "agreement"],
        "Sales_Pricing": ["pricing", "price", "quote"],
        "Marketing_Content_Branding": ["marketing", "branding", "campaign"],
        "Operations_SOPs_Vendors": ["sop", "vendor", "operation"],
        "Operations_Projects_Scheduling": ["project", "schedule", "timeline"],
        "Compliance_Legal": ["compliance", "legal", "regulation"],
        "Regulatory_Risk": ["regulatory", "risk", "assessment"],
        "Audit_Intellectual_Property": ["audit", "intellectual", "property"],
    }

    # Score each category based on keyword frequency
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = sum([word_freq.get(keyword, 0) for keyword in keywords])
        category_scores[category] = score

    # Determine the category with the highest score
    best_match = max(category_scores, key=category_scores.get)
    if category_scores[best_match] > 0:
        logging.info(f"Determined category: {best_match} with score {category_scores[best_match]}")
        return best_match
    else:
        logging.info("No matching category found. Defaulting to 'Default'.")
        return "Default"
    
def generate_file_name(text_content):
    """
    Generates a descriptive file name for the provided text using OpenAI's GPT model.

    Parameters:
        text_content (str): The text content based on which the filename is generated.

    Returns:
        str: A sanitized and descriptive filename. If GPT fails, returns a fallback name.
    """
    prompt = f"""Generate a descriptive file name for a file containing the following text:
{text_content[:500]}

Make sure the file name:
- Does not contain any special characters (e.g., <>:"/\\|?*).
- Uses only letters, numbers, underscores, dashes, or spaces.
- Is short and concise.
- Does not start or end with spaces or quotes.
- Does not include any quotation marks.
"""

    try:
        logger.info("Sending text to OpenAI for filename generation.")
        response = client.chat.completions.create(  # Use 'chat_completions' as per the new API
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.5
        )
        filename = response.choices[0].message.content.strip()
        sanitized_filename = sanitize_filename(filename)
        logger.info("Received filename from OpenAi.")
        return sanitized_filename
    except Exception as e:
        logger.error(f"Error calling GPT API for filename generation: {e}")
        write_log(f"Error calling GPT API for filename generation: {e}")
        return generate_fallback_name("default_filename")
    
def clean_text_with_gpt(text_content):
    """
    Cleans and corrects the provided text using OpenAI's GPT model.

    Parameters:
        text_content (str): The original text content to be cleaned.

    Returns:
        str: The cleaned and corrected text. If GPT fails, returns the original text.
    """
    prompt = f"Please clean and correct the following text in its original language:\n\n{text_content[:1000]}"

    try:
        logger.info("Sending text to OpenAi for cleaning.")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" if you have access
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        cleaned_text = response.choices[0].message.content.strip()
        logger.info("Received cleaned text from OpenAi.")
        return cleaned_text
    except Exception as e:
        logger.error(f"Error calling GPT API: {e}")
        write_log(f"Error calling GPT API: {e}")
        return text_content  # Fallback to original text if GPT fails

def process_text(text_content, folder_mappings):
    """
    Processes the extracted text by cleaning it, generating a filename,
    and determining its category.

    Parameters:
        text_content (str): The raw text extracted from the file.
        folder_mappings (dict): A dictionary mapping categories to folder names.

    Returns:
        dict: A dictionary containing cleaned text, new filename, and file category.
    """
    cleaned_text = clean_text_with_gpt(text_content)
    new_filename = generate_file_name(cleaned_text)
    file_category = determine_file_type(cleaned_text, folder_mappings)

    return {
        "cleaned_text": cleaned_text,
        "new_filename": new_filename,
        "file_category": file_category
    }

def tokenize_text(text):
    tokenizer = nltk.data.load ('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)
