from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounts.models import Student, UbuUser
from catalog.models import Item
from catalog.services import create_item

from .models import BorrowItem, BorrowRequest, Cart, CartItem, Queue, ReturnItem, ReturnRequest
from .services import compute_due_date, compute_fine, expire_queues

RELEASE = date(2026, 11, 10)


class BorrowFixture(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            user=UbuUser.objects.create(email="s@ubu.ac.th"), student_id="66114540001", phone="0812345678",
        )
        self.paper = create_item(Item.ItemType.MATERIAL, name="กระดาษ", qty_total=20)
        self.hdmi = create_item(Item.ItemType.DURABLE_MATERIAL, name="HDMI", qty_total=5,
                                max_borrow_days=3, fine_rate_per_day=Decimal("10.00"))
        self.projector = create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-01",
                                     max_borrow_days=7, fine_rate_per_day=Decimal("50.00"))
        self.request = BorrowRequest.objects.create(student=self.student, status=BorrowRequest.Status.BORROWING)

    def borrow(self, item, qty=1, release=RELEASE):
        bi = BorrowItem(borrow_request=self.request, item=item, qty=qty)
        bi.due_date = compute_due_date(bi, release)
        bi.save()
        return bi


class DueDateTests(BorrowFixture):
    """ERD: กำหนดคืนรายชิ้น (UC-17)"""

    def test_due_date_uses_each_item_max_borrow_days(self):
        self.assertEqual(self.borrow(self.hdmi, 2).due_date, RELEASE + timedelta(days=3))
        self.assertEqual(self.borrow(self.projector).due_date, RELEASE + timedelta(days=7))

    def test_material_has_no_due_date(self):
        self.assertIsNone(self.borrow(self.paper, 5).due_date)

    def test_special_request_uses_custom_due_date_for_all_items(self):
        self.request.is_special = True
        self.request.custom_due_date = date(2026, 12, 1)
        self.request.save()
        self.assertEqual(self.borrow(self.hdmi).due_date, date(2026, 12, 1))
        self.assertEqual(self.borrow(self.projector).due_date, date(2026, 12, 1))

    def test_special_request_requires_date(self):
        with self.assertRaises(ValidationError):
            BorrowRequest(student=self.student, is_special=True).full_clean()

    def test_earliest_due_date_skips_fully_returned(self):
        hdmi = self.borrow(self.hdmi)            # 13 พ.ย.
        self.borrow(self.projector)              # 17 พ.ย.
        self.assertEqual(self.request.earliest_due_date, date(2026, 11, 13))
        rr = ReturnRequest.objects.create(borrow_request=self.request, status=ReturnRequest.Status.RETURNED)
        ReturnItem.objects.create(return_request=rr, borrow_item=hdmi, qty_returned=1)
        self.assertEqual(self.request.earliest_due_date, date(2026, 11, 17))


class FineTests(BorrowFixture):
    """ERD: ค่าปรับ = max(0, วันที่คืน − due_date) × fine_rate_per_day × qty_returned (UC-18)"""

    def test_on_time_no_fine(self):
        bi = self.borrow(self.projector)
        self.assertEqual(compute_fine(bi, bi.due_date, 1), Decimal("0.00"))
        self.assertEqual(compute_fine(bi, bi.due_date - timedelta(days=2), 1), Decimal("0.00"))

    def test_late_fine_multiplies_days_rate_qty(self):
        bi = self.borrow(self.hdmi, 3)
        self.assertEqual(compute_fine(bi, bi.due_date + timedelta(days=4), 2), Decimal("80.00"))  # 4 × 10 × 2

    def test_material_never_fined(self):
        bi = self.borrow(self.paper, 5)
        self.assertEqual(compute_fine(bi, RELEASE + timedelta(days=30), 5), Decimal("0.00"))

    def test_return_request_total_uses_sum_or_custom(self):
        """UC-36: custom_fine เป็น NULL → SUM(fine) · ตั้งค่าแล้ว → ใช้ค่านั้น (แก้เป็น 0 ได้)"""
        rr = ReturnRequest.objects.create(borrow_request=self.request)
        ReturnItem.objects.create(return_request=rr, borrow_item=self.borrow(self.hdmi), fine=Decimal("30"))
        ReturnItem.objects.create(return_request=rr, borrow_item=self.borrow(self.projector), fine=Decimal("100"))
        self.assertEqual(rr.total_fine, Decimal("130"))
        rr.custom_fine = Decimal("0")
        rr.save()
        self.assertEqual(rr.total_fine, Decimal("0"))
        self.assertEqual(self.request.total_fine, Decimal("0"))


class ItemTypeRuleTests(BorrowFixture):
    def test_equipment_qty_must_be_one_in_cart(self):
        cart = Cart.objects.create(student=self.student)
        with self.assertRaises(ValidationError):
            CartItem(cart=cart, item=self.projector, qty=2).full_clean()
        CartItem(cart=cart, item=self.hdmi, qty=2).full_clean()

    def test_equipment_qty_must_be_one_in_borrow(self):
        with self.assertRaises(ValidationError):
            BorrowItem(borrow_request=self.request, item=self.projector, qty=2).full_clean()

    def test_material_cannot_be_returned(self):
        rr = ReturnRequest.objects.create(borrow_request=self.request)
        with self.assertRaises(ValidationError):
            ReturnItem(return_request=rr, borrow_item=self.borrow(self.paper, 2), qty_returned=1).full_clean()

    def test_cannot_return_more_than_borrowed(self):
        rr = ReturnRequest.objects.create(borrow_request=self.request)
        with self.assertRaises(ValidationError):
            ReturnItem(return_request=rr, borrow_item=self.borrow(self.hdmi, 2), qty_returned=3).full_clean()

    def test_material_cannot_be_queued(self):
        with self.assertRaises(ValidationError):
            Queue(item=self.paper, student=self.student).full_clean()
        Queue(item=self.projector, student=self.student).full_clean()


class QueueExpiryTests(BorrowFixture):
    def test_notified_queue_expires_after_one_day(self):
        """UC-10: แจ้งเตือนแล้วไม่ยืนยันภายใน 1 วัน → EXPIRED"""
        now = timezone.now()
        old = Queue.objects.create(item=self.projector, student=self.student,
                                   status=Queue.Status.NOTIFIED, notified_at=now - timedelta(days=1, minutes=1))
        fresh = Queue.objects.create(item=self.hdmi, student=self.student,
                                     status=Queue.Status.NOTIFIED, notified_at=now - timedelta(hours=5))
        self.assertEqual(expire_queues(now), 1)
        old.refresh_from_db()
        fresh.refresh_from_db()
        self.assertEqual(old.status, Queue.Status.EXPIRED)
        self.assertEqual(fresh.status, Queue.Status.NOTIFIED)
