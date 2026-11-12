from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import DurableMaterial, Equipment, Item, Material
from .services import create_item


class CreateItemTests(TestCase):
    def test_material_total_participation(self):
        """ISA Total: สร้าง ITEM แล้วต้องมี subtype คู่กัน · qty_available = qty_total"""
        item = create_item(Item.ItemType.MATERIAL, name="กระดาษ", qty_total=10)
        self.assertIsInstance(item.detail, Material)
        self.assertEqual(item.detail.qty_available, 10)
        self.assertFalse(item.is_returnable)

    def test_durable(self):
        item = create_item(Item.ItemType.DURABLE_MATERIAL, name="สาย HDMI", qty_total=5,
                           max_borrow_days=7, fine_rate_per_day=Decimal("10"))
        self.assertIsInstance(item.detail, DurableMaterial)
        self.assertTrue(item.is_returnable)

    def test_equipment_is_one_piece(self):
        item = create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-01")
        self.assertIsInstance(item.detail, Equipment)
        self.assertEqual(item.detail.status, Equipment.Status.AVAILABLE)
        self.assertIn("UBU-EQ-001-01", str(item))

    def test_duplicate_asset_tag_rejected_and_rolled_back(self):
        create_item(Item.ItemType.EQUIPMENT, name="A", asset_tag="UBU-EQ-009-01")
        with self.assertRaises(ValidationError):
            create_item(Item.ItemType.EQUIPMENT, name="B", asset_tag="UBU-EQ-009-01")
        self.assertEqual(Item.objects.count(), 1)  # ITEM ของ B ต้องไม่ค้าง (atomic)

    def test_available_more_than_total_rejected(self):
        with self.assertRaises(ValidationError):
            create_item(Item.ItemType.MATERIAL, name="X", qty_total=5, qty_available=6)


class DisjointTests(TestCase):
    def test_subtype_must_match_item_type(self):
        """ISA Disjoint: ITEM ประเภท MATERIAL จะมีแถว EQUIPMENT ไม่ได้"""
        item = create_item(Item.ItemType.MATERIAL, name="กระดาษ", qty_total=1)
        with self.assertRaises(ValidationError):
            Equipment(item=item, asset_tag="UBU-EQ-X").full_clean()

    def test_db_constraint_qty_available_not_above_total(self):
        item = create_item(Item.ItemType.MATERIAL, name="ปากกา", qty_total=3)
        item.material.qty_available = 4
        with self.assertRaises(IntegrityError), transaction.atomic():
            item.material.save()
