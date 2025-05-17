# Authentication and Authorization Patterns

This document outlines two common patterns for handling user authentication and authorization in a microservices architecture, with Service B using Service A as a downstream dependency and leveraging API keys for authorization. Here service B could be a function running in a notebook that has code calls service A.

## Authentication vs Authorization

### Authentication
- Verifies the identity of a user or service
- Typically done using username/password for users or mutual TLS/client credentials for services
- Proves "who you are"
- Example: User logging in with credentials, Service B authenticating to Service A

### Authorization
- Determines what a user or service can access
- Typically done using tokens (JWT) for users or API keys for services
- Proves "what you can do"
- Example: Using JWT for user access, API key for Service B to access Service A resources

## Pattern 1: Service-Managed API Keys

In this pattern, each service manages its own API keys for authorization, while a centralized login service handles user authentication.

### Components

1. **Login Service**
   - Manages user credentials (username/password) - Authentication
   - Handles user authentication
   - Issues JWT tokens - Authorization for users
   - Does not manage API keys

2. **Service A (API Key Issuer and Validator)**
   - Handles user login requests
   - Forwards authentication to Login Service
   - Validates JWTs locally using shared secret (HMAC) or public key (RSA/ECDSA)
   - Issues and manages its own API keys - Authorization for services
   - Stores API key hashes locally
   - Validates API keys for Service B requests

3. **Service B (API Key User)**
   - Distinct service using Service A as a downstream dependency
   - Retrieves stored API keys from environment variables or secure vault
   - Includes API keys in `x-api-key` header for authorization when calling Service A
   - Processes user requests and integrates Service A responses

### Authentication and Authorization Flow

1. **User Authentication**
   ```
   User -> Service A: Login with username/password (Authentication)
   Service A -> Login Service: Forward credentials
   Login Service -> Service A: Return JWT with user claims (Authorization)
   Service A -> User: Return JWT
   ```

2. **API Key Provisioning (Authorization for Service B)**
   ```
   Admin -> Service A: Request API key for Service B (with JWT)
   Service A: Validate JWT, extract claims (e.g., admin ID, roles)
   Service A: Generate secure random API key with Service B-specific scope
   Service A: Hash API key, store hash with metadata (Service B ID, scope, expiry)
   Service A -> Admin: Return plaintext API key
   Admin: Store API key in Service B’s environment variables or secure vault
   ```

3. **Service-to-Service Communication (Authorization)**
   ```
   User -> Service B: Request X (e.g., with JWT for user authorization)
   Service B: Validate JWT to authorize user request
   Service B: Retrieve Service A’s API key from secure vault or environment
   Service B -> Service A: Request Y with API key in x-api-key header for authorization
   Service A: Hash API key, check local storage to confirm authorization
   Service A -> Service B: Return 200 with data for request Y if authorized, 403 if unauthorized
   Service B: Process Service A’s response, complete request X
   Service B -> User: Return response for Request X
   ```

### Implementation Details

1. **Service A API Key Management**
   - Generate secure random API keys
   - Hash API keys before storage (e.g., using bcrypt)
   - Store metadata (Service B ID, scope, rate limits, expiry)
   - Provide API key validation endpoint
   - Support API key revocation and rotation

2. **Service B Implementation**
   - Accept user requests with JWT or other credentials
   - Validate user authorization (e.g., verify JWT)
   - Retrieve API key from secure storage (e.g., AWS Secrets Manager, HashiCorp Vault)
   - Include API key in `x-api-key` header for Service A requests
   - Handle 200 and 403 responses, with retry logic for key rotation

### Use Cases
- Smaller ecosystems
- Services with specific authorization requirements
- When services need direct control over API keys
- Varying API key policies per service

## Pattern 2: Centralized API Key Management

In this pattern, a dedicated service manages API keys for authorization across the ecosystem, similar to the login service for authentication.

### Components

1. **Login Service**
   - Manages user credentials - Authentication
   - Issues JWT tokens - Authorization for users
   - Does not manage API keys

2. **API Key Management Service**
   - Centralized API key issuance - Authorization
   - API key validation - Authorization
   - Manages API key lifecycle, usage monitoring, and auditing

3. **Service A (API Key Handler)**
   - Handles user login requests
   - Forwards authentication to Login Service
   - Requests API key issuance from API Key Management Service
   - Validates API keys via API Key Management Service
   - Does not store API keys locally

4. **Service B (API Key User)**
   - Distinct service using Service A as a downstream dependency
   - Retrieves stored API keys from environment variables or secure vault
   - Includes API keys in `x-api-key` header for authorization when calling Service A
   - Processes user requests and integrates Service A responses

### Authentication and Authorization Flow

1. **User Authentication**
   ```
   User -> Service A: Login with username/password (Authentication)
   Service A -> Login Service: Forward credentials
   Login Service -> Service A: Return JWT with user claims (Authorization)
   Service A -> User: Return JWT
   ```

2. **API Key Provisioning (Authorization for Service B)**
   ```
   Admin -> Service A: Request API key for Service B (with JWT)
   Service A: Validate JWT, extract claims (e.g., admin ID, roles)
   Service A -> API Key Management Service: Request API key
   API Key Management Service: Generate API key, store hash with metadata
   API Key Management Service -> Service A: Return API key
   Service A -> Admin: Return API key
   Admin: Store API key in Service B’s environment variables or secure vault
   ```

3. **Service-to-Service Communication (Authorization)**
   ```
   User -> Service B: Request X (e.g., with JWT for user authorization)
   Service B: Validate JWT to authorize user request
   Service B: Retrieve Service A’s API key from secure vault or environment
   Service B -> Service A: Request Y with API key in x-api-key header for authorization
   Service A -> API Key Management Service: Check API key for authorization
   API Key Management Service -> Service A: Return authorization result
   Service A -> Service B: Return 200 for request Y if authorized, 403 if unauthorized
   Service B: Process Service A’s response, complete request X
   Service B -> User: Return response for Request X
   ```

### Implementation Details

1. **API Key Management Service**
   - Secure API key generation
   - Store hashed API keys with metadata (scope, rate limits, expiry)
   - Provide validation endpoints
   - Implement usage tracking, audit logging, and key rotation
   - Cache validation results briefly to reduce latency

2. **Service A Implementation**
   - Validate JWTs for user requests
   - Handle API key provisioning requests
   - Integrate with API Key Management Service for key validation

3. **Service B Implementation**
   - Accept user requests with JWT or other credentials
   - Validate user authorization (e.g., verify JWT)
   - Retrieve API key from secure storage (e.g., AWS Secrets Manager)
   - Include API key in `x-api-key` header for Service A requests
   - Handle 200 and 403 responses, with retry logic for key rotation

### Use Cases
- Large ecosystems
- Consistent API key policies
- Centralized monitoring and auditing
- Complex API key lifecycle management
- Cross-service API key usage

## Security Considerations

### For Both Patterns

1. **API Key Security**
   - Use secure random generation for API keys
   - Hash keys before storage
   - Store keys in secure vaults (e.g., AWS Secrets Manager, HashiCorp Vault) or encrypted environment variables
   - Implement rate limiting per key
   - Set appropriate expiry times and rotate keys periodically

2. **Transport Security**
   - Always use HTTPS for all communications
   - Validate TLS certificates
   - Use secure headers (e.g., `x-api-key` for authorization)
   - Implement CORS policies

3. **Error Handling**
   - Return 403 Forbidden for authorization failures, 401 Unauthorized for authentication failures
   - Avoid exposing sensitive details in errors
   - Log security events for auditing
   - Implement retry logic for key rotation or expiration

### Pattern-Specific Considerations

1. **Service-Managed API Keys**
   - Each service must implement secure key storage
   - Manage authorization policies per service
   - More complex to audit across services
   - Easier to implement service-specific requirements

2. **Centralized API Key Management**
   - Single point of failure; ensure high availability
   - More complex to implement
   - Easier to audit and enforce consistent policies
   - Cache validation results to reduce latency

## Choosing a Pattern

Consider these factors when choosing a pattern:

1. **Ecosystem Size**
   - Small: Service-Managed
   - Large: Centralized

2. **Operational Complexity**
   - Simple: Service-Managed
   - Complex: Centralized

3. **Compliance Requirements**
   - Basic: Service-Managed
   - Strict: Centralized

4. **Development Resources**
   - Limited: Service-Managed
   - Available: Centralized

5. **Future Growth**
   - Stable: Service-Managed
   - Growing: Centralized

## Migration Considerations

When migrating between patterns:

1. **Service-Managed to Centralized**
   - Plan gradual migration
   - Implement API Key Management Service
   - Migrate services one at a time
   - Support dual validation for existing keys
   - Update documentation

2. **Centralized to Service-Managed**
   - Plan service-specific key management
   - Migrate key storage to individual services
   - Update authorization policies
   - Maintain backward compatibility
   - Update documentation
