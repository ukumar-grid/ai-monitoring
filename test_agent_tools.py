import json
import ollama

# 1. Define Python tool function (simulating a Prometheus instant query)
def query_prometheus_instant(query: str) -> str:
    """
    Executes an instant PromQL query against the Prometheus API.
    
    Args:
        query: PromQL expression string (e.g., 'http_requests_total{code="500"}')
    """
    print(f"\n[TOOL EXECUTING] querying Prometheus with PromQL: '{query}'")
    
    # Mock responses mimicking Prometheus API JSON output
    if "code=\"500\"" in query or "status=\"500\"" in query:
        return json.dumps({
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [{
                    "metric": {"method": "GET", "route": "/api/checkout", "code": "500"},
                    "value": [1710000000, "142.0"]
                }]
            }
        })
    else:
        return json.dumps({
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [{
                    "metric": {"method": "GET", "route": "/api/checkout", "code": "200"},
                    "value": [1710000000, "1205.0"]
                }]
            }
        })


# 2. Define standard Ollama / OpenAI function tool schema
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "query_prometheus_instant",
            "description": "Query Prometheus instant metric value using PromQL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Valid PromQL query, e.g., 'http_requests_total' or 'node_cpu_seconds_total'"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def run_agent_turn(user_prompt: str):
    MODEL = "qwen2.5:7b"
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI SRE/Monitoring Assistant. "
                "Use available tools to fetch infrastructure metrics before making claims. "
                "Do not invent metrics."
            )
        },
        {"role": "user", "content": user_prompt}
    ]

    print(f"User Prompt: '{user_prompt}'\n" + "-"*50)

    # First loop: Pass user query and tools to model
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=tools_schema
    )

    # Append assistant's decision to context
    messages.append(response['message'])

    # Check if the LLM elected to call any tools
    if response['message'].get('tool_calls'):
        available_tools = {
            "query_prometheus_instant": query_prometheus_instant
        }

        for tool in response['message']['tool_calls']:
            fn_name = tool['function']['name']
            fn_args = tool['function']['arguments']
            
            if fn_name in available_tools:
                # Execute tool
                tool_result = available_tools[fn_name](**fn_args)
                
                # Append tool output to message chain
                messages.append({
                    "role": "tool",
                    "content": tool_result
                })

        # Second loop: Pass tool output back to LLM for synthesis
        final_response = ollama.chat(
            model=MODEL,
            messages=messages
        )
        
        print("\n[FINAL AI RESPONSE]")
        print(final_response['message']['content'])
    else:
        print("\n[AI RESPONSE (No tools used)]")
        print(response['message']['content'])


if __name__ == "__main__":
    run_agent_turn("Can you check if there are any HTTP 500 errors occurring on our checkout endpoint right now?")
