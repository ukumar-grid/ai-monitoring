import json
import time
import httpx

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP

mcp = FastMCP("Prometheus-MCP-Server")
PROMETHEUS_URL = "http://localhost:9090"

def resolve_time(time_str: str) -> str:
    """Converts relative strings like 'now()' or '-1m' into Unix timestamps."""
    now = time.time()
    if not time_str or time_str == "now()":
        return str(int(now))
    if time_str.startswith("-"):
        unit = time_str[-1]
        val = int(time_str[1:-1])
        if unit == "m":
            return str(int(now - val * 60))
        elif unit == "h":
            return str(int(now - val * 3600))
        elif unit == "s":
            return str(int(now - val))
    return time_str

@mcp.tool()
async def query_prometheus_instant(promql: str) -> str:
    """Executes a PromQL instant query against live Prometheus metrics."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": promql},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                results = data.get("data", {}).get("result", [])
                if not results:
                    return json.dumps({"status": "no_data", "message": f"No metric series returned for query: {promql}"})
                return json.dumps({"status": "success", "result": results})
            return json.dumps({"status": "error", "message": data.get("error", "Unknown error")})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
async def query_prometheus_range(promql: str, start_time: str, end_time: str = "now()", step: str = "15s") -> str:
    """Executes a PromQL range query over a specified timeframe."""
    async with httpx.AsyncClient() as client:
        try:
            start_ts = resolve_time(start_time)
            end_ts = resolve_time(end_time)
            
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query_range",
                params={
                    "query": promql,
                    "start": start_ts,
                    "end": end_ts,
                    "step": step
                },
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return json.dumps({"status": "success", "result": data.get("data", {}).get("result", [])})
            return json.dumps({"status": "error", "message": data.get("error", "Unknown error")})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

if __name__ == "__main__":
    mcp.run()