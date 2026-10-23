import asyncio
import json
import sys
import datetime
import zoneinfo
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL_NAME = "qwen2.5:7b"

def get_current_ist_timestamp() -> str:
    """Returns current date and time in Indian Standard Time (IST) formatted string."""
    ist = zoneinfo.ZoneInfo("Asia/Kolkata")
    now = datetime.datetime.now(ist)
    return now.strftime("%Y-%m-%d %H:%M:%S IST")

def get_system_prompt(current_time_str: str) -> str:
    return f"""You are an automated AI Site Reliability Engineer (SRE).
Your objective is to investigate infrastructure alerts using live Prometheus metrics via MCP tools.

CRITICAL RULES:
1. Always run tools to inspect metrics before rendering a verdict. Never assume numbers.
2. Ground every claim strictly in retrieved metric data.
3. IMPORTANT METRIC SCHEMA:
   - Request metric: `http_requests_total`
   - Job label: `job="mock-service"` (NOT `job="mock-app"`)
   - Status label: `code="500"` or `code="200"` (NOT `status_code`)
   - Route label: `route="/api/checkout"`
4. Use the EXACT current timestamp provided below for the report header: `{current_time_str}`
5. Output your final answer ONLY in the structured Markdown format specified below:

# 🚨 Incident Investigation Report

**Report Generated:** {current_time_str}
**Target Application:** mock-service
**Status:** [CRITICAL | WARNING | NORMAL]

---

### 1. Executive Summary
Brief high-level summary of findings.

### 2. Evidence & Observed Metrics
- **Metric Queried:** `metric_name`
- **Observed Value:** <exact numbers returned>
- **Affected Route/Component:** <e.g. /api/checkout>

### 3. Root Cause Analysis
Explain what caused the metric pattern based strictly on observations.

### 4. Recommended Remediation
- Action item 1
- Action item 2
"""

async def run_investigation(user_query: str) -> str:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_prometheus_server.py"]
    )

    # Calculate current live IST timestamp
    current_time_ist = get_current_ist_timestamp()
    system_prompt = get_system_prompt(current_time_ist)

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()
            ollama_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                } for tool in mcp_tools.tools
            ]

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]

            response = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                tools=ollama_tools
            )
            messages.append(response['message'])

            if response['message'].get('tool_calls'):
                for call in response['message']['tool_calls']:
                    tool_name = call['function']['name']
                    tool_args = call['function']['arguments']
                    
                    print(f"[TOOL CALL] {tool_name}({json.dumps(tool_args)})")
                    
                    mcp_result = await session.call_tool(tool_name, tool_args)
                    result_text = mcp_result.content[0].text
                    
                    messages.append({"role": "tool", "content": result_text})

                final_response = ollama.chat(model=MODEL_NAME, messages=messages)
                report_content = final_response['message']['content']
            else:
                report_content = response['message']['content']

            return report_content

if __name__ == "__main__":
    query = "Investigate http_requests_total for HTTP 500 errors across our endpoints."
    report = asyncio.run(run_investigation(query))
    
    print("\n" + report)
    
    filename = f"incident_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w") as f:
        f.write(report)
    print(f"\n[SUCCESS] Report written to {filename}")