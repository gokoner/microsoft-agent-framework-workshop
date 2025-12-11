"""
Tutorial 19: Secure Agent Orchestration Web Interface
Demonstrates Entra ID → APIM → MCP authentication flow
"""

import os
import json
import base64
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# Azure SDK imports
from azure.identity import DefaultAzureCredential

load_dotenv()

app = FastAPI(title="Secure Agent Orchestration Demo")

# Configuration
APIM_GATEWAY_URL = os.getenv("APIM_GATEWAY_URL", "https://apim-a35tm-aiagents.azure-api.net")
APIM_SUBSCRIPTION_KEY = os.getenv("APIM_SUBSCRIPTION_KEY")
MCP_ENDPOINT = f"{APIM_GATEWAY_URL}/travel-mcp/mcp"
TENANT_ID = os.getenv("AZURE_TENANT_ID")
API_CLIENT_ID = os.getenv("API_CLIENT_ID")

# Global state
credential = None
token_info = {}


def decode_jwt(token: str) -> dict:
    """Decode JWT without verification for display."""
    try:
        parts = token.split(".")
        payload_padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(payload_padded))
    except Exception:
        return {}


@app.on_event("startup")
async def startup():
    """Initialize credentials on startup."""
    global credential, token_info
    credential = DefaultAzureCredential()

    # Get token for display
    try:
        scope = f"api://{API_CLIENT_ID}/.default" if API_CLIENT_ID else "https://management.azure.com/.default"
        token = credential.get_token(scope)
        token_info = {
            "token": token.token,
            "expires": datetime.fromtimestamp(token.expires_on).isoformat(),
            "claims": decode_jwt(token.token)
        }
    except Exception as e:
        token_info = {"error": str(e)}


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main UI."""
    claims_html = ""
    if "claims" in token_info:
        for k, v in list(token_info["claims"].items())[:10]:
            claims_html += f'<div class="claim"><span class="claim-name">{k}:</span> <span class="claim-value">{str(v)[:50]}</span></div>'

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Secure Agent Orchestration</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #00d4ff; margin-bottom: 30px; }}
        h2 {{ color: #fff; margin-bottom: 15px; }}

        .section {{ 
            background: rgba(255,255,255,0.05); 
            border-radius: 15px; 
            padding: 25px; 
            margin-bottom: 25px; 
        }}

        .flow-diagram {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .flow-step {{
            text-align: center;
            padding: 15px 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            border: 2px solid #333;
            min-width: 120px;
        }}
        .flow-step .icon {{ font-size: 2em; margin-bottom: 8px; }}
        .flow-step .title {{ font-weight: bold; }}
        .flow-arrow {{ font-size: 1.5em; color: #00d4ff; }}

        .token-box {{
            background: #1a1a1a;
            border-radius: 8px;
            padding: 15px;
            font-family: monospace;
            font-size: 0.85em;
            max-height: 200px;
            overflow-y: auto;
        }}
        .claim {{ margin: 5px 0; }}
        .claim-name {{ color: #00d4ff; }}
        .claim-value {{ color: #00ff88; }}

        .test-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
        .test-card {{
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #333;
        }}
        .test-card h3 {{ margin-bottom: 10px; font-size: 1em; }}
        .status {{ 
            padding: 4px 10px; 
            border-radius: 4px; 
            font-size: 0.9em; 
            display: inline-block;
        }}
        .status-success {{ background: #00ff88; color: #000; }}
        .status-fail {{ background: #ff4444; color: #fff; }}

        button {{
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: #fff;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 15px;
        }}
        button:hover {{ transform: scale(1.02); }}

        #results {{ 
            background: #1a1a1a; 
            border-radius: 8px; 
            padding: 15px; 
            margin-top: 15px;
            min-height: 100px;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Secure Agent Orchestration with Entra ID & APIM</h1>

        <div class="section">
            <h2>Authentication Flow</h2>
            <div class="flow-diagram">
                <div class="flow-step">
                    <div class="icon">👤</div>
                    <div class="title">User</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="icon">🔑</div>
                    <div class="title">Entra ID</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="icon">🛡️</div>
                    <div class="title">APIM</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="icon">🔧</div>
                    <div class="title">MCP Server</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="icon">🤖</div>
                    <div class="title">AI Agent</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Your JWT Token Claims</h2>
            <div class="token-box">
                {claims_html if claims_html else '<div style="color:#ff4444">Token not available</div>'}
            </div>
        </div>

        <div class="section">
            <h2>Security Test Results</h2>
            <div class="test-grid" id="test-results">
                <div class="test-card">
                    <h3>🚫 No Authentication</h3>
                    <p>Testing without any auth headers...</p>
                    <span class="status" id="status-noauth">Pending</span>
                </div>
                <div class="test-card">
                    <h3>🔑 Subscription Key Only</h3>
                    <p>Testing with APIM subscription key...</p>
                    <span class="status" id="status-subkey">Pending</span>
                </div>
                <div class="test-card">
                    <h3>🎫 JWT Token Only</h3>
                    <p>Testing with JWT but no sub key...</p>
                    <span class="status" id="status-jwt">Pending</span>
                </div>
                <div class="test-card">
                    <h3>✅ Full Authentication</h3>
                    <p>Testing with JWT + subscription key...</p>
                    <span class="status" id="status-full">Pending</span>
                </div>
            </div>
            <button onclick="runTests()">Run Security Tests</button>
            <div id="results"></div>
        </div>
    </div>

    <script>
        async function runTests() {{
            document.getElementById('results').textContent = 'Running tests...';
            try {{
                const response = await fetch('/test-auth');
                const data = await response.json();

                data.tests.forEach(test => {{
                    let statusId = '';
                    if (test.scenario.includes('No Auth')) statusId = 'status-noauth';
                    else if (test.scenario.includes('Subscription')) statusId = 'status-subkey';
                    else if (test.scenario.includes('JWT')) statusId = 'status-jwt';
                    else if (test.scenario.includes('Full')) statusId = 'status-full';

                    if (statusId) {{
                        const el = document.getElementById(statusId);
                        el.textContent = test.status_code + ' ' + (test.success ? '✓' : '✗');
                        el.className = 'status ' + (test.success ? 'status-success' : 'status-fail');
                    }}
                }});

                document.getElementById('results').textContent = JSON.stringify(data, null, 2);
            }} catch (e) {{
                document.getElementById('results').textContent = 'Error: ' + e;
            }}
        }}
    </script>
</body>
</html>
"""


@app.get("/test-auth")
async def test_auth():
    """Test different authentication scenarios."""
    tests = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {{"jsonrpc": "2.0", "method": "tools/list", "id": 1}}

        # Test 1: No auth
        try:
            r = await client.post(MCP_ENDPOINT, json=payload, headers={{"Content-Type": "application/json"}})
            tests.append({{"scenario": "No Authentication", "status_code": r.status_code, "success": r.status_code == 200}})
        except Exception as e:
            tests.append({{"scenario": "No Authentication", "status_code": 0, "success": False, "error": str(e)}})

        # Test 2: Subscription key only
        try:
            headers = {{"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": APIM_SUBSCRIPTION_KEY or ""}}
            r = await client.post(MCP_ENDPOINT, json=payload, headers=headers)
            tests.append({{"scenario": "Subscription Key Only", "status_code": r.status_code, "success": r.status_code == 200}})
        except Exception as e:
            tests.append({{"scenario": "Subscription Key Only", "status_code": 0, "success": False, "error": str(e)}})

        # Test 3: JWT only  
        jwt = token_info.get("token", "")
        try:
            headers = {{"Content-Type": "application/json", "Authorization": f"Bearer {{jwt}}"}}
            r = await client.post(MCP_ENDPOINT, json=payload, headers=headers)
            tests.append({{"scenario": "JWT Token Only", "status_code": r.status_code, "success": r.status_code == 200}})
        except Exception as e:
            tests.append({{"scenario": "JWT Token Only", "status_code": 0, "success": False, "error": str(e)}})

        # Test 4: Full auth (JWT + subscription key)
        try:
            headers = {{
                "Content-Type": "application/json", 
                "Ocp-Apim-Subscription-Key": APIM_SUBSCRIPTION_KEY or "",
                "Authorization": f"Bearer {{jwt}}"
            }}
            r = await client.post(MCP_ENDPOINT, json=payload, headers=headers)
            tests.append({{"scenario": "Full Auth (JWT + SubKey)", "status_code": r.status_code, "success": r.status_code == 200}})
        except Exception as e:
            tests.append({{"scenario": "Full Auth (JWT + SubKey)", "status_code": 0, "success": False, "error": str(e)}})

    return {{"tests": tests}}


@app.get("/token-info")
async def get_token():
    """Return token information."""
    return token_info


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)
