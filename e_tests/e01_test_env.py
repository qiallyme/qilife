# tests/test_env.py

from dotenv import load_dotenv
import os

print("🔍 Loading environment variables...")
load_dotenv()

# Check if a sample variable exists
sample_var = os.getenv("APP_ENV", "Not Set")
print(f"✅ APP_ENV: {sample_var}")

# Now test key module imports
print("\n🔍 Testing key module imports...")

try:
    import openai
    print("✅ openai loaded")
except ImportError:
    print("❌ openai not found")

try:
    import pytesseract
    print("✅ pytesseract loaded")
except ImportError:
    print("❌ pytesseract not found")

try:
    import pdfplumber
    print("✅ pdfplumber loaded")
except ImportError:
    print("❌ pdfplumber not found")

try:
    from notion_client import Client
    print("✅ notion-client loaded")
except ImportError:
    print("❌ notion-client not found")

try:
    from flask import Flask
    print("✅ Flask loaded")
except ImportError:
    print("❌ Flask not found")

print("\n🎯 Environment check complete.")
