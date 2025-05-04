# Integration Testing with Locksmitha

When writing integration tests for services that use Locksmitha for authentication, follow these guidelines:

### 1. **Test Setup**

1. **Install Dependencies**
   ```bash
   pip install fastapi httpx pytest pytest-asyncio keylin
   ```

2. **Configure Test Environment**
   ```bash
   # For tests, you can use any test secret - it doesn't need to match Locksmitha
   # The test will use this secret for both creating and validating JWTs
   export KEYLIN_JWT_SECRET="test_secret"
   ```

> **Note:** In tests, the JWT secret doesn't need to match the one used by Locksmitha. This is because:
> - Tests are self-contained and don't communicate with the real Locksmitha service
> - The same test secret is used for both creating and validating JWTs
> - This allows tests to run independently and reliably without external dependencies
>
> In production, however, the `KEYLIN_JWT_SECRET` must match the one used by Locksmitha.

### 2. **Writing Tests**

1. **Create Test JWTs**
   ```python
   from uuid import UUID
   from keylin.jwt_utils import create_jwt_for_user

   # Create a test user ID (use a consistent UUID for your tests)
   test_user_id = UUID("12345678-1234-5678-1234-567812345678")
   test_email = "test@example.com"

   # Create a JWT for this user
   # This will use the test secret from KEYLIN_JWT_SECRET
   jwt = create_jwt_for_user(test_user_id, test_email)
   ```

2. **Test Protected Endpoints**
   ```python
   import pytest
   from httpx import AsyncClient
   from fastapi import FastAPI, Depends, HTTPException
   from fastapi.security import HTTPBearer
   import jwt
   from keylin.config import JWT_SECRET, JWT_ALGORITHM

   app = FastAPI()
   security = HTTPBearer()

   async def get_current_user(credentials = Depends(security)) -> UUID:
       try:
           # This will use the same test secret for validation
           payload = jwt.decode(
               credentials.credentials,
               JWT_SECRET,
               algorithms=[JWT_ALGORITHM]
           )
           return UUID(payload["sub"])
       except Exception as e:
           raise HTTPException(status_code=401)

   @pytest.mark.asyncio
   async def test_protected_endpoint():
       async with AsyncClient(app=app) as client:
           # Create JWT for test user
           jwt = create_jwt_for_user(test_user_id, test_email)

           # Test the endpoint
           response = await client.get(
               "/protected",
               headers={"Authorization": f"Bearer {jwt}"}
           )
           assert response.status_code == 200
   ```

### 3. **Test Scenarios**

Always test these scenarios in your integration tests:

1. **Valid JWT**
   - Token created with test secret
   - Valid user ID and email
   - Not expired

2. **Invalid JWT**
   - Wrong secret
   - Malformed token
   - Missing required claims

3. **Expired JWT**
   - Token past expiration time
   - Token with very short expiry

4. **Missing JWT**
   - No Authorization header
   - Empty token

## Key Rotation Strategy

### 1. **Production Setup**

- Use a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault) to manage JWT secrets
- Rotate secrets regularly (recommended: every 30 days)
- Use a grace period (e.g., 1 hour) to allow existing tokens to be validated

### 2. **Implementation Steps**

1. **Generate New Secret**
   ```bash
   # Generate a strong random secret
   openssl rand -base64 32
   ```

2. **Update Secrets Manager**
   - Add new secret to your secrets manager
   - Keep old secret for grace period
   - Update Locksmitha to use new secret

3. **Update Environment Variables**
   - Update `KEYLIN_JWT_SECRET` in all services
   - Ensure all services are updated within grace period

### 3. **Best Practices**

- **Never hardcode secrets** in code or configuration files
- **Use different secrets** for development, testing, and production
- **Monitor token validation** during rotation to catch any issues
- **Log secret rotation events** for audit purposes
- **Test rotation process** in staging environment first

### 4. **Security Considerations**

1. **Secret Management**
   - Use strong, random secrets
   - Rotate secrets regularly
   - Never commit secrets to version control

2. **Token Validation**
   - Validate all required claims
   - Check token expiration
   - Verify token signature

3. **Error Handling**
   - Don't expose sensitive details in error messages
   - Log validation failures for monitoring
   - Use appropriate HTTP status codes
