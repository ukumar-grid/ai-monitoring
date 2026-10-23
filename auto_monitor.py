import time
import httpx
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from agent import run_investigation

PROMETHEUS_URL = "http://localhost:9090"
CHECK_INTERVAL_SECONDS = 15

# Email Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # Using SSL port for reliable connections
SENDER_EMAIL = "your@gmail.com"
SENDER_PASSWORD = "**** **** **** ****"  # Replace with 16-char App Password (no spaces)
RECIPIENT_EMAIL = "your@gmail.com"


def send_email_alert(subject: str, report_markdown: str):
    """Sends the generated AI incident report to your inbox."""
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(report_markdown, "plain"))

        # SSL connection on port 465 avoids STARTTLS connection drops
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            
        print(f"\n[EMAIL SENT] Incident report successfully sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"\n[EMAIL ERROR] Failed to send email alert: {e}")


def check_for_anomalies() -> bool:
    """Queries Prometheus to check if HTTP 500 error rates exceed 0."""
    promql = 'sum(rate(http_requests_total{code="500"}[1m]))'
    try:
        response = httpx.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": promql}, timeout=5.0)
        data = response.json()
        results = data.get("data", {}).get("result", [])
        if results:
            val = float(results[0]["value"][1])
            if val > 0:
                print(f"\n[ALERT TRIGGERED] 500 Error rate detected: {val} req/sec")
                return True
    except Exception as e:
        print(f"[MONITORING ERROR] {e}")
    return False


def start_automated_loop():
    print(f"Starting Automated Incident Monitoring Loop (Interval: {CHECK_INTERVAL_SECONDS}s)...")
    try:
        while True:
            if check_for_anomalies():
                print("[AUTOMATION] Launching AI Agent Investigation...")
                report = asyncio.run(
                    run_investigation(
                        "An automatic alert fired for HTTP 500 errors! Query instant and range metrics to generate a full incident report."
                    )
                )

                print("\n--- GENERATED REPORT ---")
                print(report)

                send_email_alert("🚨 [CRITICAL ALERT] AI Incident Report: /api/checkout Error Spike", report)

                print("\n[PAUSING] Sleeping 60s to avoid duplicate reports...")
                time.sleep(60)
            else:
                print(".", end="", flush=True)
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nAutomated monitoring stopped.")


if __name__ == "__main__":
    start_automated_loop()