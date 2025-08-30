import logging
from datetime import datetime
import requests

# Log file location
LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """
    Logs heartbeat every 5 minutes and optionally checks GraphQL hello query.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Append heartbeat message
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

    # Optional: Check GraphQL hello query
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            hello_val = data.get("data", {}).get("hello", "No response")
            with open(LOG_FILE, "a") as f:
                f.write(f"{timestamp} GraphQL hello: {hello_val}\n")
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {e}\n")
