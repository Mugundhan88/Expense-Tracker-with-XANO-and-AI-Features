# Expense Tracker - User Guide

## 1. Introduction

Welcome to the Expense Tracker application! This system is designed to help users categorize and analyze their spending patterns, leveraging a XANO backend (simulated for this project) and AI-powered features for receipt processing and financial insights.

Key features include:

*   **XANO Backend:** A robust (though simulated in this deliverable) backend for managing user data, expenses, categories, and receipts.
*   **Receipt Image Recognition (OCR + NLP):** Python scripts to extract text from receipt images and parse key information like vendor, date, and total amount.
*   **Spending Pattern Analysis:** A Python script to analyze historical expense data, providing summaries by category and over time.
*   **Predictive Budgeting:** A Python script to forecast future spending based on past averages.

This guide will walk you through the system architecture, how to (conceptually) set up the backend, how to use the provided AI scripts, and how the components are intended to integrate.

## 2. System Architecture Overview

The system consists of two main parts:

1.  **XANO Backend (Simulated):** This would be the central hub for data storage and API provision. All user data, expense records, categories, and receipt metadata are designed to be stored here. The detailed architecture for this is in `system_architecture.md`.
2.  **AI Python Scripts:** Standalone Python scripts that perform specialized AI tasks:
    *   `receipt_parser.py`: For OCR and basic NLP on receipt images.
    *   `spending_analyzer.py`: For analyzing expense data.
    *   `predictive_budgeter.py`: For forecasting future expenses.

These AI scripts are designed to be called by the XANO backend, likely by wrapping them in a simple web service (e.g., Flask/FastAPI) that XANO can call via HTTP requests.

## 3. XANO Backend Setup (Simulated)

As direct XANO account creation and setup by the AI is not possible, a detailed guide for manually setting up the XANO backend has been provided in:

*   `/home/ubuntu/xano_implementation_guide_simulated.md`

This guide walks through:

*   Creating the necessary database tables (`users`, `categories`, `expenses`, `receipts`) with the correct schema.
*   Defining the API endpoints as specified in `system_architecture.md` (e.g., for authentication, CRUD operations on expenses, receipt uploads, and fetching reports).

Following this guide in a XANO free tier account will allow you to replicate the intended backend structure.

## 4. Using the AI Python Scripts

The AI features are implemented as Python scripts. You will need Python 3.11 and the necessary libraries installed (Tesseract OCR, pytesseract, Pillow). The installation for Tesseract was:

```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr libtesseract-dev tesseract-ocr-eng
pip3 install pytesseract Pillow
```

### 4.1. Receipt Parser (`receipt_parser.py`)

This script takes an image file path as input, performs OCR to extract text, and then uses regular expressions to parse out the vendor name, transaction date, and total amount.

**Usage:**

```bash
python3.11 /home/ubuntu/receipt_parser.py <path_to_receipt_image> --output_json <path_to_output.json>
```

*   `<path_to_receipt_image>`: Replace with the actual path to a receipt image file (e.g., `.png`, `.jpg`).
*   `--output_json <path_to_output.json>`: (Optional) If provided, the script will save the parsed JSON data to the specified file.

**Example:**

1.  Save a sample receipt image (e.g., `sample_receipt.png`) in `/home/ubuntu/test_data/`.
2.  Run: `python3.11 /home/ubuntu/receipt_parser.py /home/ubuntu/test_data/sample_receipt.png --output_json /home/ubuntu/test_data/receipt_output.json`

**Output:**

The script will print the raw OCR text and the parsed JSON data to the console. If `--output_json` is used, the JSON will also be saved to the file.

```json
{
  "vendor_name": "Example Store",
  "transaction_date": "05/10/2025",
  "total_amount": 25.99,
  "raw_text": "... (full extracted text) ..."
}
```
*(Note: The accuracy of vendor/date/total extraction depends heavily on receipt quality and the robustness of the regex, which is simplified for this demonstration.)*

### 4.2. Spending Analyzer (`spending_analyzer.py`)

This script takes a JSON file containing a list of expense records and analyzes spending patterns.

**Input JSON Format (`expenses.json`):**

```json
[
  {
    "category_name": "Food",
    "amount": 12.50,
    "expense_date": "2025-04-10"
  },
  {
    "category_name": "Transport",
    "amount": 30.00,
    "expense_date": "2025-04-12"
  },
  {
    "category_name": "Food",
    "amount": 25.00,
    "expense_date": "2025-04-15"
  },
  {
    "category_name": "Utilities",
    "amount": 75.00,
    "expense_date": "2025-05-01"
  },
  {
    "category_name": "Food",
    "amount": 10.00,
    "expense_date": "2025-05-05"
  }
]
```

**Usage:**

```bash
python3.11 /home/ubuntu/spending_analyzer.py <path_to_expenses.json> --output_json <path_to_analysis_output.json> --period monthly --start_date YYYY-MM-DD --end_date YYYY-MM-DD
```

*   `<path_to_expenses.json>`: Path to your expense data file.
*   `--output_json`: (Optional) Save analysis to a file.
*   `--period`: (Optional) `monthly` (default) or `yearly` for aggregation.
*   `--start_date`, `--end_date`: (Optional) Filter expenses by date range.

**Example:**

1.  Create `sample_expenses.json` in `/home/ubuntu/test_data/` with the content above.
2.  Run: `python3.11 /home/ubuntu/spending_analyzer.py /home/ubuntu/test_data/sample_expenses.json --output_json /home/ubuntu/test_data/analysis_output.json --period monthly`

**Output:**

A JSON object with `summary`, `by_category`, and `over_time` analysis.

### 4.3. Predictive Budgeter (`predictive_budgeter.py`)

This script uses historical expense data (same format as `spending_analyzer.py`) to predict future spending, typically on a per-category basis using simple averaging.

**Usage:**

```bash
python3.11 /home/ubuntu/predictive_budgeter.py <path_to_expenses.json> --output_json <path_to_prediction_output.json> --category <CategoryName> --future_periods <N>
```

*   `<path_to_expenses.json>`: Path to your expense data file.
*   `--output_json`: (Optional) Save prediction to a file.
*   `--category`: (Optional) Predict for a specific category. If omitted, predicts based on all expenses (less meaningful for budgeting).
*   `--future_periods`: (Optional) Number of future periods (e.g., months) to predict. Default is 3.

**Example:**

1.  Use the same `sample_expenses.json` from `/home/ubuntu/test_data/`.
2.  Run: `python3.11 /home/ubuntu/predictive_budgeter.py /home/ubuntu/test_data/sample_expenses.json --output_json /home/ubuntu/test_data/prediction_output.json --category Food --future_periods 3`

**Output:**

A JSON object with predictions for the specified category.

## 5. Integration Concept

As detailed in `system_architecture.md`:

1.  **Receipt Upload:** User uploads an image to a XANO endpoint (e.g., `POST /receipts/upload`).
2.  **XANO Action:** XANO stores the image and creates a `receipts` record.
3.  **OCR Trigger:** XANO (via a background task or function) calls an external service that wraps `receipt_parser.py`. This service receives the image (or its path/ID).
4.  **OCR Processing:** `receipt_parser.py` processes the image.
5.  **Update XANO:** The external service calls a XANO endpoint (e.g., `PUT /receipts/{receiptId}/ocr-result`) to update the `receipts` table with extracted vendor, date, and total.
6.  **Expense Creation:** User can then create an expense, potentially linking it to the processed receipt.
7.  **Analysis & Prediction:** When a user requests spending analysis or predictions via dedicated XANO API endpoints (e.g., `GET /reports/spending-patterns`, `GET /reports/predictive-budgeting`):
    *   XANO queries the relevant expense data from its database.
    *   For complex analysis/predictions beyond XANO's direct capabilities, it would pass this data to an external service wrapping `spending_analyzer.py` or `predictive_budgeter.py`.
    *   The results are returned to XANO, which then sends them to the user.

*The XANO rate limit (10 requests/20 seconds on the free tier) is a critical consideration for these integrations, especially for callbacks from external services.*

## 6. Testing the System (Simulated)

*   **Backend APIs:** Once the XANO backend is set up as per the `xano_implementation_guide_simulated.md`, you can use XANO's built-in Swagger UI or a tool like Postman to test the API endpoints (e.g., register user, login, create expense).
*   **AI Scripts:** Test the Python scripts individually using the command-line examples provided above. You will need to create a `/home/ubuntu/test_data/` directory and place a sample receipt image and a `sample_expenses.json` file there.

    **Sample `sample_receipt.png`:** You would need to provide your own image file for testing `receipt_parser.py`.

    **Sample `sample_expenses.json` for `/home/ubuntu/test_data/`:**
    ```json
    [
      {"category_name": "Food", "amount": 12.50, "expense_date": "2025-03-10"},
      {"category_name": "Transport", "amount": 30.00, "expense_date": "2025-03-12"},
      {"category_name": "Food", "amount": 25.00, "expense_date": "2025-03-15"},
      {"category_name": "Entertainment", "amount": 50.00, "expense_date": "2025-03-20"},
      {"category_name": "Utilities", "amount": 75.00, "expense_date": "2025-04-01"},
      {"category_name": "Food", "amount": 10.00, "expense_date": "2025-04-05"},
      {"category_name": "Food", "amount": 15.50, "expense_date": "2025-04-10"},
      {"category_name": "Transport", "amount": 22.00, "expense_date": "2025-04-12"},
      {"category_name": "Utilities", "amount": 80.00, "expense_date": "2025-05-01"},
      {"category_name": "Food", "amount": 18.75, "expense_date": "2025-05-05"}
    ]
    ```

## 7. Deliverables Overview

The following key files constitute this project deliverable:

*   `/home/ubuntu/system_architecture.md`: Overall system design.
*   `/home/ubuntu/xano_implementation_guide_simulated.md`: Guide for setting up the XANO backend.
*   `/home/ubuntu/receipt_parser.py`: Python script for OCR and NLP.
*   `/home/ubuntu/spending_analyzer.py`: Python script for spending analysis.
*   `/home/ubuntu/predictive_budgeter.py`: Python script for predictive budgeting.
*   `/home/ubuntu/user_guide.md` (this file).
*   `/home/ubuntu/loom_video_script.md`: Script for the demonstration video.
*   `/home/ubuntu/todo.md`: Task checklist used during development.

**For Testing:**

*   **Swagger URL:** If you set up the XANO backend, XANO will provide a Swagger URL for your API group. This is how you would test the APIs.
*   **User Credentials:** After setting up XANO and the `/auth/register` endpoint, you can create a test user. These credentials would be used for testing authenticated API endpoints.

This concludes the user guide. Please refer to the individual script files and architecture documents for more specific details.
