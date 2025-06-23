import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API (API key should now be loaded from .env)
# genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Specify the model to use
MODEL_NAME = "gemini-2.5-pro-preview-03-25"

def get_account_category(client, form_type, industry, transaction_type, description):
    """
    Uses the Gemini API to determine the appropriate account category.
    """
    prompt = f"""Based on the {form_type} tax form and the {industry} industry,
    categorize the following bank transaction which is a {transaction_type}:
    Description: "{description}"
    Return only the most appropriate account name for this transaction."""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=generate_content_config,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Category Not Found"

def main():
    """
    Prompts for Excel file, tax form, and industry, then categorizes transactions.
    """
    file_path = input("Enter the path to your Excel file: ")
    try:
        df = pd.read_excel(file_path, usecols=[0, 1, 2])
        print("\nFirst few rows of your data:")
        print(df.head())
    except FileNotFoundError:
        print("Error: File not found.")
        return
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    form_type = input("Enter the tax form type (1120 or 1040): ").strip()
    industry = input("Enter the industry (e.g., Food Service, Retail, Consulting): ").strip()

    # Initialize the Gemini Client
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    categorized_data = []
    for index, row in df.iterrows():
        # Assuming your columns are in the order: Date, Description, Amount
        date = row.iloc[0]
        description = row.iloc[1]
        amount = row.iloc[2]

        if pd.notna(amount):
            transaction_type = "deposit" if amount > 0 else "withdrawal"
        else:
            transaction_type = "unknown"

        category = get_account_category(client, form_type, industry, transaction_type, description)
        categorized_data.append([date, description, amount, category])

    categorized_df = pd.DataFrame(categorized_data, columns=["Date", "Description", "Amount", "Category"])

    print("\nCategorized Data:")
    print(categorized_df)

    # Option to save the categorized data to a new Excel file
    save_option = input("\nDo you want to save the categorized data to a new Excel file? (yes/no): ").lower()
    if save_option == "yes":
        output_file_path = input("Enter the path for the output Excel file: ")
        try:
            categorized_df.to_excel(output_file_path, index=False)
            print(f"Categorized data saved to: {output_file_path}")
        except Exception as e:
            print(f"Error saving Excel file: {e}")

if __name__ == "__main__":
    main()