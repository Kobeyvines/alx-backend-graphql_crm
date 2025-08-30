from datetime import datetime
from celery import shared_task
import requests

LOG_FILE = "/tmp/crm_report_log.txt"

@shared_task
def generate_crm_report():
    """
    Generates a CRM report by querying the GraphQL endpoint
    and logs the result to /tmp/crm_report_log.txt
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # GraphQL endpoint
        url = "http://localhost:8000/graphql"
        query = """
        {
            totalCustomers
            totalOrders
            totalRevenue
        }
        """

        response = requests.post(url, json={"query": query})
        data = response.json().get("data", {})

        customers = data.get("totalCustomers", 0)
        orders = data.get("totalOrders", 0)
        revenue = data.get("totalRevenue", 0)

        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n")

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - Report generation failed: {e}\n")
