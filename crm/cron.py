from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """
    Logs a heartbeat every 5 minutes and queries GraphQL hello field.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Always append heartbeat message
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

    # GraphQL hello check using gql
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql("{ hello }")
        result = client.execute(query)
        hello_val = result.get("hello", "No response")

        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL hello: {hello_val}\n")
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {e}\n")

def update_low_stock():
    """
    Runs GraphQL mutation to restock low-stock products and logs results.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        # GraphQL client setup
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)

        result = client.execute(mutation)
        updates = result.get("updateLowStockProducts", {})

        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - {updates.get('message', 'No message')}\n")
            for product in updates.get("updatedProducts", []):
                f.write(
                    f"  Product {product['name']} restocked, new stock: {product['stock']}\n"
                )
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - GraphQL mutation failed: {e}\n")