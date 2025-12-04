# Tutorial 20: Multi-User MCP with Azure API Management AI Gateway

## Design Document

**Status**: Updated for 2025 Features  
**Date**: December 2025  
**Estimated Duration**: 90 minutes  
**Prerequisites**: Tutorial 19b (Foundry MCP Authentication)

---

## 1. Overview

### What's New in 2025

This design document has been updated to incorporate the latest Azure platform capabilities:

| Feature | Description |
|---------|-------------|
| **Microsoft Foundry Responses API** | New GA API replacing Assistants threads pattern |
| **APIM AI Gateway** | Native GenAI capabilities: semantic caching, token metrics, LLM load balancing |
| **APIM MCP Server Support** | Expose REST APIs as MCP servers, passthrough to existing MCP servers |
| **A2A Agent APIs** | Agent-to-Agent protocol support in APIM (preview) |
| **Azure API Center** | Centralized MCP server registry and discovery portal |

### Building Upon Tutorial 19b

Tutorial 19b introduced Microsoft Foundry's MCP authentication patterns using the Responses API:
- **Unauthenticated** - Public MCP servers (gitmcp.io, Microsoft Learn)
- **Key-based** - API keys via Project Connections
- **Agentic Identity** - Managed Identity for Azure resources
- **OAuth Passthrough** - User delegation for personalized access

**Tutorial 20 extends this foundation** by integrating APIM's **AI Gateway** as the enterprise control plane for:
- Multi-user MCP access with identity propagation
- GenAI-specific policies (token limits, semantic caching)
- Unified governance across MCP servers and AI APIs

### Problem Statement

Enterprise AI agents must respect user identity, roles, and permissions when accessing data and systems. Instead of building custom authentication middleware in each MCP server, we leverage:

1. **Microsoft Foundry** - OAuth Identity Passthrough for user delegation
2. **APIM AI Gateway** - Centralized security, monitoring, and governance
3. **APIM Credential Manager** - Automated OAuth token lifecycle management

This combination provides:
- Authenticate users via Microsoft Entra ID
- Manage OAuth 2.0 connections and token refresh automatically
- Pass user context to MCP servers through APIM policies
- Enforce role-based access control (RBAC) on MCP tools
- Use Row-Level Security (RLS) in Azure SQL Database
- Track token usage per user for cost allocation
- Maintain audit trails for compliance

### Architecture Advantage: APIM AI Gateway

Azure API Management now includes dedicated **AI Gateway capabilities**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        APIM AI Gateway Capabilities                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  Traffic        │  │  Scalability    │  │  Security       │         │
│  │  Mediation      │  │  & Performance  │  │  & Safety       │         │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤         │
│  │ • REST → MCP    │  │ • Token limits  │  │ • OAuth/JWT     │         │
│  │ • MCP passthru  │  │ • Semantic cache│  │ • Content safety│         │
│  │ • A2A agents    │  │ • Load balancer │  │ • IP filtering  │         │
│  │ • LLM endpoints │  │ • PTU priority  │  │ • Rate limiting │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  Resiliency     │  │  Observability  │  │  Developer      │         │
│  │                 │  │  & Governance   │  │  Experience     │         │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤         │
│  │ • Circuit break │  │ • Token metrics │  │ • API Center    │         │
│  │ • Retry-After   │  │ • Prompt logging│  │ • MCP registry  │         │
│  │ • Failover      │  │ • Cost tracking │  │ • Dev portal    │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Benefits Over Custom Middleware

| Aspect | Custom Middleware | APIM AI Gateway |
|--------|-------------------|-----------------|
| **OAuth Handling** | Build JWT validation, refresh, caching | Zero-code via Credential Manager |
| **Token Metrics** | Custom instrumentation | `llm-emit-token-metric` policy |
| **Semantic Caching** | Build with Redis + embeddings | `llm-semantic-cache-*` policies |
| **Rate Limiting** | Per-request code | `llm-token-limit` policy (TPM-based) |
| **MCP Governance** | Build for each server | Centralized policies across all servers |
| **Monitoring** | Custom logging | Built-in Azure Monitor dashboards |

### Learning Objectives

By the end of this tutorial, you will:

1. **Expose REST APIs as MCP Servers** - Use APIM to convert existing APIs to MCP protocol
2. **Configure APIM Credential Manager** - Automate OAuth 2.0 token lifecycle
3. **Implement AI Gateway Policies** - Token limits, semantic caching, user metrics
4. **Connect Foundry Agents to APIM MCP** - Use MCPTool with APIM-managed endpoints
5. **Implement Role-Based MCP Tools** - RBAC using APIM-injected headers
6. **Configure Database RLS** - Row-Level Security in Azure SQL
7. **Register MCP Servers in API Center** - Enterprise discovery and governance

---

## 2. Use Case: Enterprise Travel Management System

### Business Scenario

A company needs an AI-powered travel assistant where different employees have different access levels:

**User Roles:**

1. **Employee** (`employee`)
   - Search flights and hotels
   - Submit travel requests for approval
   - View own bookings
   - Cancel own pending requests

2. **Manager** (`manager`)
   - All employee capabilities
   - Approve/reject team member travel requests
   - View team bookings and budgets
   - Reallocate team travel budget

3. **Travel Administrator** (`admin`)
   - All manager capabilities
   - View all company bookings
   - Modify travel policies
   - Override approvals
   - Access system configuration

4. **Finance Analyst** (`finance`)
   - View all bookings (read-only)
   - Generate cost reports by department
   - Export financial data
   - View budget utilization

### Data Access Patterns

| Role | Own Bookings | Team Bookings | All Bookings | Financial Reports |
|------|-------------|---------------|--------------|-------------------|
| Employee | Read/Write | ❌ | ❌ | ❌ |
| Manager | Read/Write | Read/Approve | ❌ | Team Only |
| Admin | Read/Write | Read/Write | Read/Write | ✅ Full Access |
| Finance | Read-Only | Read-Only | Read-Only | ✅ Full Access |

---

## 3. Architecture Design

### High-Level Flow: Foundry + APIM AI Gateway + MCP

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. User authenticates with Microsoft Entra ID                        │
│    - AI agent/app gets user JWT token with claims (oid, email, roles)│
│    - Token audience: Microsoft Foundry                                │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 2. User interacts with Microsoft Foundry Agent (Responses API)        │
│    - Agent configured with MCPTool pointing to APIM                  │
│    - Uses OAuth Identity Passthrough authentication                  │
│    - responses.create() with previous_response_id for conversations  │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 3. Foundry Agent → APIM AI Gateway (MCP Server endpoint)             │
│    - Authorization: Bearer <user_jwt_token>                          │
│    - APIM validates token, extracts user claims                      │
│    - MCP protocol: Streamable HTTP or SSE transport                  │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 4. APIM AI Gateway Policies (Inbound)                                │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │ <validate-jwt> - Verify Entra ID token                    │     │
│    │ <get-authorization-context> - Get managed OAuth token     │     │
│    │ <llm-token-limit> - Enforce TPM limits per user           │     │
│    │ <llm-semantic-cache-lookup> - Check cached responses      │     │
│    │ <set-header> - Inject X-User-Id, X-User-Email, X-User-Roles│    │
│    └──────────────────────────────────────────────────────────┘     │
│                                                                       │
│    MCP Server Options in APIM:                                        │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │ Option A: REST API exposed as MCP Server                  │     │
│    │   - API operations become MCP tools automatically         │     │
│    │   - No code changes to existing REST APIs                 │     │
│    │                                                           │     │
│    │ Option B: Passthrough to existing MCP Server              │     │
│    │   - FastMCP on ACA, Azure Functions, Logic Apps           │     │
│    │   - APIM adds governance layer                            │     │
│    └──────────────────────────────────────────────────────────┘     │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 5. MCP Server Backend (FastMCP on Azure Container Apps)              │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │ MCP Server receives requests with APIM-injected context: │     │
│    │   - X-User-Id header → user's Entra ID object_id         │     │
│    │   - X-User-Email header → for display/logging            │     │
│    │   - X-User-Roles header → comma-separated roles          │     │
│    │   - Authorization header → APIM-managed OAuth token      │     │
│    │                                                           │     │
│    │ MCP Tool Implementation:                                  │     │
│    │   1. Extract user context from headers (no JWT parsing!) │     │
│    │   2. Check tool permission matrix (RBAC decorator)       │     │
│    │   3. Execute tool with user context                      │     │
│    │   4. Database queries filtered by SESSION_CONTEXT + RLS  │     │
│    └──────────────────────────────────────────────────────────┘     │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 6. Azure SQL Database with Entra ID Authentication + RLS             │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │ Connection: Managed Identity or OBO token                 │     │
│    │ SESSION_CONTEXT: sp_set_session_context 'user_id', ...   │     │
│    │                                                           │     │
│    │ Row-Level Security automatically filters:                 │     │
│    │   - Employee: See only own bookings                       │     │
│    │   - Manager: See team bookings                            │     │
│    │   - Admin/Finance: See all bookings                       │     │
│    └──────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 7. Azure API Center - MCP Server Registry                            │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │ - Centralized catalog of all MCP servers                  │     │
│    │ - Discovery portal for developers                         │     │
│    │ - Sync from APIM automatically                            │     │
│    │ - Live demo: https://mcp.azure.com                        │     │
│    └──────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Details

#### A. APIM AI Gateway Policy Configuration

**1. Inbound Policy: Authentication + AI Gateway Features**

```xml
<inbound>
    <!-- 1. Validate JWT from Entra ID -->
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
        <openid-config url="https://login.microsoftonline.com/{tenant}/.well-known/openid-configuration"/>
        <audiences>
            <audience>api://travel-mcp-server</audience>
        </audiences>
        <issuers>
            <issuer>https://sts.windows.net/{tenant}/</issuer>
        </issuers>
        <required-claims>
            <claim name="oid" match="any"/>
        </required-claims>
    </validate-jwt>
    
    <!-- 2. Extract user claims into variables -->
    <set-variable name="user-id" value="@(context.Request.Headers.GetValueOrDefault("Authorization","").AsJwt()?.Claims["oid"]?.FirstOrDefault() ?? "anonymous")" />
    <set-variable name="user-email" value="@(context.Request.Headers.GetValueOrDefault("Authorization","").AsJwt()?.Claims["email"]?.FirstOrDefault() ?? "")" />
    <set-variable name="user-roles" value="@(String.Join(",", context.Request.Headers.GetValueOrDefault("Authorization","").AsJwt()?.Claims["roles"] ?? new string[]{}))" />
    
    <!-- 3. AI Gateway: Token rate limiting per user (TPM-based) -->
    <llm-token-limit 
        counter-key="@((string)context.Variables["user-id"])" 
        tokens-per-minute="10000" 
        estimate-prompt-tokens="true"
        remaining-tokens-variable-name="remainingTokens">
    </llm-token-limit>
    
    <!-- 4. AI Gateway: Semantic cache lookup -->
    <llm-semantic-cache-lookup 
        score-threshold="0.9"
        embeddings-backend-id="embeddings-backend"
        embeddings-backend-auth="system-assigned">
        <vary-by>@((string)context.Variables["user-id"])</vary-by>
    </llm-semantic-cache-lookup>
    
    <!-- 5. Get managed OAuth token (for OBO to backend services) -->
    <get-authorization-context 
        provider-id="entra-id-provider" 
        authorization-id="@((string)context.Variables["user-id"])"
        context-variable-name="auth-context" 
        identity-type="managed"
        ignore-error="true">
    </get-authorization-context>
    
    <!-- 6. Inject user context headers for MCP server -->
    <set-header name="X-User-Id" exists-action="override">
        <value>@((string)context.Variables["user-id"])</value>
    </set-header>
    <set-header name="X-User-Email" exists-action="override">
        <value>@((string)context.Variables["user-email"])</value>
    </set-header>
    <set-header name="X-User-Roles" exists-action="override">
        <value>@((string)context.Variables["user-roles"])</value>
    </set-header>
    
    <!-- 7. Emit token metrics for cost tracking -->
    <llm-emit-token-metric namespace="travel-mcp">
        <dimension name="User" value="@((string)context.Variables["user-email"])" />
        <dimension name="Tool" value="@(context.Request.Url.Path)" />
        <dimension name="Department" value="@(context.Request.Headers.GetValueOrDefault("X-Department", "unknown"))" />
    </llm-emit-token-metric>
</inbound>

<outbound>
    <!-- Store response in semantic cache -->
    <llm-semantic-cache-store duration="3600" />
</outbound>
```

**2. MCP Session Rate Limiting (for tool calls)**

```xml
<!-- Rate limit MCP tool calls by session -->
<set-variable name="body" value="@(context.Request.Body.As<string>(preserveContent: true))" />
<choose>
    <when condition="@(
        Newtonsoft.Json.Linq.JObject.Parse((string)context.Variables["body"])["method"] != null 
        && Newtonsoft.Json.Linq.JObject.Parse((string)context.Variables["body"])["method"].ToString() == "tools/call"
    )">
        <rate-limit-by-key 
            calls="100" 
            renewal-period="60" 
            counter-key="@(context.Request.Headers.GetValueOrDefault("Mcp-Session-Id", "unknown"))" />
    </when>
</choose>
```

#### B. Exposing REST API as MCP Server in APIM

APIM can now **automatically convert REST APIs to MCP servers**:

1. **In Azure Portal**: APIs → MCP Servers → Create MCP Server
2. **Select**: "Expose an API as an MCP server"
3. **Choose API**: Select your REST API (e.g., Travel Booking API)
4. **Select Operations**: Choose which operations become MCP tools

**Benefits**:
- No code changes to existing REST APIs
- API operations automatically become MCP tools
- OpenAPI descriptions become tool descriptions
- APIM policies apply to all tool calls

**MCP Server URL**: `https://{apim-name}.azure-api.net/{api-name}-mcp/mcp`

#### C. Passthrough to Existing MCP Server

For custom FastMCP servers:

1. **In Azure Portal**: APIs → MCP Servers → Create MCP Server
2. **Select**: "Expose an existing MCP server"
3. **Backend URL**: `https://travel-mcp-server.azurecontainerapps.io/mcp`
4. **Transport**: Streamable HTTP (recommended) or SSE

**APIM adds**:
- Authentication at the gateway
- Rate limiting per user/session
- Token metrics and logging
- Semantic caching (where applicable)

#### D. Simplified FastMCP Server (No Auth Middleware Needed!)

The MCP server becomes much simpler since APIM handles all OAuth complexity:

**1. Extract User Context from APIM-Injected Headers**

```python
from fastapi import Request, HTTPException

def get_user_context(request: Request) -> dict:
    """Extract user context from APIM-injected headers.
    
    APIM validates JWT and extracts claims, so MCP server 
    doesn't need any JWT parsing or validation logic!
    """
    user_id = request.headers.get("X-User-Id")
    user_email = request.headers.get("X-User-Email")
    user_roles = request.headers.get("X-User-Roles", "").split(",")
    
    if not user_id or user_id == "anonymous":
        raise HTTPException(status_code=401, detail="Unauthorized: Missing user context")
    
    return {
        "user_id": user_id,
        "email": user_email,
        "roles": [r.strip() for r in user_roles if r.strip()]
    }
```

**2. Role-Based Tool Decorator**

```python
from functools import wraps

def require_role(*allowed_roles):
    """Decorator to enforce role-based access on MCP tools"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_ctx = get_user_context(request)
            
            # Check if user has required role
            if not any(role in user_ctx["roles"] for role in allowed_roles):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Forbidden: Requires one of {allowed_roles}"
                )
            
            # Add user context to function kwargs
            return await func(request, user_ctx=user_ctx, *args, **kwargs)
        return wrapper
    return decorator
```

**3. MCP Tool with RBAC**

```python
@mcp.tool()
@require_role("manager", "admin")
async def approve_travel_request(request: Request, booking_id: int) -> Dict[str, Any]:
    """Approve a team member's travel request (managers and admins only)"""
    user_ctx = get_user_context(request)
    
    # Database query with user context
    async with get_db_connection(user_ctx) as conn:
        # Set SESSION_CONTEXT for RLS
        await conn.execute(f"EXEC sp_set_session_context 'user_id', '{user_ctx['user_id']}'")
        
        # Update booking (RLS ensures manager can only approve their team's requests)
        result = await conn.execute(
            "UPDATE TravelBookings SET status='approved', approved_by=@user_id WHERE booking_id=@id",
            {"user_id": user_ctx["user_id"], "id": booking_id}
        )
        
        if result.rowcount == 0:
            return {"error": "Booking not found or access denied"}
        
        return {"success": True, "booking_id": booking_id, "approved_by": user_ctx["email"]}
```

#### B. Database Schema

**Users Table:**
```sql
CREATE TABLE Users (
    user_id NVARCHAR(100) PRIMARY KEY,  -- Azure AD object_id
    email NVARCHAR(255) NOT NULL UNIQUE,
    display_name NVARCHAR(255),
    role NVARCHAR(50) NOT NULL CHECK (role IN ('employee', 'manager', 'admin', 'finance')),
    department NVARCHAR(100),
    manager_id NVARCHAR(100) FOREIGN KEY REFERENCES Users(user_id),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

**TravelBookings Table:**
```sql
CREATE TABLE TravelBookings (
    booking_id INT PRIMARY KEY IDENTITY,
    user_id NVARCHAR(100) NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    manager_id NVARCHAR(100) FOREIGN KEY REFERENCES Users(user_id),
    
    -- Booking details
    origin NVARCHAR(100),
    destination NVARCHAR(100),
    departure_date DATE,
    return_date DATE,
    
    -- Financial
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    currency NVARCHAR(3) DEFAULT 'USD',
    
    -- Workflow
    status NVARCHAR(50) CHECK (status IN ('pending', 'approved', 'rejected', 'completed', 'cancelled')),
    submitted_at DATETIME2 DEFAULT GETDATE(),
    approved_at DATETIME2,
    approved_by NVARCHAR(100) FOREIGN KEY REFERENCES Users(user_id),
    
    -- Audit
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

**Row-Level Security:**
```sql
-- Security function
CREATE FUNCTION dbo.fn_TravelBookingSecurity(@user_id NVARCHAR(100), @user_role NVARCHAR(50))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
    SELECT 1 AS result
    WHERE 
        @user_role IN ('admin', 'finance')  -- Admin/Finance see all
        OR user_id = @user_id                -- Users see own bookings
        OR manager_id = @user_id;            -- Managers see team bookings

-- Security policy
CREATE SECURITY POLICY TravelBookingSecurityPolicy
    ADD FILTER PREDICATE dbo.fn_TravelBookingSecurity(user_id, SESSION_CONTEXT(N'user_role'))
    ON dbo.TravelBookings
WITH (STATE = ON);
```

#### C. MCP Tools with RBAC

**Tool Permission Matrix:**

| Tool | Employee | Manager | Admin | Finance |
|------|----------|---------|-------|---------|
| `search_flights` | ✅ | ✅ | ✅ | ✅ |
| `search_hotels` | ✅ | ✅ | ✅ | ✅ |
| `submit_travel_request` | ✅ | ✅ | ✅ | ❌ |
| `view_my_bookings` | ✅ | ✅ | ✅ | ❌ |
| `cancel_my_booking` | ✅ | ✅ | ✅ | ❌ |
| `view_team_bookings` | ❌ | ✅ | ✅ | ✅ |
| `approve_travel_request` | ❌ | ✅ | ✅ | ❌ |
| `view_all_bookings` | ❌ | ❌ | ✅ | ✅ |
| `generate_cost_report` | ❌ | ✅ (team) | ✅ | ✅ |
| `modify_travel_policy` | ❌ | ❌ | ✅ | ❌ |

---

## 4. OAuth On-Behalf-Of Flow Details

### Token Exchange Process

```
┌──────────────────────────────────────────────────────────────────┐
│ Step 1: User Authentication                                       │
│ User → Azure AD: Login with credentials                          │
│ Azure AD → User: JWT access token (audience: AI Foundry)        │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 2: Agent Request                                             │
│ User → Agent: "Show my travel bookings"                          │
│ Agent attaches user token to HostedMCPTool request               │
│ Request Header: Authorization: Bearer <user_jwt_token>           │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 3: MCP Server Token Exchange (OBO)                          │
│                                                                   │
│ POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token│
│ Body:                                                             │
│   grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer        │
│   client_id={mcp_server_client_id}                              │
│   client_secret={mcp_server_secret}                             │
│   assertion={user_jwt_token}                                     │
│   requested_token_use=on_behalf_of                               │
│   scope=https://database.windows.net/.default                    │
│                                                                   │
│ Response:                                                         │
│   {                                                               │
│     "access_token": "<obo_token_for_sql>",                       │
│     "token_type": "Bearer",                                       │
│     "expires_in": 3600                                            │
│   }                                                               │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 4: Database Access with OBO Token                           │
│ MCP Server → Azure SQL: Connect with OBO token                   │
│ Connection String:                                                │
│   Server=tcp:{server}.database.windows.net,1433;                │
│   Database={db};                                                  │
│   Authentication=Active Directory Access Token;                  │
│   AccessToken={obo_token};                                       │
│                                                                   │
│ SET CONTEXT_INFO:                                                 │
│   EXEC sp_set_session_context 'user_id', @user_id;              │
│   EXEC sp_set_session_context 'user_role', @user_role;          │
│                                                                   │
│ Query executes with RLS automatically enforced                   │
└──────────────────────────────────────────────────────────────────┘
```

### Required Azure AD App Registrations

**1. AI Agent Application**
- **App Name**: `travel-assistant-agent`
- **Redirect URIs**: Microsoft Foundry endpoints
- **API Permissions**: 
  - User.Read (Microsoft Graph)
  - Access to MCP Server API
- **Token Claims**: email, roles, oid

**2. MCP Server Application**
- **App Name**: `travel-mcp-server`
- **Expose an API**: `api://travel-mcp-server`
- **API Permissions**:
  - SQL Database (https://database.windows.net/.default)
  - Microsoft Graph (optional for profile lookups)
- **Client Secret**: For OBO token exchange
- **Pre-authorized applications**: AI Agent app

**3. Database Access**
- Azure SQL configured with Azure AD authentication
- MCP Server service principal added as database user
- Users added as database users (automatic via Azure AD)

---

## 5. Implementation Plan

### Part 1: APIM AI Gateway Setup (20 min)
- Create APIM instance with AI Gateway features enabled
- Configure OAuth credential provider (Entra ID)
- Set up managed identity for backend services
- Enable Application Insights for monitoring

### Part 2: Expose Travel API as MCP Server (15 min)
- Import existing Travel REST API to APIM
- Create MCP Server from REST API
- Select operations to expose as MCP tools
- Configure MCP server policies (rate limiting, auth)

### Part 3: AI Gateway Policy Configuration (20 min)
- Implement JWT validation policy
- Configure `llm-token-limit` for TPM-based rate limiting
- Add `llm-semantic-cache-*` policies for caching
- Configure `llm-emit-token-metric` for cost tracking
- Add user context header injection

### Part 4: Database Setup with RLS (15 min)
- Create Azure SQL Database with Entra ID auth
- Create database schema (Users, TravelBookings)
- Implement Row-Level Security policies
- Seed sample data (users with different roles)

### Part 5: Connect Foundry Agent to APIM MCP (15 min)
- Configure MCPTool with APIM MCP endpoint
- Set up OAuth Identity Passthrough in Foundry
- Test tool discovery and invocation
- Verify user context propagation

### Part 6: Register in API Center (10 min)
- Create Azure API Center instance
- Sync MCP servers from APIM
- Configure API Center portal for discovery
- Test MCP server discovery workflow

---

## 6. Security Considerations

### Authentication Security
- JWT signature validation using Azure AD public keys
- Token expiration checks
- Replay attack prevention
- Secure token storage (in-memory cache only)

### Authorization Security
- Principle of least privilege
- Role validation on every request
- Database-level security (RLS) as defense-in-depth
- Audit logging for sensitive operations

### Database Security
- Azure AD authentication (no SQL passwords)
- Row-Level Security enforced at database layer
- Encrypted connections (TLS)
- Column-level encryption for sensitive data

### Network Security
- Container Apps with VNET integration
- Private endpoint for SQL Database
- API Management for additional security layer
- Rate limiting and throttling

---

## 7. Testing Scenarios

### Scenario 1: Employee Access
```
User: alice@contoso.com (role: employee)
Action: "Show my travel bookings"
Expected: See only Alice's bookings
Expected: Cannot see Bob's bookings
Expected: Cannot approve requests
```

### Scenario 2: Manager Access
```
User: bob@contoso.com (role: manager, manages Alice)
Action: "Show team travel requests pending my approval"
Expected: See Alice's pending requests
Expected: Can approve/reject Alice's requests
Expected: Cannot see other team's bookings
```

### Scenario 3: Finance Analyst Access
```
User: charlie@contoso.com (role: finance)
Action: "Generate cost report for Q4 2024"
Expected: See all bookings (read-only)
Expected: Generate financial reports
Expected: Cannot modify bookings
Expected: Cannot approve requests
```

### Scenario 4: Unauthorized Access Attempt
```
User: alice@contoso.com (role: employee)
Action: "Approve Bob's travel request"
Expected: 403 Forbidden error
Expected: Error message: "Insufficient permissions for tool 'approve_travel_request'"
```

---

## 8. Tutorial Structure

### Tutorial 20 Outline (Building on Tutorial 19b)

**Part 1: Introduction to APIM AI Gateway**
- What's new in APIM for AI workloads
- GenAI-specific policies overview
- MCP server support in APIM
- Architecture: Foundry + APIM + MCP

**Part 2: Exposing REST API as MCP Server**
- Import REST API to APIM
- Create MCP Server from API operations
- Configure tool descriptions from OpenAPI
- Test with MCP Inspector

**Part 3: AI Gateway Policies**
- Token rate limiting (`llm-token-limit`)
- Semantic caching (`llm-semantic-cache-*`)
- Token metrics (`llm-emit-token-metric`)
- User context injection (`set-header`)

**Part 4: Authentication & Authorization**
- JWT validation with Entra ID
- Credential Manager for OAuth tokens
- User identity propagation to backends
- Per-user rate limiting

**Part 5: Database Design with RLS**
- Create Azure SQL schema with user roles
- Implement Row-Level Security policies
- Configure SESSION_CONTEXT for filtering
- Test RLS with different users

**Part 6: Connecting Foundry Agents**
- Configure MCPTool with APIM endpoint
- OAuth Identity Passthrough setup
- Responses API conversation pattern
- Multi-user session management

**Part 7: API Center Integration**
- Register MCP servers in API Center
- Configure discovery portal
- Sync from APIM automatically
- Developer self-service workflow

**Part 8: Production Best Practices**
- Monitoring with Azure Monitor dashboards
- Cost allocation by user/department
- Compliance and audit requirements
- Scaling and performance tuning

---

## 9. Key Takeaways

After completing Tutorial 20, learners will understand:

1. **APIM AI Gateway**: Leverage purpose-built GenAI capabilities for token limits, semantic caching, and metrics
2. **REST to MCP Conversion**: Expose existing REST APIs as MCP servers without code changes
3. **MCP Passthrough**: Govern custom MCP servers (FastMCP, LangChain) through APIM
4. **User Identity Propagation**: Pass user context from Foundry through APIM to backends
5. **Responses API Integration**: Use Foundry's new GA API with APIM-managed MCP tools
6. **Database-Level Security**: Implement Row-Level Security (RLS) for defense-in-depth
7. **API Center Discovery**: Register and discover MCP servers in enterprise catalog

### Why This Approach Matters

**Compared to Custom Middleware**:

| Aspect | Custom Build | APIM AI Gateway |
|--------|--------------|-----------------|
| Token rate limiting | Custom counters + Redis | `llm-token-limit` policy |
| Semantic caching | Build embeddings pipeline | `llm-semantic-cache-*` policies |
| Token metrics | Custom instrumentation | `llm-emit-token-metric` + dashboards |
| MCP server exposure | Build MCP protocol support | REST API → MCP in portal |
| OAuth management | JWT validation, refresh, caching | Credential Manager |
| MCP discovery | Build custom registry | Azure API Center |

**Production Benefits**:
- Zero-code MCP server creation from REST APIs
- AI-specific policies for token management
- Built-in monitoring dashboards for GenAI workloads
- Centralized governance across all MCP servers
- Developer self-service through API Center portal

### Integration with Microsoft Foundry

Tutorial 20 demonstrates the complete enterprise pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enterprise AI Agent Stack                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │ Azure AI      │    │ APIM AI       │    │ MCP Servers   │   │
│  │ Foundry       │───▶│ Gateway       │───▶│ (ACA/Funcs)   │   │
│  │               │    │               │    │               │   │
│  │ • Agents      │    │ • Auth/AuthZ  │    │ • FastMCP     │   │
│  │ • MCPTool     │    │ • Token mgmt  │    │ • LangChain   │   │
│  │ • Responses   │    │ • Caching     │    │ • Logic Apps  │   │
│  │   API         │    │ • Monitoring  │    │               │   │
│  └───────────────┘    └───────────────┘    └───────────────┘   │
│                              │                                   │
│                              ▼                                   │
│                    ┌───────────────┐                            │
│                    │ Azure API     │                            │
│                    │ Center        │                            │
│                    │               │                            │
│                    │ • MCP Registry│                            │
│                    │ • Discovery   │                            │
│                    │ • Governance  │                            │
│                    └───────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

This architecture demonstrates how **Azure API Management** transforms from a simple gateway into a complete **AI-aware enterprise platform** for managing MCP servers, LLM APIs, and agent-to-agent communication.

---

## 10. Next Steps

After Tutorial 20, learners can explore:
- **Tutorial 21**: A2A (Agent-to-Agent) APIs with APIM - multi-agent orchestration
- **Tutorial 22**: Multi-tenant SaaS patterns with API Center
- **Tutorial 23**: Advanced compliance (GDPR, data residency, content safety)
- **Tutorial 24**: Performance at scale (PTU priority, regional load balancing)

---

## 11. Reference Links

### Azure API Management AI Gateway
- [AI Gateway Capabilities Overview](https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities)
- [MCP Server Overview](https://learn.microsoft.com/en-us/azure/api-management/mcp-server-overview)
- [Expose REST API as MCP Server](https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server)
- [Expose Existing MCP Server](https://learn.microsoft.com/en-us/azure/api-management/expose-existing-mcp-server)
- [Secure MCP Servers](https://learn.microsoft.com/en-us/azure/api-management/secure-mcp-servers)

### GenAI Policies
- [llm-token-limit Policy](https://learn.microsoft.com/en-us/azure/api-management/llm-token-limit-policy)
- [llm-semantic-cache Policies](https://learn.microsoft.com/en-us/azure/api-management/llm-semantic-cache-lookup-policy)
- [llm-emit-token-metric Policy](https://learn.microsoft.com/en-us/azure/api-management/llm-emit-token-metric-policy)
- [llm-content-safety Policy](https://learn.microsoft.com/en-us/azure/api-management/llm-content-safety-policy)

### Microsoft Foundry
- [Responses API](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/responses)
- [MCP Tools in Foundry](https://learn.microsoft.com/en-us/training/modules/connect-agent-to-mcp-tools/)

### Azure API Center
- [Register MCP Servers](https://learn.microsoft.com/en-us/azure/api-center/register-discover-mcp-server)
- [API Center Portal](https://learn.microsoft.com/en-us/azure/api-center/set-up-api-center-portal)
- [Live MCP Registry Demo](https://mcp.azure.com)

### Labs and Samples
- [AI Gateway Labs](https://github.com/Azure-Samples/ai-gateway)
- [AI Gateway Workshop](https://aka.ms/ai-gateway/workshop)
- [MCP Client Authorization Lab](https://github.com/Azure-Samples/AI-Gateway/tree/main/labs/mcp-client-authorization)
- [Secure Remote MCP Servers Sample](https://github.com/Azure-Samples/remote-mcp-apim-functions-python)

---

## Summary

Tutorial 20 extends Tutorial 19b by integrating **Azure API Management's AI Gateway** as the enterprise control plane for MCP servers and AI agents. Key updates for 2025:

1. **APIM AI Gateway Features**: Purpose-built GenAI policies for token limits, semantic caching, and metrics
2. **Native MCP Support**: Expose REST APIs as MCP servers directly in APIM, or passthrough to existing MCP servers
3. **Responses API Integration**: Use Foundry's new GA API (`responses.create()`) with APIM-managed MCP tools
4. **Azure API Center**: Centralized MCP server registry and discovery portal
5. **A2A Agent APIs**: Support for agent-to-agent communication (preview)

The MCP server implementation is simplified - APIM handles authentication, rate limiting, and caching, while injecting user context headers (`X-User-Id`, `X-User-Email`, `X-User-Roles`). Database security is enforced through **Row-Level Security (RLS)** in Azure SQL.

This architecture demonstrates the complete **enterprise AI agent stack**: Microsoft Foundry for agent orchestration, APIM AI Gateway for governance, and API Center for discovery.

---

**Document Status**: Updated for December 2025 Features  
**Next Action**: Review design, implement tutorial notebook
