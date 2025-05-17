# Manual Password Reset Guide (Using Curl)

This guide provides step-by-step instructions on how to manually reset a user's password using `curl`. This is useful when:
- A frontend application for handling password resets is not available or not yet set up.
- You need to directly test the backend's password reset functionality.

## Prerequisites

1.  Your `login` FastAPI backend application is running (typically on `http://localhost:8001`).
2.  Mailpit (or your configured mail catching service) is running and accessible (typically on `http://localhost:8025` for Mailpit).
3.  You have an existing user account in the system whose password you want to reset.
4.  `curl` command-line tool is installed on your system.

## Steps

### Step 1: Trigger the "Forgot Password" Request

First, you need to tell the backend that a user has forgotten their password. This will trigger an email with a reset token.

*   **Using Swagger UI (if available):**
    1.  Navigate to your backend's API documentation (e.g., `http://localhost:8001/docs`).
    2.  Find the "forgot password" endpoint (usually `POST /auth/forgot-password`).
    3.  Execute it by providing the email address of the user.
*   **Using `curl`:**
    Open your terminal and run the following command, replacing `user@example.com` with the email address of the user whose password you want to reset:
    ```bash
    curl -X POST http://localhost:8001/auth/forgot-password \
         -H "Content-Type: application/json" \
         -d '{"email": "user@example.com"}'
    ```
    A successful request should return a `202 Accepted` status from the server.

### Step 2: Retrieve the Reset Email from Mailpit

1.  Open your web browser and navigate to Mailpit (e.g., `http://localhost:8025`).
2.  You should find an email sent to the user's email address with a subject like "Password Reset". Open this email.

### Step 3: Extract the Password Reset Token

1.  Inside the email, look for the password reset link. It will typically look like:
    `http://localhost:3000/reset-password?token=SOME_LONG_TOKEN_STRING`
    (Note: The `localhost:3000` part is for the frontend, which we are bypassing. The important part is the token.)
2.  Carefully copy **only the token part** – the long string of characters that appears after `token=`.

    **Example:**
    If the link is: `http://localhost:3000/reset-password?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`
    The token to copy is: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

### Step 4: Choose a New Password

Decide on the new password you want to set for the user.
For example: `MyNewSecureP@ssw0rd!`

### Step 5: Send the Reset Password Request via `curl`

This step uses the extracted token and your new password to tell the backend to perform the actual password update.

1.  Open your terminal.
2.  Construct the following `curl` command. **Ensure you replace the placeholder values with your actual token and new password.**

    ```bash
    curl -X POST http://localhost:8001/auth/reset-password \
         -H "Content-Type: application/json" \
         -d '{
               "token": "PASTE_YOUR_EXTRACTED_TOKEN_HERE",
               "password": "ENTER_YOUR_CHOSEN_NEW_PASSWORD_HERE"
             }'
    ```

    **Example with placeholders filled:**
    ```bash
    curl -X POST http://localhost:8001/auth/reset-password \
         -H "Content-Type: application/json" \
         -d '{
               "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
               "password": "MyNewSecureP@ssw0rd!"
             }'
    ```
    *(Remember to use your actual token from Step 3 and your chosen new password from Step 4.)*

3.  Execute the command.

### Step 6: Check the Server's Response

*   **Successful Reset:** If the token is valid and the password meets any requirements, the backend should respond with a `200 OK` status. The response body might be empty or contain a simple success message (e.g., `{}`).
*   **Failed Reset:** If there's an issue, you'll likely receive an error status code:
    *   `400 Bad Request`: Often indicates an invalid/expired token or that the password doesn't meet complexity rules. The response body usually includes a `detail` field explaining the error (e.g., `{"detail":"RESET_PASSWORD_BAD_TOKEN"}` or `{"detail":"RESET_PASSWORD_INVALID_PASSWORD"}`).
    *   `422 Unprocessable Entity`: The JSON payload might be malformed or missing required fields.

### Step 7: Verify the New Password

Try logging in as the user with their email address and the new password you set in Step 4. You can do this via your application's login endpoint (e.g., using `curl` against `http://localhost:8001/auth/jwt/login` or through Swagger UI).

If login is successful, the password has been reset!

---
For further assistance, refer to the main project `README.md` or application logs.
