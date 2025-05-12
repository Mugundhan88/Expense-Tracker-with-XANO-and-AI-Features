# XANO Backend Implementation Guide (Simulated)

This document provides a step-by-step guide on how to implement the backend for the Expense Tracker application within XANO, based on the designed system architecture. Since direct access to a XANO instance is not available for this AI, these steps describe the process as it would be performed manually in the XANO interface.

**Prerequisites:**

*   A XANO account (Free Tier is sufficient for this design).
*   Familiarity with the XANO interface (Workspace, Database, API sections).

**Reference:** The `system_architecture.md` document contains the detailed database schema and API endpoint definitions.

## 1. Workspace Setup

1.  Log in to your XANO account.
2.  If you don't have one, create a new Workspace. The free tier allows for one workspace.

## 2. Database Table Creation

Navigate to the "Database" section of your XANO workspace. For each table defined in `system_architecture.md`, perform the following:

### 2.1. `users` Table

1.  Click "Add Table".
2.  Name the table `users`.
3.  Add the following fields (columns) with their respective types and settings:
    *   `id`: (Automatically created as Primary Key, Integer, Auto-increment)
    *   `email`: Type `text`. Add a unique index to this field. Mark as required.
    *   `password_hash`: Type `text`. Mark as required.
    *   `created_at`: Type `timestamp`. Set default to `Now`.
    *   `updated_at`: Type `timestamp`. Set default to `Now`.
4.  Save the table.

### 2.2. `categories` Table

1.  Click "Add Table".
2.  Name the table `categories`.
3.  Add the following fields:
    *   `id`: (Primary Key, Integer, Auto-increment)
    *   `user_id`: Type `table_reference` pointing to `users.id`. Allow null (for system-wide categories). Add an index.
    *   `name`: Type `text`. Add an index. Mark as required.
    *   `created_at`: Type `timestamp`. Set default to `Now`.
    *   `updated_at`: Type `timestamp`. Set default to `Now`.
4.  *Constraint Note:* XANO might not directly support unique constraints on a combination of `user_id` and `name` through the UI. This logic would need to be enforced in the API business logic (e.g., before creating a new category, check if a category with the same name already exists for that user).
5.  Save the table.
6.  *Predefined Categories (Optional):* You can add some initial system-wide categories by adding records to this table with `user_id` set to `null`. Examples: "Food", "Transport", "Utilities".

### 2.3. `expenses` Table

1.  Click "Add Table".
2.  Name the table `expenses`.
3.  Add the following fields:
    *   `id`: (Primary Key, Integer, Auto-increment)
    *   `user_id`: Type `table_reference` pointing to `users.id`. Mark as required. Add an index.
    *   `category_id`: Type `table_reference` pointing to `categories.id`. Mark as required. Add an index.
    *   `amount`: Type `decimal` or `float`. Mark as required.
    *   `description`: Type `text`. Allow null.
    *   `expense_date`: Type `date` or `timestamp`. Mark as required.
    *   `receipt_id`: Type `table_reference` pointing to `receipts.id`. Allow null. Add an index.
    *   `created_at`: Type `timestamp`. Set default to `Now`.
    *   `updated_at`: Type `timestamp`. Set default to `Now`.
4.  Save the table.

### 2.4. `receipts` Table

1.  Click "Add Table".
2.  Name the table `receipts`.
3.  Add the following fields:
    *   `id`: (Primary Key, Integer, Auto-increment)
    *   `user_id`: Type `table_reference` pointing to `users.id`. Mark as required. Add an index.
    *   `file_name_original`: Type `text`.
    *   `file_path_xano`: Type `file` (XANO's special type for file references) or `text` if storing a URL/path manually. XANO's `file` metadata type is preferred as it handles storage integration.
    *   `mime_type`: Type `text`.
    *   `size_bytes`: Type `integer`.
    *   `ocr_status`: Type `text` (or `enum` if XANO supports it directly). Default to "pending". Values: "pending", "processing", "completed", "failed".
    *   `ocr_text_raw`: Type `text_long` or `text` (choose based on expected length). Allow null.
    *   `extracted_vendor_name`: Type `text`. Allow null.
    *   `extracted_transaction_date`: Type `date`. Allow null.
    *   `extracted_total_amount`: Type `decimal` or `float`. Allow null.
    *   `uploaded_at`: Type `timestamp`. Set default to `Now`.
    *   `processed_at`: Type `timestamp`. Allow null.
4.  Save the table.

## 3. API Endpoint Creation

Navigate to the "API" section of your XANO workspace. Create a new API Group (e.g., "Expense Tracker v1"). Within this group, create the endpoints as defined in `system_architecture.md`.

For each endpoint:

1.  Click "Add API Endpoint".
2.  Choose the HTTP method (GET, POST, PUT, DELETE).
3.  Define the path (e.g., `/auth/register`, `/expenses/{expenseId}`).
4.  **Inputs:** Define any expected inputs (from query, path variables, or request body) according to the architecture document. XANO allows you to specify types for these inputs.
5.  **Function Stack:** This is where the core logic of the API resides. For each endpoint, you will build a function stack:
    *   **Authentication:** For protected endpoints, add a XANO authentication function (e.g., JWT-based) at the beginning of the stack.
    *   **Database Operations:** Use XANO's database connector functions (Create Record, Query Records, Update Record, Delete Record) to interact with the tables created in Step 2.
    *   **Input Validation:** Add validation steps for inputs.
    *   **Conditional Logic:** Use XANO's utility functions for if/else conditions, loops, etc.
    *   **Password Hashing:** For user registration and login, use XANO's password hashing functions (e.g., Bcrypt).
    *   **File Uploads (for `POST /receipts/upload`):** XANO has specific functions to handle file inputs and store them. The `file_path_xano` in the `receipts` table would be populated with the metadata from this upload.
    *   **External API Calls (for OCR integration):** For the OCR processing trigger, the function stack for `POST /receipts/upload` (or a subsequent background task) would include an "External API Request" function to call your AI service. Similarly, the AI service would call a dedicated XANO endpoint (e.g., `PUT /receipts/{receiptId}/ocr-result`) to update the record.
    *   **Response:** Configure the output of the API endpoint, ensuring it matches the structure defined in `system_architecture.md`.

### Example: `POST /auth/register` Function Stack (Conceptual)

1.  **Inputs:** `email` (text), `password` (text).
2.  **Function 1 (Precondition):** Check if user with `email` already exists in `users` table. If yes, return error (e.g., 409 Conflict).
3.  **Function 2 (Password Hash):** Hash the input `password` using Bcrypt.
4.  **Function 3 (Create Record):** Create a new record in the `users` table with `email` and the `hashed_password`.
5.  **Function 4 (Generate JWT):** Generate a JWT token for the newly created user.
6.  **Response:** Return `user_id`, `email`, and `token`.

### Example: `POST /receipts/upload` Function Stack (Conceptual)

1.  **Inputs:** `file` (file input).
2.  **Authentication:** Ensure user is authenticated.
3.  **Function 1 (File Upload):** Process the `file` input, store it using XANO's file handling. Get metadata (name, path, size, MIME type).
4.  **Function 2 (Create Record):** Create a record in the `receipts` table with `user_id`, file metadata, and `ocr_status: "pending"`.
5.  **Function 3 (Trigger OCR - Asynchronous):**
    *   Option A (Background Task): Add the `receipt_id` to a XANO task queue (if free tier supports this robustly for external calls) or create a XANO background task that will call the external OCR service.
    *   Option B (Direct Call, if simple): Make an immediate, non-blocking call to the external OCR service API, passing `receipt_id` and perhaps a temporary URL to the image if XANO provides one. *Careful with XANO's request timeouts and rate limits here.*
6.  **Response:** Return `receipt_id`, `file_name_original`, `ocr_status: "pending"` (202 Accepted).

## 4. Setting up AI Feature Interactions

As described in `system_architecture.md` and the endpoint examples above:

*   **OCR Service:** You will need a separate AI service (e.g., a Python Flask/FastAPI application) that performs OCR and NLP.
    *   This service needs an endpoint that XANO can call (e.g., `POST /process-receipt`).
    *   This service will then call back to a XANO endpoint (e.g., `PUT /api/v1/receipts/{receiptId}/ocr-result`) to update the `receipts` table with the extracted data. Ensure this callback endpoint in XANO is secured (e.g., with a secret API key checked in the function stack).
*   **Spending Pattern Analysis & Predictive Budgeting:**
    *   These are designed to be implemented primarily using XANO's database query and function stack capabilities within their respective API endpoints (`GET /reports/spending-patterns`, `GET /reports/predictive-budgeting`).
    *   This involves querying the `expenses` table, performing aggregations (SUM, AVG, GROUP BY), and potentially some basic calculations for predictions.

## 5. Testing

*   Use XANO's built-in API testing interface or an external tool like Postman.
*   Test each endpoint thoroughly according to its definition in `system_architecture.md`.
*   Verify authentication, input validation, correct database operations, and response formats.

## 6. Swagger (OpenAPI) URL

Once your API endpoints are defined in XANO, it automatically generates an OpenAPI (Swagger) specification. You can typically find the URL for this in your XANO API Group settings. This URL will be one of the deliverables.

## 7. User Credentials for Testing

Once the `POST /auth/register` endpoint is working, you can use it to create a test user account. The email and password for this test account will be provided as part of the submission deliverables.

This guide provides a high-level overview of the simulated XANO backend setup. The actual implementation within XANO involves using its visual programming interface to construct the function stacks for each API endpoint. Refer to the official XANO documentation for detailed instructions on using specific XANO features and functions.
