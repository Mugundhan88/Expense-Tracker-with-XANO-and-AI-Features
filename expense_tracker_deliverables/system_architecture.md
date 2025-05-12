# Expense Tracker System Architecture

This document outlines the system architecture for the Expense Tracker application, focusing on the XANO backend, database schema, API endpoints, and AI feature integration.

## 1. Guiding Principles & Constraints

*   **Backend Platform:** XANO (Free Tier)
*   **Key XANO Free Tier Constraints:**
    *   1 Workspace, 1 Team Member
    *   100,000 Total Data Records
    *   1GB Database SSD Storage
    *   1GB Image/File Storage (Images only, watermarked)
    *   API Rate Limit: 10 requests per 20 seconds (critical for design)
    *   File Upload Limit: 64MB per file
    *   5 Background Tasks
*   AI features will be designed to work within these constraints, potentially leveraging external services for heavy processing if XANO internal functions are insufficient or hit limits.

## 2. Database Schema (XANO)

The following tables will be created in the XANO database.

### 2.1. `users` Table

Stores user account information.

*   `id` (Primary Key, Integer, Auto-increment)
*   `email` (Text, Unique, Indexed) - User's email address.
*   `password_hash` (Text) - Hashed password for security.
*   `created_at` (Timestamp, Default: Now)
*   `updated_at` (Timestamp, Default: Now)

### 2.2. `categories` Table

Stores expense categories. Can be predefined or user-defined.

*   `id` (Primary Key, Integer, Auto-increment)
*   `user_id` (Foreign Key to `users.id`, Integer, Nullable) - If null, it's a system-wide predefined category. Otherwise, it's user-specific.
*   `name` (Text, Indexed) - Name of the category (e.g., "Food", "Transport", "Groceries").
*   `created_at` (Timestamp, Default: Now)
*   `updated_at` (Timestamp, Default: Now)
*   *Constraint:* Unique combination of `user_id` and `name` for user-defined categories.

### 2.3. `expenses` Table

Stores individual expense records.

*   `id` (Primary Key, Integer, Auto-increment)
*   `user_id` (Foreign Key to `users.id`, Integer, Indexed, Not Null) - The user who owns this expense.
*   `category_id` (Foreign Key to `categories.id`, Integer, Indexed, Not Null) - The category of the expense.
*   `amount` (Decimal/Float, Not Null) - The monetary value of the expense.
*   `description` (Text, Nullable) - A brief description of the expense.
*   `expense_date` (Date/Timestamp, Not Null) - The date the expense was incurred.
*   `receipt_id` (Foreign Key to `receipts.id`, Integer, Nullable, Indexed) - Link to an associated uploaded receipt.
*   `created_at` (Timestamp, Default: Now)
*   `updated_at` (Timestamp, Default: Now)

### 2.4. `receipts` Table

Stores information about uploaded receipt images and their OCR processing status.

*   `id` (Primary Key, Integer, Auto-increment)
*   `user_id` (Foreign Key to `users.id`, Integer, Indexed, Not Null) - The user who uploaded the receipt.
*   `file_name_original` (Text) - Original name of the uploaded file.
*   `file_path_xano` (Text) - Path/URL to the stored file within XANO's file storage.
*   `mime_type` (Text) - MIME type of the uploaded file (e.g., "image/jpeg").
*   `size_bytes` (Integer) - Size of the file in bytes.
*   `ocr_status` (Enum/Text, Default: "pending") - Status of OCR processing: "pending", "processing", "completed", "failed".
*   `ocr_text_raw` (Text, Nullable) - Raw text extracted by the OCR process.
*   `extracted_vendor_name` (Text, Nullable) - Vendor name extracted by NLP from OCR text.
*   `extracted_transaction_date` (Date, Nullable) - Transaction date extracted by NLP.
*   `extracted_total_amount` (Decimal/Float, Nullable) - Total amount extracted by NLP.
*   `uploaded_at` (Timestamp, Default: Now)
*   `processed_at` (Timestamp, Nullable) - Timestamp when OCR/NLP processing finished.

## 3. API Endpoints (XANO)

All endpoints will be versioned, e.g., `/api/v1/`. Authentication will be required for most endpoints, likely using JWTs managed by XANO.

### 3.1. Authentication (`/auth`)

*   `POST /register`
    *   Description: Register a new user.
    *   Request Body: `{ "email": "user@example.com", "password": "securepassword123" }`
    *   Response: `{ "user_id": 123, "email": "user@example.com", "token": "YOUR_JWT_TOKEN" }` (201 Created)
*   `POST /login`
    *   Description: Log in an existing user.
    *   Request Body: `{ "email": "user@example.com", "password": "securepassword123" }`
    *   Response: `{ "user_id": 123, "email": "user@example.com", "token": "YOUR_JWT_TOKEN" }` (200 OK)
*   `POST /logout` (Requires Auth)
    *   Description: Log out the current user (invalidate token if possible on XANO).
    *   Response: (204 No Content or 200 OK)

### 3.2. Categories (`/categories` - Requires Auth)

*   `GET /`
    *   Description: List all available categories (predefined system categories + user-specific categories).
    *   Response: `[{ "id": 1, "name": "Food", "user_id": null, "is_custom": false }, ...]` (200 OK)
*   `POST /`
    *   Description: Create a new custom category for the authenticated user.
    *   Request Body: `{ "name": "Personal Shopping" }`
    *   Response: `{ "id": 15, "name": "Personal Shopping", "user_id": 123, "is_custom": true }` (201 Created)
*   `PUT /{categoryId}`
    *   Description: Update a user-owned custom category.
    *   Request Body: `{ "name": "Updated Category Name" }`
    *   Response: `{ "id": 15, ... }` (200 OK)
*   `DELETE /{categoryId}`
    *   Description: Delete a user-owned custom category (if not in use by expenses, or handle accordingly).
    *   Response: (204 No Content)

### 3.3. Expenses (`/expenses` - Requires Auth)

*   `GET /`
    *   Description: List expenses for the authenticated user. Supports filtering by date range, category.
    *   Query Parameters: `?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD&categoryId=1&page=1&limit=20`
    *   Response: `{ "data": [{...expense_object...}], "pagination": { "total_records": 100, "current_page": 1, ...} }` (200 OK)
*   `POST /`
    *   Description: Create a new expense record.
    *   Request Body: `{ "category_id": 1, "amount": 19.99, "description": "Lunch with client", "expense_date": "YYYY-MM-DD", "receipt_id": null }`
    *   Response: `{...new_expense_object...}` (201 Created)
*   `GET /{expenseId}`
    *   Description: Get details of a specific expense.
    *   Response: `{...expense_object...}` (200 OK)
*   `PUT /{expenseId}`
    *   Description: Update an existing expense.
    *   Request Body: `{ "amount": 20.50, "description": "Updated lunch details" }`
    *   Response: `{...updated_expense_object...}` (200 OK)
*   `DELETE /{expenseId}`
    *   Description: Delete an expense.
    *   Response: (204 No Content)

### 3.4. Receipts & OCR (`/receipts` - Requires Auth)

*   `POST /upload`
    *   Description: Upload a receipt image. This will trigger an asynchronous OCR process.
    *   Request: Multipart form data (e.g., `file` field with the image).
    *   Response: `{ "receipt_id": 789, "file_name_original": "receipt.jpg", "ocr_status": "pending" }` (202 Accepted)
*   `GET /{receiptId}`
    *   Description: Get details of a specific receipt, including OCR status and extracted data.
    *   Response: `{ "id": 789, ..., "ocr_status": "completed", "ocr_text_raw": "...", "extracted_vendor_name": "Cafe X", ... }` (200 OK)
*   `POST /expenses/from-receipt/{receiptId}` (Convenience Endpoint)
    *   Description: Create an expense record from a processed receipt's extracted data.
    *   Request Body: (Optional) `{ "category_id": 5, "description_override": "Business Lunch" }` (to override or add info)
    *   Response: `{...new_expense_object_created_from_receipt...}` (201 Created)

### 3.5. Analysis & Predictions (`/reports` - Requires Auth)

*   `GET /spending-patterns`
    *   Description: Get analysis of spending patterns (e.g., by category, over time).
    *   Query Parameters: `?period=monthly&startDate=YYYY-MM-DD&endDate=YYYY-MM-DD`
    *   Response: `{ "summary": { "total_spent": 1250.75 }, "by_category": [{ "category_name": "Food", "total": 400.50, "percentage": 32.02 }, ...], "over_time": [{ "period_label": "April 2025", "total": 600.00 }, ...] }` (200 OK)
*   `GET /predictive-budgeting`
    *   Description: Get predictive budgeting insights based on historical spending.
    *   Query Parameters: `?category_id=1&future_periods=3` (e.g., predict for next 3 months for category 1)
    *   Response: `{ "category_name": "Food", "average_monthly_spend": 150.00, "predictions": [{ "period_label": "June 2025", "predicted_spend": 155.00, "confidence_level": "medium" }, ...] }` (200 OK)

## 4. AI Feature Integration Strategy

### 4.1. Receipt Image Recognition (OCR + NLP)

1.  **Upload:** User uploads receipt image via `POST /receipts/upload`.
2.  **Storage & Queuing:** XANO stores the image (max 64MB, watermarked on free tier) and creates a `receipts` record with `ocr_status: "pending"`.
3.  **Processing (Asynchronous - External Service Preferred):**
    *   A XANO background task or a trigger (if available on new record creation) makes an API call to an external AI service (e.g., a Python Flask/FastAPI app, AWS Lambda, Google Cloud Function).
    *   This external service will:
        *   Fetch the image from XANO (if XANO provides a temporary secure URL) or be passed the image data directly (less ideal for large files).
        *   Perform OCR using a library like Tesseract or a cloud service (e.g., Google Vision AI API, AWS Textract - considering their free tiers).
        *   Perform NLP on the OCR text to extract vendor, date, total amount, and potentially line items (using regex, simple NLP libraries, or more advanced models if budget/complexity allows).
        *   Call a dedicated XANO API endpoint (e.g., `PUT /receipts/{receiptId}/ocr-result`) to update the `receipts` record with the extracted data and set `ocr_status` to "completed" or "failed".
4.  **Rate Limiting:** Calls from XANO to the external service and from the external service back to XANO must respect XANO's 10 req/20s limit. The external service should handle its own scaling and processing time without blocking XANO.

### 4.2. Spending Pattern Analysis

*   This will primarily be handled within XANO.
*   The `GET /reports/spending-patterns` endpoint will trigger XANO functions/queries.
*   These functions will perform database aggregations (SUM, GROUP BY) on the `expenses` table, joined with `categories` and filtered by user and date ranges.
*   XANO's data manipulation capabilities will be used to structure the JSON response.
*   Complex, long-running analyses might strain XANO's free tier; if so, a hybrid approach (XANO provides raw data to an external service for analysis) could be considered, but the goal is to do this within XANO if possible.

### 4.3. Predictive Budgeting

*   This will also aim to be handled within XANO for simplicity on the free tier.
*   The `GET /reports/predictive-budgeting` endpoint will trigger XANO functions.
*   The logic will involve:
    *   Querying historical expense data for the user/category.
    *   Applying a simple forecasting algorithm (e.g., moving average, simple linear regression on past few periods' spending).
    *   XANO's function stack would need to support basic arithmetic and conditional logic to implement this.
*   For more sophisticated ML-based predictions, an external AI service would be necessary, similar to the OCR flow.

## 5. XANO Specific Considerations

*   **Swagger/OpenAPI:** XANO automatically generates OpenAPI documentation for the defined API endpoints. This URL will be provided as part of the submission.
*   **User Credentials for Testing:** Test user accounts will be created using the `POST /auth/register` endpoint. Credentials for one such account will be provided.
*   **Simulation:** If direct XANO implementation is not possible (e.g., due to account creation constraints for the AI), this document will serve as the detailed blueprint. Python scripts will be developed for the AI features, and their interaction with these defined XANO APIs will be simulated/documented.

This architecture aims to meet the project requirements while respecting the constraints of XANO's free tier. The most significant challenge will be the API rate limit and the delegation of intensive AI tasks to external services if XANO's internal capabilities are exceeded.
