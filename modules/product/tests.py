from django.test import TestCase
from django.utils import timezone
from decimal import Decimal

from .models import Product


class ProductModelTests(TestCase):
    def test_str_returns_name(self):
        p = Product.objects.create(
            name="Sample",
            barcode="12345",
            price=Decimal("9.99"),
            stock=10,
        )
        self.assertEqual(str(p), "Sample")

    def test_auto_timestamps_are_set(self):
        p = Product.objects.create(
            name="Timestamps",
            barcode="TS-001",
            price=Decimal("0.00"),
            stock=0,
        )
        self.assertIsNotNone(p.created_at)
        self.assertIsNotNone(p.updated_at)
        self.assertLessEqual(p.created_at, p.updated_at)

    def test_updated_at_changes_on_save(self):
        p = Product.objects.create(
            name="Update",
            barcode="UP-001",
            price=Decimal("1.00"),
            stock=1,
        )
        first_updated = p.updated_at
        p.price = Decimal("2.00")
        p.save()
        self.assertGreaterEqual(p.updated_at, first_updated)

    def test_field_max_lengths(self):
        name_field = Product._meta.get_field("name")
        barcode_field = Product._meta.get_field("barcode")
        self.assertEqual(name_field.max_length, 200)
        self.assertEqual(barcode_field.max_length, 100)

    def test_decimal_and_integer_fields(self):
        p = Product.objects.create(
            name="Numeric",
            barcode="NUM-001",
            price=Decimal("1234567.89"),
            stock=999,
        )
        self.assertEqual(p.price, Decimal("1234567.89"))
        self.assertEqual(p.stock, 999)
