🤖 AI-Powered Infrastructure Monitoring & Intelligent Incident Analysis Agent

An autonomous, locally hosted Site Reliability Engineering (SRE) agent built using Ollama, Model Context Protocol (MCP), Prometheus, and Grafana.

The agent continuously monitors system health, detects operational failure patterns such as HTTP 500 error spikes, and uses native tool calling to perform multi-step root-cause investigations against live metrics. It generates structured Markdown incident reports with timestamps in Indian Standard Time (IST) and dispatches real-time email alerts.

🏗️ Architecture & Operational Flow
+--------------------------------------+
|       Mock Target Application        |
|       Express.js Service :3001       |
+-------------------+------------------+
                    |
                    | Scrapes /metrics every 5 seconds
                    v
+--------------------------------------+
|      Prometheus Metrics Collector    | <----> Grafana Dashboard
|      Time-Series Database :9090      |        (Visualization)
+-------------------+------------------+
                    |
                    | PromQL Instant & Range Queries
                    v
+--------------------------------------+
|        Prometheus MCP Server         |
|        In-Process Stdio Transport    |
+-------------------+------------------+
                    |
                    | JSON-RPC Tool Discovery & Invocation
                    v
+--------------------------------------+
|       Python AI Agent Execution      |
|       Monitoring & Investigation     |
+-------------------+------------------+
                    |
                    | System Prompt + Metric Data
                    v
+--------------------------------------+
|          Ollama Local Runtime        |
|          Model: qwen2.5:7b           |
+-------------------+------------------+
                    |
                    +--------------------------+
                    |                          |
                    v                          v
       +--------------------------+  +--------------------------+
       | Structured Markdown      |  | Automated Email Alert    |
       | Incident Report (.md)    |  | SMTP Delivery            |
       +--------------------------+  +--------------------------+

Workflow
Metrics Collection: The mock Express.js application exposes Prometheus metrics.
Monitoring: Prometheus scrapes application metrics at configured intervals.
Anomaly Detection: The Python monitoring process evaluates PromQL queries to detect abnormal error rates.
AI Investigation: When an anomaly is detected, the agent invokes Prometheus tools through MCP.
Root-Cause Analysis: The local LLM analyzes observed metrics and generates an incident assessment.
Report Generation: The agent produces a structured Markdown incident report with IST timestamps.
Email Notification: The monitoring process sends the incident report to the configured administrator.
🚀 Core Features & Technical Highlights
100% Local AI Reasoning: Uses qwen2.5:7b through Ollama to keep LLM inference local and avoid external LLM API costs.
Model Context Protocol (MCP): Uses the MCP SDK over stdio transport. The agent dynamically discovers and invokes Prometheus query tools, including query_prometheus_instant and query_prometheus_range.
Automated Anomaly Detection: Runs a background monitoring loop that periodically evaluates metrics using PromQL.

Example query:

sum(rate(http_requests_total{code="500"}[1m]))

Controlled Chaos Simulation: Provides endpoints such as /chaos/error-spike/enable to simulate HTTP 500 error spikes and variable latency.
Evidence-Grounded Reporting: Uses system prompt constraints to reduce unsupported claims. Reports reference observed metrics, routes, status codes, and timestamps.
Real-Time SMTP Email Alerts: Sends formatted incident investigation reports to a configured administrator inbox using Gmail SMTP.
Observability Integration: Combines Prometheus metrics collection with Grafana dashboards for operational visibility and manual verification.
🛠️ Tech Stack
Layer	Technology	Description
Monitored Application	Node.js, Express.js	Target service exposing Prometheus metrics through prom-client
Observability	Prometheus, Grafana	Metrics collection, time-series storage, and dashboard visualization
AI Runtime	Ollama, qwen2.5:7b	Local LLM runtime supporting tool-calling workflows
Agent Protocol	Model Context Protocol (MCP)	Standardized interface for interacting with external tools
Automation	Python 3.10+	Monitoring loop, AI agent execution, and SMTP alerting
HTTP Client	httpx	Asynchronous HTTP communication
Async Execution	Python asyncio	Asynchronous monitoring and agent orchestration
Containerization	Docker, Docker Compose	Runs the application and observability services
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
    ├── package.json            # Express.js and prom-client dependencies
    └── app.js                  # Application, metrics, and chaos endpoints

⚙️ Local Setup & Installation
1. Prerequisites

Install the following tools before proceeding:

Docker Desktop
Ollama
Python 3.10 or higher
Git

Ensure Docker is running and Ollama is available on your machine.

2. Clone the Repository

Replace YOUR_GITHUB_USERNAME with your GitHub username.

git clone https://github.com/YOUR_GITHUB_USERNAME/ai-infra-monitor.git
cd ai-infra-monitor

Note: Replace the placeholder with the actual repository URL after publishing the project to GitHub.
3. Create a Python Virtual Environment

macOS / Linux

python3 -m venv myenv
source myenv/bin/activate


Windows PowerShell

python -m venv myenv
.\myenv\Scripts\Activate.ps1


Install the required Python dependencies:

python -m pip install --upgrade pip
python -m pip install mcp httpx ollama

4. Pull the Ollama Model

Download the model used by the agent:

ollama pull qwen2.5:7b


Ensure Ollama is running and the model is available before starting the agent.

5. Launch the Infrastructure

Start Prometheus, Grafana, and the mock application using Docker Compose:

docker compose up -d --build


Verify that the services are accessible.

Service	URL
Prometheus UI	http://localhost:9090
Grafana UI	http://localhost:3000
Mock Application Metrics	http://localhost:3001/metrics

Grafana credentials: If you have not configured custom credentials, the default local credentials are often admin / admin. Change the password when prompted.

🧪 Testing & Execution
1. Configure Email Credentials

The automated monitoring script uses SMTP to send incident reports.

For Gmail, generate an app password if your account supports it. Configure the following environment variables before running the monitoring process.

macOS / Linux

export SENDER_EMAIL="your_email@gmail.com"
export SENDER_PASSWORD="your_16_char_app_password"
export RECIPIENT_EMAIL="your_email@gmail.com"


Windows PowerShell

$env:SENDER_EMAIL="your_email@gmail.com"
$env:SENDER_PASSWORD="your_16_char_app_password"
$env:RECIPIENT_EMAIL="your_email@gmail.com"


Update auto_monitor.py to read these variables using Python's os.environ or os.getenv.

Security: Never commit real email credentials, app passwords, or other secrets to GitHub.
2. Trigger Chaos Mode

Enable the simulated HTTP 500 error spike:

curl -X POST http://localhost:3001/chaos/error-spike/enable


Generate failing traffic against the checkout endpoint.

Bash-compatible terminals

for i in {1..10}; do
  curl -s http://localhost:3001/api/checkout > /dev/null
done


Windows PowerShell

1..10 | ForEach-Object {
    Invoke-WebRequest `
        -Uri http://localhost:3001/api/checkout `
        -Method GET `
        -SkipHttpErrorCheck | Out-Null
}


Adjust the HTTP method if your application defines the checkout endpoint differently.

3. Start Automated Monitoring

Activate the Python virtual environment and run:

python auto_monitor.py


The monitoring process should periodically query Prometheus, detect the configured anomaly, launch the AI investigation, and send an email report when the required conditions and credentials are satisfied.

Illustrative terminal output

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

Note: This is example output. Actual logs, metrics, reports, and email delivery depend on your implementation and runtime configuration.
4. Verify the Results
Open Prometheus and inspect the relevant HTTP request metrics.
Open Grafana and review the configured dashboards.
Check the generated incident report.
Confirm that the alert email reaches the configured recipient.
Verify that the investigation references observed telemetry rather than unsupported assumptions.
5. Disable Chaos Mode

Restore normal application behavior:

curl -X POST http://localhost:3001/chaos/error-spike/disable

📄 Example Generated Incident Report

The following is an illustrative example of the Markdown incident report that can be included in the automated email alert.

Email Subject: 🚨 [CRITICAL ALERT] AI Incident Report: /api/checkout Error Spike

Recipient: Configured administrator email address

🚨 Incident Investigation Report

Report Generated: 2026-10-23 11:48:00 IST
Target Application: mock-service
Status: CRITICAL

1. Executive Summary

A critical increase in HTTP 500 status code responses was detected on the /api/checkout route of the mock-service application.

2. Evidence & Observed Metrics
Metric Queried: http_requests_total{job="mock-service", code="500", route="/api/checkout"}
Observed Value: 48 failure requests
Affected Route/Component: /api/checkout
3. Root Cause Analysis

The sudden spike in HTTP 500 responses indicates backend execution failures on the checkout endpoint. Observed latency increases of up to two seconds may correlate with event-loop blockage, unhandled exceptions, or slow dependencies.

These explanations are hypotheses and should be validated against application logs and supporting metrics before being treated as confirmed root causes.

4. Recommended Remediation
Inspect application runtime logs for stack traces associated with /api/checkout.
Verify database connection pool limits and dependent service response times.
Review recent service deployments and configuration changes.
Monitor error rates and latency after remediation.
Important: The metric values, timestamps, and incident details in this example are illustrative. They are not verified live observations.
🔒 Security Best Practices
Never commit SMTP passwords, API credentials, or other secrets to source control.
Store local credentials in environment variables or a dedicated secrets manager.
Add .env files, virtual environments, generated reports, and other sensitive files to .gitignore as appropriate.
Restrict access to local monitoring dashboards and application endpoints.
Validate and authenticate operational endpoints before exposing them beyond a trusted development environment.
Treat AI-generated root-cause explanations as hypotheses until corroborated by telemetry and logs.
Avoid logging credentials or other sensitive information during incident investigations.
Use least-privilege access for services and accounts wherever possible.
🧹 Stop the Infrastructure

Stop the Docker Compose services:

docker compose down


To stop the services and remove their Compose-managed volumes, run the following command only if you intend to delete the stored data:

docker compose down --volumes

Warning: Removing volumes can permanently delete persisted data, depending on your Docker Compose configuration.
📌 Future Enhancements

Potential improvements for the project include:

Multi-service monitoring and incident correlation.
Additional anomaly detection strategies for latency, throughput, and resource utilization.
Persistent incident history and report storage.
Alert deduplication and incident severity classification.
Integration with Slack, Microsoft Teams, or other notification platforms.
Automated recovery workflows with approval controls.
Unit and integration tests for MCP tools and investigation workflows.
