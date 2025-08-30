#!/bin/bash

# Get current timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Execute Django command to delete inactive customers and capture the count
deleted_count=$(python3 manage.py shell <<EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

# Get customers with no orders in the last year
year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(
    order__isnull=True
) | Customer.objects.filter(
    order__created_at__lt=year_ago
)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log the results
echo "[$timestamp] Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt