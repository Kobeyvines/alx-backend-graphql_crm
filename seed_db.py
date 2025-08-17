import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")
django.setup()

from crm.models import Customer, Product

def seed():
    Customer.objects.all().delete()
    Product.objects.all().delete()

    Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    Customer.objects.create(name="Bob", email="bob@example.com")

    Product.objects.create(name="Laptop", price=1200.00, stock=10)
    Product.objects.create(name="Phone", price=600.00, stock=15)

    print("Seed data inserted!")

if __name__ == "__main__":
    seed()
