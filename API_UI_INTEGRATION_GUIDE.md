# userdb API & UI Integration Guide

This guide provides practical details for integrating a login service and user management UI with the `userdb` library.

---

## API Endpoints

| Endpoint                | Method | Description                        |
|------------------------|--------|------------------------------------|
| `/auth/jwt/login`      | POST   | User login (returns JWT)           |
| `/auth/register`       | POST   | User registration                  |
| `/users/`              | GET    | List users (admin only)            |
| `/users/me`            | GET    | Get current user info              |
| `/auth/forgot-password`| POST   | Request password reset (if enabled)|
| `/auth/reset-password` | POST   | Reset password (if enabled)        |
| `/auth/verify`         | POST   | Email verification (if enabled)    |

---

## Example Requests & Responses

### Login
**Request:**
```json
POST /auth/jwt/login
{
  "username": "user@example.com",
  "password": "password"
}
```
**Response:**
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### Registration
**Request:**
```json
POST /auth/register
{
  "email": "user@example.com",
  "password": "password",
  "full_name": "User Name"
}
```
**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

### Get Current User
**Request:**
```http
GET /users/me
Authorization: Bearer <access_token>
```
**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true,
  "is_superuser": false,
  "is_verified": true
}
```

---

## Using JWT in the UI
- After login, store the `access_token` securely (e.g., in memory, or localStorage with security caveats).
- For all authenticated API requests, send the token in the `Authorization` header:
  ```http
  Authorization: Bearer <access_token>
  ```
- Log out by deleting the token from storage.

---

## User Model Example
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true,
  "is_superuser": false,
  "is_verified": true
}
```

---

## CORS & Security for UI Integration
- Set `allow_origins` in your FastAPI CORS middleware to the UI's domain(s).
- Always use HTTPS in production.
- Never expose secrets or tokens in client-side code.
- Consider rate limiting and brute-force protection.

---

## Error Handling & Status Codes
- `401 Unauthorized`: Invalid or missing token.
- `400 Bad Request`: Invalid input (e.g., bad email/password).
- `403 Forbidden`: Not enough permissions (e.g., non-admin accessing `/users/`).
- `422 Unprocessable Entity`: Validation errors.
- UI should display user-friendly error messages for these cases.

---

## Password Reset & Email Verification
- If enabled, users can request a password reset via `/auth/forgot-password`.
- The UI should prompt for email, then handle the reset link sent by email.
- Email verification can be triggered and handled similarly.
- See [fastapi-users docs](https://frankie567.github.io/fastapi-users/) for more details.

---

## Extending the User Model for UI
- Add fields to the `User` model and Pydantic schemas in your backend.
- Update the UI to display/edit new fields as needed.
- Keep API and UI in sync regarding user data shape.

---

## Practical Tips
- Use OpenAPI docs (`/docs`) to explore and test endpoints.
- Use tools like Postman or HTTPie for manual API testing.
- For production, always use migrations for DB changes.
- Keep your UI and backend CORS settings in sync.

---

For more details, see the main README and the [fastapi-users documentation](https://frankie567.github.io/fastapi-users/).
