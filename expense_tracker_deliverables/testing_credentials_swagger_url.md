# Testing Credentials and Swagger URL

This document provides information on how to obtain testing credentials and the Swagger URL for the Expense Tracker application, assuming the XANO backend has been set up as per the `xano_implementation_guide_simulated.md`.

## 1. User Credentials for Testing

Since the XANO backend implementation is simulated for this project, actual pre-created user credentials cannot be provided directly. However, if you implement the backend in XANO following the `xano_implementation_guide_simulated.md`, you would create test user credentials as follows:

1.  **Ensure the `POST /api/v1/auth/register` endpoint is correctly implemented in your XANO instance.** This endpoint is designed to take an email and password, hash the password, and store the new user in the `users` table.
2.  **Use a tool like Postman or XANO's built-in API testing interface to send a POST request to your `/api/v1/auth/register` endpoint.**

    *   **Method:** `POST`
    *   **URL:** `[Your_XANO_Base_URL]/api/v1/auth/register`
    *   **Body (JSON):**
        ```json
        {
          "email": "testuser@example.com",
          "password": "TestPassword123!"
        }
        ```
3.  **Upon successful registration, the API should return a response including a JWT token.** You can then use this `testuser@example.com` and `TestPassword123!` (or any other credentials you choose to register) to test authenticated endpoints by including the received JWT token in the `Authorization` header (e.g., `Authorization: Bearer YOUR_JWT_TOKEN`).

**Example Test Credentials (to be created by you):**

*   **Email:** `testuser@example.com`
*   **Password:** `TestPassword123!`

## 2. Swagger URL (OpenAPI Specification)

XANO automatically generates an OpenAPI (Swagger) specification for the API endpoints you create within an API Group.

To obtain the Swagger URL once you have set up the backend in your XANO instance:

1.  Navigate to your XANO Workspace.
2.  Go to the "API" section.
3.  Select the API Group you created for the Expense Tracker (e.g., "Expense Tracker v1").
4.  Within the API Group settings or main page, XANO typically provides a direct link to the Swagger documentation. This is often labeled as "Swagger Documentation," "OpenAPI Spec," or similar.
5.  The URL will look something like: `https://[Your_XANO_Instance_Subdomain].xano.io/api:[Your_API_Group_ID]/swagger.json` or a more user-friendly UI path like `https://[Your_XANO_Instance_Subdomain].xano.io/api:[Your_API_Group_ID]/

This Swagger URL can be used with tools like Swagger UI or Postman to explore and test your API endpoints interactively.

**Note:** The exact location and naming for the Swagger URL might vary slightly based on XANO UI updates, so refer to the current XANO documentation if needed.
