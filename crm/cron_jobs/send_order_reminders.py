#!/usr/bin/env python3
import sys
import logging
from datetime import datetime, timedelta

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def main():
    # GraphQL endpoint
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Calculate date cutoff (last 7 days)
    cutoff_date = (datetime.now() - timedelta(days=7)).date().isoformat()

    # GraphQL query
    query = gql(
        """
        query GetRecentOrders($cutoff: Date!) {
            orders(orderDate_Gte: $cutoff, status: "PENDING") {
                id
                customer {
                    email
                }
            }
        }
        """
    )

    # Execute query
    params = {"cutoff": cutoff_date}
    try:
        result = client.execute(query, variable_values=params)
        orders = result.get("orders", [])
        for order in orders:
            logging.info(f"Order ID: {order['id']} | Customer Email: {order['customer']['email']}")
    except Exception as e:
        logging.error(f"Error fetching orders: {e}")
        sys.exit(1)

    print("Order reminders processed!")

if __name__ == "__main__":
    main()
