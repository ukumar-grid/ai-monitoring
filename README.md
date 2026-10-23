


🤖 AI-Powered Infrastructure Monitoring & Intelligent Incident Analysis Agent
An autonomous, locally hosted SRE (Site Reliability Engineering) agent built using Ollama, Model Context Protocol (MCP), Prometheus, and Grafana.
The agent continuously monitors system health, detects operational failure patterns (such as HTTP 500 error spikes), uses native tool calling to perform multi-step root-cause investigations against live metrics, generates structured Markdown incident reports in Indian Standard Time (IST), and dispatches real-time email alerts.

🏗️ Architecture & Operational Flow
               +----------------------------------+
               |  Mock Target Application         |
               |  (Express.js Service on :3001)   |
               +-----------------+----------------+
                                 |
                                 | Pulls /metrics (5s scrape)
                                 v
               +----------------------------------+
               |  Prometheus Metrics Collector    | <----> [ Grafana Dashboard ]
               |  (Time-Series Database on :9090) |        (Visual Verification)
               +-----------------+----------------+
                                 |
                                 | PromQL Instant & Range Queries
                                 v
               +----------------------------------+
               |  Prometheus MCP Server           |
               |  (In-Process Stdio Transport)    |
               +-----------------+----------------+
                                 |
                                 | JSON-RPC Tool Discovery & Invocation
                                 v
               +----------------------------------+
               |  Python AI Agent Execution Loop  |
               +-----------------+----------------+
                                 |
                                 | System Prompt + Metric Vector Payloads
                                 v
               +----------------------------------+
               |  Ollama Local LLM Runtime        |
               |  (Model: qwen2.5:7b)             |
               +-----------------+----------------+
                                 |
                                 +-------------------------+
                                 |                         |
                                 v                         v
                   +---------------------------+ +-------------------+
                   | Structured Markdown       | | Automated Email   |
                   | Incident Report (.md)     | | Alert (via SMTP)  |
                   +---------------------------+ +-------------------+

🚀 Core Features & Technical Highlights
* 100% Local AI Reasoning: Powered by qwen2.5:7b via Ollama. Keeps inference local, avoids external LLM API costs, and supports low-latency SRE investigations.
* Model Context Protocol (MCP): Uses the MCP SDK over stdio transport. The agent dynamically discovers and invokes PromQL query tools (query_prometheus_instant and query_prometheus_range) exposed by an in-process FastMCP server.
* Automated Anomaly Detection Loop: A background polling process continuously checks metric rates using PromQL, such as sum(rate(http_requests_total{code="500"}[1m])). When an anomaly is detected, it launches the AI investigation agent.
* Controlled Chaos Simulation: Includes chaos endpoints such as /chaos/error-spike/enable to simulate failure scenarios, including HTTP 500 error spikes and variable latency.
* Evidence-Grounded Reporting: Uses system prompt constraints to reduce unsupported model claims. Reports include IST timestamps and reference observed metric counters, routes, and status codes.
* Real-Time SMTP Email Dispatch: Sends formatted incident investigation reports to a configured administrator inbox using Gmail SMTP.

🛠️ Stack & Technologies
Layer	Technology	Description
Monitored App	Node.js / Express	Target service exposing Prometheus metrics through prom-client
Observability	Prometheus + Grafana	Metrics collection, time-series storage, and dashboard visualization
AI Runtime	Ollama (qwen2.5:7b)	Local LLM runtime supporting tool-calling workflows
Protocol	Model Context Protocol (MCP)	Standardized interface for AI agents to interact with external tools
Automation	Python 3.10+ (httpx, asyncio)	Asynchronous monitoring loop, agent execution cycle, and SMTP emailer
📂 Repository Structure
ai-infra-monitor/
├── docker-compose.yml          # Prometheus, Grafana, and mock app configuration
├── .gitignore                  # Excludes virtual environments, secrets, and reports
├── agent.py                    # MCP client, prompts, and AI execution loop
├── auto_monitor.py             # Background monitoring and SMTP alert sender
├── mcp_prometheus_server.py    # FastMCP server wrapping the Prometheus HTTP API
├── prometheus/
│   └── prometheus.yml          # Prometheus scrape job configuration
└── mock-app/
    ├── Dockerfile              # Container image for the target application
    ├── package.json            # Express and prom-client dependencies
    └── app.js                  # Application, metrics, and chaos endpoints

⚙️ Local Setup & Installation
1. Prerequisites
Install the following:
* Docker Desktop
* Ollama
* Python 3.10 or higher
* Git
2. Clone the Repository
Replace YOUR_GITHUB_USERNAME with your GitHub username and ensure the repository exists.
git clone https://github.com/YOUR_GITHUB_USERNAME/ai-infra-monitor.git
cd ai-infra-monitor
3. Create a Python Virtual Environment
macOS / Linux:
python3 -m venv myenv
source myenv/bin/activate
Windows PowerShell:
python -m venv myenv
.\myenv\Scripts\Activate.ps1
Install the required Python dependencies:
python -m pip install --upgrade pip
pip install mcp httpx ollama
4. Pull the Ollama Model
ollama pull qwen2.5:7b
Ensure Ollama is running and the model is available before starting the agent.
5. Launch Infrastructure Services
Start Prometheus, Grafana, and the mock application using Docker Compose:
docker compose up -d --build
Verify the service endpoints:
Service	URL
Prometheus UI	http://localhost:9090
Grafana UI	http://localhost:3000
Mock application metrics	http://localhost:3001/metrics
Grafana: If you have not configured credentials, the default local Grafana credentials are often admin / admin. Change the password when prompted.

🧪 Testing & Execution
1. Configure Email Credentials
Configure the SMTP credentials used by auto_monitor.py.
Prefer environment variables instead of hardcoding passwords in the source code. For Gmail, generate an app password if your account configuration supports it.
For example, set these environment variables before running the agent.
macOS / Linux:
export SENDER_EMAIL="your_email@gmail.com"
export SENDER_PASSWORD="your_16_char_app_password"
export RECIPIENT_EMAIL="your_email@gmail.com"
Windows PowerShell:
$env:SENDER_EMAIL="your_email@gmail.com"
$env:SENDER_PASSWORD="your_16_char_app_password"
$env:RECIPIENT_EMAIL="your_email@gmail.com"
Update auto_monitor.py to read these variables using Python's os.environ or os.getenv.
Never commit real email credentials, app passwords, or other secrets to GitHub.
2. Trigger Chaos Mode
Enable the simulated HTTP 500 error spike:
curl -X POST http://localhost:3001/chaos/error-spike/enable
Generate failing traffic against the checkout route:
for i in {1..10}; do
  curl -s http://localhost:3001/api/checkout > /dev/null
done
The loop above works in Bash-compatible terminals. On Windows PowerShell, use:
1..10 | ForEach-Object {
    Invoke-WebRequest `
        -Uri http://localhost:3001/api/checkout `
        -Method GET `
        -SkipHttpErrorCheck | Out-Null
}
Adjust the HTTP method if your application defines the checkout endpoint differently.
3. Start Automated Monitoring
In a terminal with the Python virtual environment activated, run:
python auto_monitor.py
The monitoring process should periodically query Prometheus, detect the configured anomaly, launch the AI investigation, and send an email report if the required conditions and credentials are satisfied.
Illustrative terminal output:
Starting Automated Incident Monitoring Loop (Interval: 15s)...

[ALERT TRIGGERED] 500 Error rate detected: 0.6 req/sec
[AUTOMATION] Launching AI Agent Investigation...
[TOOL CALL] query_prometheus_instant({
    "promql": "http_requests_total{job=\"mock-service\", code=\"500\"}"
})

--- GENERATED REPORT ---
# 🚨 Incident Investigation Report

**Target Application:** mock-service
**Status:** CRITICAL

---

### 1. Executive Summary

Critical HTTP 500 error rates detected on route /api/checkout...

[EMAIL SENT] Incident report successfully sent.
The output above is an example. Actual logs, metrics, report contents, and email delivery depend on your implementation and runtime configuration.
4. Verify the Results
* Open Prometheus and inspect the relevant HTTP request metrics.
* Open Grafana to review the configured dashboards.
* Check the generated incident report.
* Confirm that the alert email reaches the configured recipient.
5. Disable Chaos Mode
Restore normal application behavior:
curl -X POST http://localhost:3001/chaos/error-spike/disable

📄 Example Generated Email Incident Report
Subject: 🚨 [CRITICAL ALERT] AI Incident Report: /api/checkout Error Spike
Recipient: Configured administrator email address
# 🚨 Incident Investigation Report

**Report Generated:** 2026-10-23 11:48:00 IST
**Target Application:** mock-service
**Status:** CRITICAL

---

### 1. Executive Summary

A critical increase in HTTP 500 status code responses was detected on the
`/api/checkout` route of the `mock-service` application.

### 2. Evidence & Observed Metrics

- **Metric Queried:** `http_requests_total{job="mock-service", code="500", route="/api/checkout"}`
- **Observed Value:** 48 failure requests
- **Affected Route/Component:** `/api/checkout`

### 3. Root Cause Analysis

The sudden spike in HTTP 500 responses indicates backend execution failures
on the checkout endpoint. Observed latency increases up to 2 seconds may
correlate with event-loop blockage, unhandled exceptions, or slow dependencies.

These hypotheses should be validated against application logs and supporting
metrics before being treated as a confirmed root cause.

### 4. Recommended Remediation

- Inspect application runtime logs for `/api/checkout` stack traces.
- Verify database connection pool limits and dependent service response times.
- Review recent service deployments and configuration changes.
- Monitor error rates and latency after remediation.
The metric values, timestamps, and incident details above are illustrative examples, not verified live observations.

🔒 Security Best Practices
* Keep SMTP passwords, API credentials, and other secrets out of source control.
* Store local credentials in environment variables or a secrets manager.
* Add .env, virtual environments, generated reports, and other sensitive files to .gitignore as appropriate.
* Restrict access to local monitoring dashboards and application endpoints.
* Validate and authenticate any operational endpoints before exposing them beyond a trusted development environment.
* Treat AI-generated root-cause explanations as hypotheses until corroborated by telemetry and logs.

🧹 Stop the Infrastructure
To stop the Docker Compose services:
docker compose down
To stop the services and remove their Compose-managed volumes as well, use the following only if you intend to delete the stored data:
docker compose down --volumes


