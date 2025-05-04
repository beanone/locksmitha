# Role-Based Access Control (RBAC) Architecture for Locksmitha

This document outlines architectural options and best practices for implementing role-based access control (RBAC) in the Locksmitha authentication ecosystem and its integrated services.

---

## 1. Where Should RBAC Live?

### A. Centralized in the Login/Authentication Service (Recommended)
- **How:**
  - Store user roles and permissions in the same user database as the login service.
  - Add role/permission fields to your user model (e.g., `roles: List[str]` or `is_admin: bool`).
  - Expose roles in the JWT claims when issuing tokens.
  - Downstream services (like `graph_reader_api`) check the JWT for roles/permissions and enforce access control locally.
- **Pros:**
  - Single source of truth for user identity and roles.
  - Simpler user management and auditing.
  - JWTs are self-contained: no extra DB lookups needed for most requests.
- **Cons:**
  - If you need to revoke roles immediately, you may need short-lived tokens or a token blacklist.

#### Example: User Model and JWT Claim
```python
# In your login service's user model
class User(Base):
    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    roles = Column(ARRAY(String), default=list)  # e.g., ["admin", "editor"]
    # ... other fields ...

# When issuing JWT:
claims = {
    "sub": str(user.id),
    "roles": user.roles,
    # ... other claims ...
}
```

---

### B. Separate Authorization Service (Advanced)
- **How:**
  - Keep authentication (login, JWT issuance) and authorization (role/permission checks) in separate services.
  - The login service issues tokens with minimal claims (e.g., user ID).
  - Downstream services call the authorization service to check permissions/roles for each request or on demand.
- **Pros:**
  - Maximum flexibility for complex, multi-tenant, or multi-app environments.
  - Can support dynamic, context-aware permissions.
- **Cons:**
  - More moving parts, more network calls, higher latency.
  - Harder to manage and debug for small/medium teams.

#### Example: Authorization Service API
```http
POST /authz/check
{
  "user_id": "...",
  "action": "read_entity",
  "resource": "entity:123"
}
# Response:
{
  "allowed": true
}
```

---

## 2. User Database, Roles, and Profiles

- **User Database:**
  - Store users, hashed passwords, and profile info in a single database (e.g., Postgres).
  - Add a `roles` field (array or join table) to the user model.
  - Optionally, add a `profile` table for extended user info.

- **Role Management:**
  - Roles can be simple (e.g., `is_admin: bool`) or flexible (e.g., `roles: List[str]`).
  - For more complex needs, use a join table: `user_roles(user_id, role_id)` and a `roles` table.

- **JWT Claims:**
  - When a user logs in, include their roles in the JWT claims:
    ```json
    {
      "sub": "user_id",
      "roles": ["admin", "editor"]
    }
    ```
  - Downstream services check the `roles` claim for access control.

- **Profile Management:**
  - Store profile data in the same DB, either as part of the user table or in a related table.

---

## 3. Best Practice: Centralized RBAC in the Login Service

- **Why?**
  - Simpler for most teams.
  - Fewer network calls.
  - JWTs are portable and self-contained.
  - Easy to extend to OAuth2 scopes/claims if needed.

- **How to Implement:**
  1. Extend your user model in the login service to include roles.
  2. Add role management endpoints (admin-only).
  3. Add roles to JWT claims.
  4. In downstream services, check roles from the JWT in your route dependencies.

#### Example: FastAPI Dependency for Role Check
```python
from fastapi import Depends, HTTPException

def require_role(required_role: str):
    def dependency(user=Depends(get_current_user)):
        if required_role not in user["roles"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency

# Usage in a route:
@app.get("/users/", dependencies=[Depends(require_role("admin"))])
def list_users():
    ...
```

---

## 4. When to Use a Separate Authorization Service?

- You have many microservices and want to centralize all authorization logic.
- You need dynamic, context-aware permissions (e.g., ABAC, PBAC).
- You have multiple user databases or multi-tenant requirements.
- You want to decouple authentication and authorization for organizational reasons.

---

## 4a. RBAC as a Separate Git Project/Service (Composable Deployments)

It is possible to implement RBAC as a standalone service in its own git repository, with its own Docker image and API. This allows you to compose your deployments differently depending on your use case:

- **How it works:**
  - The RBAC service is developed and versioned independently.
  - It exposes an API (e.g., `/authz/check`) for role/permission checks.
  - Other services (login, API, etc.) call this service as needed.
  - You can deploy only the login service (with built-in RBAC) for simple cases, or both login and RBAC services for complex cases.
  - Docker Compose, Kubernetes, or other orchestrators can be used to package and deploy the right combination of services for each environment.

- **Pros:**
  - Maximum flexibility for different environments and use cases.
  - RBAC logic can be reused across multiple projects.
  - Teams can work independently on authentication and authorization.

- **Cons:**
  - Requires clear API contracts and shared models between services.
  - More configuration and operational complexity.
  - Potential for network latency and additional points of failure.

- **When requirements diverge:**
  - For simple use cases, built-in RBAC is easier and faster.
  - For complex, multi-tenant, or dynamic permission scenarios, a separate RBAC service is preferable.

#### Example: Docker Compose Flexibility
```yaml
# docker-compose.yml (simple)
services:
  login:
    build: ./login_service
    # RBAC is built-in

# docker-compose.yml (advanced)
services:
  login:
    build: ./login_service
    environment:
      RBAC_URL: http://rbac:8002
  rbac:
    build: ./rbac_service
    # RBAC is external
```

---

## 5. Summary Table

| Approach         | User DB & Roles | JWT Claims | Downstream Checks | Complexity | Best For                |
|------------------|-----------------|------------|-------------------|------------|-------------------------|
| Centralized RBAC | Login service   | Yes        | Yes               | Low        | Most teams, simplicity  |
| Separate Service | Separate        | Optional   | Via API call      | High       | Large, complex systems  |

---

## 6. References
- [FastAPI Security - Role-based Access](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
- [OWASP: Access Control Design](https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control.html)
- [Auth0: RBAC vs ABAC](https://auth0.com/docs/secure/access-control/rbac/)

---

**Recommendation:**
Start with centralized RBAC in your login service. Only consider a separate authorization service if your system grows in complexity or you have very specific needs.
