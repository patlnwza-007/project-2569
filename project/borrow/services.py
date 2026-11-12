"""
กำหนดคืนและค่าปรับรายชิ้น (ERD หัวข้อ "กำหนดคืนและค่าปรับรายชิ้น")
ฟังก์ชันล้วน ทดสอบได้โดยไม่ต้องมีหน้าจอ · ใช้ตอน UC-17 (ปล่อยของ) และ UC-18 (ตรวจรับคืน)
"""
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import Queue

QUEUE_CONFIRM_WINDOW = timedelta(days=1)


def compute_due_date(borrow_item, release_date):
    """UC-17: วันครบกำหนดคืนของ BORROW_ITEM

    วัสดุสิ้นเปลือง → None · คำขอกรณีพิเศษ → custom_due_date · อื่น ๆ → วันปล่อยของ + max_borrow_days
    """
    item = borrow_item.item
    if not item.is_returnable:
        return None
    request = borrow_item.borrow_request
    if request.is_special and request.custom_due_date:
        return request.custom_due_date
    return release_date + timedelta(days=item.detail.max_borrow_days)


def compute_fine(borrow_item, return_date, qty_returned):
    """UC-18: ค่าปรับ = max(0, วันที่คืน − due_date) × fine_rate_per_day × qty_returned"""
    if borrow_item.due_date is None:
        return Decimal("0.00")
    days_late = max(0, (return_date - borrow_item.due_date).days)
    rate = borrow_item.item.detail.fine_rate_per_day
    return (Decimal(days_late) * rate * qty_returned).quantize(Decimal("0.01"))


def expire_queues(now=None):
    """UC-10: คิวที่แจ้งเตือนแล้วแต่ไม่ยืนยันภายใน 1 วัน → EXPIRED · คืนจำนวนคิวที่หมดอายุ"""
    now = now or timezone.now()
    return Queue.objects.filter(
        status=Queue.Status.NOTIFIED, notified_at__lte=now - QUEUE_CONFIRM_WINDOW,
    ).update(status=Queue.Status.EXPIRED, expired_at=now)
