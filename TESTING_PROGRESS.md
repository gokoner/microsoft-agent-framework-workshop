# Tutorials 16-19 Testing Progress

**Date Started:** October 13, 2025  
**Purpose:** Validate infrastructure setup for Tutorial 20 (Multi-User MCP with APIM OAuth)

---

## Testing Checklist

### Tutorial 16: Deploy FastMCP to Azure Container Apps

**Status:** 🔄 Not Started

**Objectives:**
- [ ] Build Docker image for travel_mcp_server.py
- [ ] Create Azure Container Registry (ACR)
- [ ] Push image to ACR
- [ ] Create Azure Container App
- [ ] Deploy MCP server
- [ ] Test with HostedMCPTool from Azure AI Foundry agent
- [ ] Verify Part 7 (Azure AI Foundry integration) works

**Azure Resources Created:**
- Resource Group: `_____________________`
- ACR Name: `_____________________`
- Container App: `_____________________`
- MCP Server URL: `_____________________`

**Notes:**
```
[Add any issues, configurations, or important observations here]
```

---

### Tutorial 17: Logic Apps MCP Server

**Status:** 🔄 Not Started

**Objectives:**
- [ ] Create Logic App workflow
- [ ] Configure connectors (Office 365, SharePoint, etc.)
- [ ] Expose Logic App as MCP server
- [ ] Register in Azure API Center
- [ ] Test MCP tools from Logic Apps

**Azure Resources Created:**
- Resource Group: `_____________________`
- Logic App Name: `_____________________`
- API Center: `_____________________`
- MCP Server Endpoint: `_____________________`

**Notes:**
```
[Add any issues, configurations, or important observations here]
```

---

### Tutorial 18: API Management Integration

**Status:** 🔄 Not Started

**Objectives:**
- [ ] Create Azure API Management instance
- [ ] Import MCP server API
- [ ] Configure inbound policies (rate limiting)
- [ ] Set up backend load balancer
- [ ] Configure circuit breaker
- [ ] Add token metrics and logging
- [ ] Test gateway with monitoring

**Azure Resources Created:**
- Resource Group: `_____________________`
- APIM Instance Name: `_____________________`
- APIM Gateway URL: `_____________________`
- Subscription Key: `_____________________`

**Policies Configured:**
- [ ] Rate limiting (per subscription)
- [ ] Backend load balancer
- [ ] Circuit breaker
- [ ] Token metrics
- [ ] Request/response logging

**Notes:**
```
[Add any issues, configurations, or important observations here]
```

---

### Tutorial 19: Orchestrating Agent with MCP

**Status:** 🔄 Not Started

**Objectives:**
- [ ] Create orchestrating agent
- [ ] Configure multiple MCP server connections
- [ ] Test multi-tool workflows through APIM
- [ ] Verify end-to-end integration
- [ ] Check monitoring and analytics

**Test Scenarios:**
- [ ] Simple single-tool request
- [ ] Complex multi-tool workflow
- [ ] Error handling and fallback
- [ ] Performance monitoring

**Notes:**
```
[Add any issues, configurations, or important observations here]
```

---

## Azure Infrastructure Summary

### For Tutorial 20 OAuth Setup

Based on tutorials 16-19, we will have:

1. **MCP Server Infrastructure:**
   - FastMCP server deployed on Azure Container Apps
   - Logic Apps workflows as MCP tools
   - Both accessible through APIM gateway

2. **APIM Gateway (Critical for Tutorial 20):**
   - APIM instance with MCP APIs imported
   - Base policies configured (rate limiting, load balancing)
   - Ready to add OAuth Credential Manager policies

3. **Monitoring & Observability:**
   - APIM Analytics configured
   - Token usage metrics
   - Request/response logging

### Additional Resources Needed for Tutorial 20

- [ ] Azure SQL Database
- [ ] Azure AD app registrations (2):
  - AI Agent Application
  - MCP Server Application
- [ ] APIM Credential Manager configuration
- [ ] OAuth connections and access policies

---

## Next Steps After Completion

1. ✅ Validate all Azure resources are created
2. ✅ Document resource URLs and keys in `.env` file
3. ✅ Test basic MCP tool calls through APIM
4. ✅ Prepare for Tutorial 20 implementation
5. ✅ Set up Azure SQL Database for Tutorial 20
6. ✅ Configure APIM OAuth Credential Manager

---

## Issues & Resolutions

| Issue | Tutorial | Resolution | Date |
|-------|----------|------------|------|
| | | | |

---

**Last Updated:** October 13, 2025  
**Next Action:** Start testing Tutorial 16
