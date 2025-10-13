# Microsoft Agent Framework Workshop

Comprehensive hands-on workshop for building AI agents using Microsoft's Agent Framework. This repository contains progressive tutorials covering everything from basic agent creation to advanced multi-agent workflows and production monitoring.

## Tutorial Series

| # | Tutorial | Topics Covered | Duration |
|---|----------|----------------|----------|
| 01 | [Basic Agent](./01_basic_agent.ipynb) | Agent creation, responses, OpenAI setup | 15 min |
| 01b | [Azure AI Foundry](./01b_azure_ai_foundry.ipynb) | Azure deployment, model endpoints | 20 min |
| 02 | [Agent with Tools](./02_agent_with_tools.ipynb) | Function calling, tool integration | 25 min |
| 03 | [Multi-turn Conversations](./03_multi_turn_conversations.ipynb) | Context management, conversation flow | 30 min |
| 04 | [Context & Memory](./04_context_and_memory.ipynb) | Memory systems, retrieval patterns | 35 min |
| 05 | [Middleware & Filters](./05_middleware_and_filters.ipynb) | Request/response pipelines, telemetry | 30 min |
| 06 | [Multi-Agent Workflows](./06_multi_agent_workflows.ipynb) | Agent collaboration, orchestration | 40 min |
| 07 | [Advanced Workflows](./07_advanced_workflows.ipynb) | Complex patterns, state management | 45 min |
| 08 | [Human-in-the-Loop](./08_human_in_the_loop.ipynb) | Approval workflows, feedback loops | 30 min |
| 09 | [Error Handling](./09_error_handling_recovery.ipynb) | Retry logic, fault tolerance | 25 min |
| 10 | [Azure File Search](./10_azure_file_search_demo.ipynb) | Vector search, RAG patterns | 35 min |
| 10b | [Competitive Intelligence](./10_competitive_intelligence_workflow.ipynb) | Multi-agent workflow, document analysis | 45 min |
| 11 | [DevUI Integration](./11_devui_competitive_intelligence.ipynb) | Development UI, testing workflows | 20 min |
| 12 | [Azure Monitor Integration](./12_azure_monitor_alerts.ipynb) | Monitoring, alerting, Log Analytics | 40 min |
| 13 | [Multi-Agent Pricing Analysis](./13_Pricing-Competitive-Intelligence-multiagent.ipynb) | Advanced orchestration, pricing intelligence | 50 min |
| 14 | [Unified Web App Monitoring](./14_unified_webapp_agent_monitoring.ipynb) | Log correlation, unified dashboards | 35 min |

**Total Learning Time**: ~7 hours

## To Be Delivered (TBD)

### Enterprise MCP Server Pattern

Advanced enterprise integration pattern demonstrating Model Context Protocol (MCP) server architecture with Azure services:

**Components:**
1. **FastMCP Server Implementation**
   - Create MCP server using fastmcp framework
   - Implement custom tools and capabilities
   - Deploy as Azure Container App for scalability

2. **Logic App MCP Integration**
   - Create Azure Logic App workflow
   - Register Logic App as MCP server in Azure API Center
   - Enable serverless workflow orchestration

3. **API Management (APIM) Gateway**
   - Connect both MCP servers to Azure APIM
   - Apply enterprise policies (rate limiting, authentication, logging)
   - Centralized API governance and monitoring

4. **AI Agent Workflow**
   - Build AI agent consuming both MCP servers as tools
   - Demonstrate enterprise workflow patterns
   - Show multi-service orchestration with governance

**Learning Objectives:**
- MCP server development and deployment
- Azure Container Apps for microservices
- Logic Apps as serverless MCP endpoints
- API Center for service registration
- APIM policies for enterprise security
- Multi-MCP agent orchestration

**Enterprise Benefits:**
- Centralized governance and monitoring
- Policy-based security and rate limiting
- Scalable container-based deployment
- Serverless workflow integration
- Production-ready enterprise patterns

## Getting Started

### Prerequisites

- Python 3.11+
- Azure subscription (for Azure AI Foundry tutorials)
- OpenAI API key or Azure OpenAI endpoint

### Setup

```bash
# Clone the repository
git clone https://github.com/gokoner/microsoft-agent-framework-workshop.git
cd microsoft-agent-framework-workshop

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env  # Edit with your API keys
```

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL_ID=gpt-4

# Azure AI Foundry Configuration (for Azure tutorials)
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Monitor Configuration (for monitoring tutorials)
WORKSPACE_ID=...
WORKSPACE_NAME=...
```

### Run Your First Agent

```bash
jupyter notebook 01_basic_agent.ipynb
```

## Documentation

- [Official Documentation](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
- [API Reference](https://learn.microsoft.com/python/api/overview/azure/ai-projects)
- [GitHub Repository](https://github.com/microsoft/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects)

## Special Topics

- [launch_devui.py](./launch_devui.py) - Development UI for testing agents

## Azure Resources Included

### Azure Workbooks

- **ai_agent_monitoring_workbook_openai_style.json** - Production-ready Azure Monitor workbook with:
  - Service health overview
  - Performance trends
  - Cost and usage insights
  - Error correlation
  - Built-in monitoring guide

### Sample Data

- **sample_data/competitive_analysis/** - Example data for pricing intelligence workflows
  - Input PDF documents
  - Extracted product data
  - Generated analysis reports

## Real-World Applications

The tutorials in this workshop demonstrate patterns used in production systems:

- Multi-agent orchestration for complex workflows
- Azure Document Intelligence integration
- Persistent memory with Mem0
- Azure Monitor integration for observability
- Log correlation across multiple services
- Cost optimization and performance monitoring

## Contributing

Contributions welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Setting up your development environment
- Code style and best practices
- Submitting pull requests
- Reporting issues

We also follow a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive community.

## License

GNU General Public License v3.0 - See [LICENSE](LICENSE) file for details

## Related Projects

- [Azure AI Samples](https://github.com/Azure-Samples/azure-ai-samples) - Official Azure AI examples
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python) - Azure SDK repository

---

**Last Updated**: October 2025  
**Repository**: https://github.com/gokoner/microsoft-agent-framework-workshop
