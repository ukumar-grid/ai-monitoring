# 🤖 AI-Powered Infrastructure Monitoring & Intelligent Incident Analysis Agent

An autonomous, locally hosted Site Reliability Engineering (SRE) agent built with Ollama, the Model Context Protocol (MCP), Prometheus, and Grafana.

The agent monitors system health, detects patterns such as HTTP 500 error spikes, and investigates live metrics. It generates timestamped Markdown incident reports in Indian Standard Time (IST) and can send email alerts.

## 🏗️ Architecture

```text
Mock Express.js application (:3001)
        │ exposes /metrics
        ▼
Prometheus (:9090) ◄──────► Grafana (:3000)
        │ PromQL queries
        ▼
Prometheus MCP server (stdio)
        │ tool discovery and invocation
        ▼
Python monitoring agent ─────► Ollama (qwen2.5:7b)
        │                            │
        └──────── incident report ◄──┘
                     │
                     └──────────────► Email alert (SMTP)
```

### Workflow

1. The mock Express.js application exposes Prometheus metrics.
2. Prometheus scrapes the application at configured intervals.
3. The Python monitor evaluates PromQL queries for abnormal error rates.
4. On an anomaly, the agent invokes Prometheus tools through MCP.
5. The local LLM analyzes observed metrics and creates an incident assessment.
6. The agent writes a Markdown report with an IST timestamp and can email it to a configured recipient.

## 🚀 Features

- **Local AI reasoning:** Uses `qwen2.5:7b` through Ollama; inference runs locally.
- **MCP tool use:** Discovers and invokes `query_prometheus_instant` and `query_prometheus_range` tools over stdio.
- **Automated anomaly detection:** Periodically evaluates PromQL queries in a background loop.
- **Chaos simulation:** Endpoints such as `/chaos/error-spike/enable` simulate HTTP 500 spikes and variable latency.
- **Evidence-grounded reports:** Prompts the model to cite observed metrics, routes, status codes, and timestamps.
- **Email alerts:** Sends incident reports through Gmail SMTP.
- **Observability:** Combines Prometheus metrics with Grafana dashboards.

Example PromQL query:

```promql
sum(rate(http_requests_total{code="500"}[1m]))
```

## 🛠️ Tech stack

| Layer | Technology | Description |
| --- | --- | --- |
| Monitored application | Node.js, Express.js | Exposes Prometheus metrics through `prom-client`. |
| Observability | Prometheus, Grafana | Metrics collection, storage, and visualization. |
| AI runtime | Ollama, `qwen2.5:7b` | Local LLM runtime for tool-calling workflows. |
| Agent protocol | Model Context Protocol (MCP) | Interface for interacting with tools. |
| Automation | Python 3.10+ | Monitoring, agent execution, and SMTP alerting. |
| HTTP client | `httpx` | Asynchronous HTTP communication. |
| Async execution | Python `asyncio` | Agent and monitoring orchestration. |
| Containerization | Docker, Docker Compose | Runs the application and observability services. |

## 📂 Repository structure

```text
ai-infra-monitor/
├── docker-compose.yml          # Prometheus, Grafana, and mock app configuration
├── .gitignore                  # Excludes virtual environments, secrets, and reports
├── agent.py                    # MCP client, prompts, and AI execution loop
├── auto_monitor.py             # Background monitoring and SMTP alert sender
├── mcp_prometheus_server.py    # MCP server wrapping the Prometheus HTTP API
├── prometheus/
│   └── prometheus.yml          # Prometheus scrape job configuration
└── mock-app/
    ├── Dockerfile              # Container image for the target application
    ├── package.json            # Express.js and prom-client dependencies
    └── app.js                  # Application, metrics, and chaos endpoints
```

## ⚙️ Local setup

### Prerequisites

- Docker Desktop
- Ollama
- Python 3.10 or later
- Git

Ensure Docker is running and Ollama is available on your machine.

### 1. Clone the repository

Replace `YOUR_GITHUB_USERNAME` with your GitHub username. Update the URL if your repository has a different name.

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/ai-infra-monitor.git
cd ai-infra-monitor
```

### 2. Create a Python virtual environment

**macOS / Linux**

```bash
python3 -m venv myenv
source myenv/bin/activate
```

**Windows PowerShell**

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

Install the Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install mcp httpx ollama
```

### 3. Pull the Ollama model

```bash
ollama pull qwen2.5:7b
```

Make sure Ollama is running and the model is available before starting the agent.

### 4. Start the infrastructure

```bash
docker compose up -d --build
```

| Service | URL |
| --- | --- |
| Prometheus UI | <http://localhost:9090> |
| Grafana UI | <http://localhost:3000> |
| Mock application metrics | <http://localhost:3001/metrics> |

If you have not configured custom Grafana credentials, the default local credentials are often `admin` / `admin`. Change the password when prompted.

## 🧪 Run a monitoring demonstration

### 1. Configure email credentials (optional)

For Gmail, generate an app password if your account supports it. Set the following variables before running the monitor.

**macOS / Linux**

```bash
export SENDER_EMAIL="your_email@gmail.com"
export SENDER_PASSWORD="your_16_char_app_password"
export RECIPIENT_EMAIL="your_email@gmail.com"
```

**Windows PowerShell**

```powershell
$env:SENDER_EMAIL="your_email@gmail.com"
$env:SENDER_PASSWORD="your_16_char_app_password"
$env:RECIPIENT_EMAIL="your_email@gmail.com"
```

Ensure `auto_monitor.py` reads these variables with Python's `os.environ` or `os.getenv`.

> **Security:** Never commit real email credentials, app passwords, or other secrets to GitHub.

### 2. Enable chaos mode and generate traffic

```bash
curl -X POST http://localhost:3001/chaos/error-spike/enable
```

**Bash-compatible terminals**

```bash
for i in {1..10}; do
  curl -s http://localhost:3001/api/checkout > /dev/null
done
```

**Windows PowerShell**

```powershell
1..10 | ForEach-Object {
    Invoke-WebRequest `
        -Uri http://localhost:3001/api/checkout `
        -Method GET `
        -SkipHttpErrorCheck | Out-Null
}
```

Adjust the HTTP method if your application defines the checkout endpoint differently.

### 3. Start automated monitoring

Activate the virtual environment, then run:

```bash
python auto_monitor.py
```

The monitor should query Prometheus, detect the configured anomaly, launch the AI investigation, and send an email when the required conditions and credentials are satisfied.

Example terminal output (your output will vary):

```text
Starting Automated Incident Monitoring Loop (Interval: 15s)...
[ALERT TRIGGERED] 500 Error rate detected: 0.6 req/sec
[AUTOMATION] Launching AI Agent Investigation...
[TOOL CALL] query_prometheus_instant({"promql": "http_requests_total{job=\"mock-service\", code=\"500\"}"})
--- GENERATED REPORT ---
Incident Investigation Report: Critical HTTP 500 errors detected on /api/checkout...
[EMAIL SENT] Incident report successfully sent.
```

Actual logs, metrics, reports, and email delivery depend on your implementation and runtime configuration.

### 4. Verify the results

- Inspect the relevant HTTP request metrics in Prometheus.
- Review the configured dashboards in Grafana.
- Check the generated incident report.
- Confirm that the alert email reaches the configured recipient.
- Verify that the investigation refers to observed telemetry rather than unsupported assumptions.

### 5. Disable chaos mode

```bash
curl -X POST http://localhost:3001/chaos/error-spike/disable
```

## 📄 Example incident report

The following is an illustrative example of a report that may be included in an automated email.

**Email subject:** 🚨 [CRITICAL ALERT] AI Incident Report: `/api/checkout` Error Spike  
**Recipient:** Configured administrator email address

### 🚨 Incident Investigation Report

**Report generated:** 2026-10-23 11:48:00 IST  
**Target application:** `mock-service`  
**Status:** CRITICAL

#### 1. Executive summary

A critical increase in HTTP 500 responses was detected on the `/api/checkout` route of `mock-service`.

#### 2. Evidence and observed metrics

- **Metric queried:** `http_requests_total{job="mock-service", code="500", route="/api/checkout"}`
- **Observed value:** 48 failure requests
- **Affected route/component:** `/api/checkout`

#### 3. Root-cause analysis

The sudden spike in HTTP 500 responses indicates backend execution failures. Observed latency increases of up to two seconds may correlate with event-loop blockage, unhandled exceptions, or slow dependencies. These are hypotheses; validate them against application logs and supporting metrics before treating them as confirmed root causes.

#### 4. Recommended remediation

- Inspect application logs for stack traces associated with `/api/checkout`.
- Verify database connection pool limits and dependent service response times.
- Review recent deployments and configuration changes.
- Monitor error rates and latency after remediation.

> **Note:** Metric values, timestamps, and incident details above are illustrative, not verified live observations.

## 🔒 Security best practices

- Never commit SMTP passwords, API credentials, or other secrets to source control.
- Store local credentials in environment variables or a dedicated secrets manager.
- Add `.env` files, virtual environments, generated reports, and other sensitive files to `.gitignore` as appropriate.
- Restrict access to local monitoring dashboards and application endpoints.
- Validate and authenticate operational endpoints before exposing them beyond a trusted development environment.
- Treat AI-generated root-cause explanations as hypotheses until corroborated by telemetry and logs.
- Avoid logging credentials or other sensitive information.
- Use least-privilege access for services and accounts wherever possible.

## 🧹 Stop the infrastructure

```bash
docker compose down
```

To stop the services and remove their Compose-managed volumes, run this only if you intend to delete the stored data:

```bash
docker compose down --volumes
```

> **Warning:** Removing volumes can permanently delete persisted data, depending on your Docker Compose configuration.

## 📌 Future enhancements

- Multi-service monitoring and incident correlation.
- Additional anomaly detection for latency, throughput, and resource utilization.
- Persistent incident history and report storage.
- Alert deduplication and incident severity classification.
- Integration with Slack, Microsoft Teams, or other notification platforms.
- Automated recovery workflows with approval controls.
- Unit and integration tests for MCP tools and investigation workflows.
