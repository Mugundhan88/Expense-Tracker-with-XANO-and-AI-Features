#!/usr/bin/env python3.11
import pytesseract
from PIL import Image
import re
import json
import argparse

def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None

def parse_receipt_text(text):
    """Parses OCR text to find vendor, date, and total amount using regex."""
    if not text:
        return {}

    extracted_data = {
        "vendor_name": None,
        "transaction_date": None,
        "total_amount": None,
        "raw_text": text
    }

    # Simple regex patterns (these would need to be much more robust for real-world use)
    # Vendor: Often at the top, look for capitalized words or common store names (very simplistic)
    # For this example, we'll take the first non-empty line as a potential vendor if it's mostly text.
    lines = text.split("\n")
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line and re.match(r"^[A-Za-z\s&\.,\-\'\_]+$", cleaned_line) and not re.search(r"\d{2}/\d{2}/\d{2,4}|\d{1,2}\.\d{2}", cleaned_line):
            # Avoid lines that look like dates or amounts
            if len(cleaned_line) > 2 and len(cleaned_line) < 50: # Arbitrary length check
                extracted_data["vendor_name"] = cleaned_line
                break # Take the first likely candidate

    # Date: Look for common date formats like MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD, Month DD, YYYY
    date_patterns = [
        r"(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})",  # 01/01/2023, 01-01-2023, 01.01.2023
        r"(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})",  # 2023/01/01, 2023-01-01
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\.\s,]+\d{1,2}[,\s]+\d{2,4})" # Jan. 01, 2023
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_data["transaction_date"] = match.group(1).strip()
            break

    # Total Amount: Look for lines starting with "Total", "TOTAL", or just a currency symbol followed by numbers.
    # This is highly dependent on receipt format and often the largest numerical value.
    # A more robust approach would look for keywords and then the largest amount nearby.
    amount_patterns = [
        r"(?:Total|TOTAL|Amount Due|Balance|SUBTOTAL)[\s:]*[$]?(\d+\.\d{2})",
        r"[$]?(\d+\.\d{2})" # General pattern for amounts
    ]
    
    possible_totals = []
    for pattern in amount_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            try:
                possible_totals.append(float(m))
            except ValueError:
                continue
    
    if possible_totals:
        # Often the largest amount is the total, but this is a heuristic
        extracted_data["total_amount"] = max(possible_totals)
    else:
        # Fallback: try to find the largest number that looks like an amount if no keywords match
        all_amounts = re.findall(r"\b\d+\.\d{2}\b", text)
        if all_amounts:
            try:
                extracted_data["total_amount"] = max([float(a) for a in all_amounts])
            except ValueError:
                pass

    return extracted_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract information from a receipt image.")
    parser.add_argument("image_path", help="Path to the receipt image file.")
    parser.add_argument("--output_json", help="Path to save the extracted data as JSON.", default=None)

    args = parser.parse_args()

    print(f"Processing image: {args.image_path}")
    ocr_text = extract_text_from_image(args.image_path)

    if ocr_text:
        print("--- OCR Text ---")
        print(ocr_text)
        print("------------------")
        parsed_data = parse_receipt_text(ocr_text)
        print("--- Parsed Data ---")
        print(json.dumps(parsed_data, indent=2))
        print("-------------------")

        if args.output_json:
            try:
                with open(args.output_json, "w") as f:
                    json.dump(parsed_data, f, indent=2)
                print(f"Saved parsed data to {args.output_json}")
            except Exception as e:
                print(f"Error saving JSON output: {e}")
    else:
        print("Could not extract text from image.")

