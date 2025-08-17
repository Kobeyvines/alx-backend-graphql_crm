import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
import re


from .models import Customer, Product, Order

# ObjectTypes
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")

        if phone and not re.match(r'^(\+?\d{10,15}|(\d{3}-\d{3}-\d{4}))$', phone):
            raise ValidationError("Invalid phone format")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully!")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customers):
        created = []
        errors = []

        with transaction.atomic():
            for data in customers:
                try:
                    name = data.get("name")
                    email = data.get("email")
                    phone = data.get("phone")

                    if Customer.objects.filter(email=email).exists():
                        errors.append(f"Email already exists: {email}")
                        continue

                    customer = Customer(name=name, email=email, phone=phone)
                    customer.full_clean()
                    customer.save()
                    created.append(customer)
                except ValidationError as e:
                    errors.append(str(e))

        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise ValidationError("Price must be positive")
        if stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")

        if not product_ids:
            raise ValidationError("At least one product is required")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise ValidationError("Invalid product IDs")

        order = Order.objects.create(customer=customer)
        order.products.set(products)
        order.calculate_total()

        return CreateOrder(order=order)


# Query + Mutation
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


# -------------------
# GraphQL Types
# -------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


# -------------------
# Utility Validators
# -------------------
def validate_phone(phone):
    if not phone:
        return True
    pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
    return re.match(pattern, phone)


# -------------------
# Create Customer
# -------------------
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []

        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists.")

        # Validate phone
        if input.phone and not validate_phone(input.phone):
            errors.append("Invalid phone format.")

        if errors:
            return CreateCustomer(customer=None, message="Failed to create customer", errors=errors)

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully", errors=None)


# -------------------
# Bulk Create Customers
# -------------------
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CreateCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, cust in enumerate(input):
                # Validate email uniqueness
                if Customer.objects.filter(email=cust.email).exists():
                    errors.append(f"Row {idx+1}: Email {cust.email} already exists.")
                    continue
                # Validate phone
                if cust.phone and not validate_phone(cust.phone):
                    errors.append(f"Row {idx+1}: Invalid phone format for {cust.phone}.")
                    continue

                customer = Customer.objects.create(
                    name=cust.name,
                    email=cust.email,
                    phone=cust.phone
                )
                created_customers.append(customer)

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# -------------------
# Create Product
# -------------------
class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False, default_value=0)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []

        if input.price <= 0:
            errors.append("Price must be positive.")
        if input.stock is not None and input.stock < 0:
            errors.append("Stock cannot be negative.")

        if errors:
            return CreateProduct(product=None, errors=errors)

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock or 0
        )
        return CreateProduct(product=product, errors=None)


# -------------------
# Create Order
# -------------------
class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []

        # Validate customer
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append(f"Invalid customer ID: {input.customer_id}")
            return CreateOrder(order=None, errors=errors)

        # Validate products
        products = Product.objects.filter(id__in=input.product_ids)
        if not products.exists():
            errors.append("No valid products found.")
        elif len(products) != len(input.product_ids):
            errors.append("Some product IDs are invalid.")

        if errors:
            return CreateOrder(order=None, errors=errors)

        # Create order
        order = Order.objects.create(
            customer=customer,
            order_date=input.order_date or timezone.now()
        )
        order.products.set(products)

        # Calculate total
        total_amount = sum([p.price for p in products])
        order.total_amount = total_amount
        order.save()

        return CreateOrder(order=order, errors=None)



# -------------------
# Root Mutation
# -------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

