"""
M3 · borrow — ตะกร้า การยืม การคืน คิว และแจ้งชำรุด
ERD: CART, CART_ITEM, BORROW_REQUEST, BORROW_ITEM, RETURN_REQUEST, RETURN_ITEM, QUEUE, DAMAGE_REPORT
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Min, Sum

from accounts.models import Staff, Student
from catalog.models import Item

MONEY = dict(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])


def _check_equipment_qty(item, qty):
    """CART_ITEM / BORROW_ITEM ของครุภัณฑ์ต้องมี qty = 1 เสมอ (UC-03, UC-05)"""
    if item is not None and item.is_equipment and qty != 1:
        raise ValidationError({"qty": "ครุภัณฑ์ยืมได้ครั้งละ 1 ชิ้นเท่านั้น"})


def _check_returnable(item, label):
    if item is not None and not item.is_returnable:
        raise ValidationError({"item": f"{label}ใช้ได้เฉพาะวัสดุคงทนและครุภัณฑ์เท่านั้น"})


class Cart(models.Model):
    """ERD: CART — นักศึกษา 1 คน มีตะกร้า 1 ใบ"""

    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, db_column="user_id", related_name="cart", verbose_name="เจ้าของตะกร้า",
    )
    created_at = models.DateTimeField("วันที่สร้างตะกร้า", auto_now_add=True)
    updated_at = models.DateTimeField("วันที่แก้ไขล่าสุด", auto_now=True)

    class Meta:
        db_table = "cart"
        verbose_name = "ตะกร้า (CART)"
        verbose_name_plural = "ตะกร้า (CART)"

    def __str__(self):
        return f"ตะกร้าของ {self.student}"


class CartItem(models.Model):
    """ERD: CART_ITEM"""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="ตะกร้า")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="cart_items", verbose_name="สิ่งของ")
    qty = models.PositiveIntegerField("จำนวนที่ต้องการ", default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField("วันที่เพิ่มลงตะกร้า", auto_now_add=True)

    class Meta:
        db_table = "cart_item"
        verbose_name = "รายการในตะกร้า (CART_ITEM)"
        verbose_name_plural = "รายการในตะกร้า (CART_ITEM)"
        constraints = [models.UniqueConstraint(fields=["cart", "item"], name="cart_item_unique_item")]

    def __str__(self):
        return f"{self.item} × {self.qty}"

    def clean(self):
        _check_equipment_qty(self.item if self.item_id else None, self.qty)


class BorrowRequest(models.Model):
    """ERD: BORROW_REQUEST — ใบคำขอยืม"""

    class Status(models.TextChoices):
        PENDING = "PENDING", "รออนุมัติ"
        BORROWING = "BORROWING", "กำลังยืม"
        RETURN_PENDING = "RETURN_PENDING", "รอตรวจรับคืน"
        ISSUED = "ISSUED", "เบิกสำเร็จ"
        RETURNED = "RETURNED", "คืนสำเร็จ"
        REJECTED = "REJECTED", "ไม่อนุมัติ"
        CANCELLED = "CANCELLED", "ยกเลิกแล้ว"
        EXPIRED = "EXPIRED", "หมดอายุแล้ว"

    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, db_column="user_id", related_name="borrow_requests", verbose_name="ผู้ขอยืม",
    )
    approved_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="approved_requests", verbose_name="ผู้อนุมัติ",
    )
    use_date = models.DateField("วันที่เริ่มใช้งาน", null=True, blank=True)
    is_special = models.BooleanField("ขอยืมกรณีพิเศษ", default=False)
    custom_due_date = models.DateField("วันที่คืนกรณีพิเศษ", null=True, blank=True)
    status = models.CharField("สถานะ", max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField("วันที่ส่งคำขอ", auto_now_add=True)
    approved_at = models.DateTimeField("วันที่อนุมัติ", null=True, blank=True)
    reject_reason = models.TextField("เหตุผลที่ไม่อนุมัติ", blank=True)

    class Meta:
        db_table = "borrow_request"
        verbose_name = "คำขอยืม (BORROW_REQUEST)"
        verbose_name_plural = "คำขอยืม (BORROW_REQUEST)"
        ordering = ["-created_at"]

    def __str__(self):
        return f"คำขอ #{self.pk} · {self.student}"

    def clean(self):
        if self.is_special and not self.custom_due_date:
            raise ValidationError({"custom_due_date": "คำขอกรณีพิเศษต้องระบุวันที่คืน"})

    @property
    def total_fine(self):
        """ยอดค่าปรับรวมของใบยืม = SUM ยอดเรียกเก็บของทุกรอบคืน"""
        return sum((r.total_fine for r in self.return_requests.all()), Decimal("0.00"))

    @property
    def earliest_due_date(self):
        """กำหนดคืนบนการ์ดคำขอ (UC-09) = MIN(due_date) ของรายการที่ยังคืนไม่ครบ"""
        dates = [bi.due_date for bi in self.items.all() if bi.due_date and bi.qty_outstanding > 0]
        return min(dates) if dates else None


class BorrowItem(models.Model):
    """ERD: BORROW_ITEM — รายการสิ่งของในใบคำขอ กำหนดคืนรายชิ้น"""

    borrow_request = models.ForeignKey(
        BorrowRequest, on_delete=models.CASCADE, related_name="items", verbose_name="ใบคำขอ",
    )
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="borrow_items", verbose_name="สิ่งของ")
    qty = models.PositiveIntegerField("จำนวนที่ยืม/เบิก", default=1, validators=[MinValueValidator(1)])
    due_date = models.DateField("วันครบกำหนดคืน", null=True, blank=True)
    initial_photo = models.ImageField("รูปถ่ายสภาพของก่อนยืม", upload_to="borrow/initial/", blank=True)
    current_location = models.CharField("ที่ตั้งปัจจุบันที่แจ้งย้าย", max_length=200, blank=True)
    moved_at = models.DateTimeField("วันเวลาที่แจ้งย้ายล่าสุด", null=True, blank=True)

    class Meta:
        db_table = "borrow_item"
        verbose_name = "รายการยืม (BORROW_ITEM)"
        verbose_name_plural = "รายการยืม (BORROW_ITEM)"

    def __str__(self):
        return f"{self.item} × {self.qty} (คำขอ #{self.borrow_request_id})"

    def clean(self):
        _check_equipment_qty(self.item if self.item_id else None, self.qty)

    @property
    def qty_returned(self):
        """จำนวนที่ตรวจรับคืนสำเร็จแล้ว (นับเฉพาะรอบที่ RETURNED)"""
        return self.return_items.filter(
            return_request__status=ReturnRequest.Status.RETURNED,
        ).aggregate(s=Sum("qty_returned"))["s"] or 0

    @property
    def qty_outstanding(self):
        if not self.item.is_returnable:
            return 0
        return self.qty - self.qty_returned


class ReturnRequest(models.Model):
    """ERD: RETURN_REQUEST — ใบแจ้งคืน 1 รอบ (คืนบางส่วนได้)"""

    class Status(models.TextChoices):
        RETURN_PENDING = "RETURN_PENDING", "รอตรวจรับคืน"
        RETURNED = "RETURNED", "คืนสำเร็จ"
        REJECTED = "REJECTED", "ปฏิเสธการรับคืน"

    borrow_request = models.ForeignKey(
        BorrowRequest, on_delete=models.CASCADE, related_name="return_requests", verbose_name="ใบคำขอยืม",
    )
    inspected_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="inspected_returns", verbose_name="ผู้ตรวจรับคืน",
    )
    status = models.CharField("สถานะ", max_length=20, choices=Status.choices, default=Status.RETURN_PENDING)
    return_photo = models.ImageField("รูปถ่ายหลักฐานการส่งคืน", upload_to="borrow/return/", blank=True)
    custom_fine = models.DecimalField("ยอดค่าปรับที่เรียกเก็บจริง", null=True, blank=True, **MONEY)
    fine_paid = models.BooleanField("ชำระค่าปรับแล้ว", default=False)
    fine_reason = models.TextField("เหตุผลการปรับ/ลดหย่อน", blank=True)
    note = models.TextField("หมายเหตุการส่งคืน", blank=True)
    created_at = models.DateTimeField("วันที่แจ้งคืน", auto_now_add=True)
    returned_at = models.DateTimeField("วันที่ตรวจรับคืนสำเร็จ", null=True, blank=True)

    class Meta:
        db_table = "return_request"
        verbose_name = "ใบแจ้งคืน (RETURN_REQUEST)"
        verbose_name_plural = "ใบแจ้งคืน (RETURN_REQUEST)"
        ordering = ["-created_at"]

    def __str__(self):
        return f"แจ้งคืน #{self.pk} · คำขอ #{self.borrow_request_id}"

    @property
    def total_fine(self):
        """ยอดเรียกเก็บของรอบคืน (UC-36): custom_fine ถ้ามี ไม่อย่างนั้น SUM(RETURN_ITEM.fine)"""
        if self.custom_fine is not None:
            return self.custom_fine
        return self.items.aggregate(s=Sum("fine"))["s"] or Decimal("0.00")


class ReturnItem(models.Model):
    """ERD: RETURN_ITEM — รายการที่คืนในรอบนั้น"""

    class Condition(models.TextChoices):
        NORMAL = "NORMAL", "ปกติ"
        DAMAGED = "DAMAGED", "ชำรุด"
        LOST = "LOST", "สูญหาย"

    return_request = models.ForeignKey(
        ReturnRequest, on_delete=models.CASCADE, related_name="items", verbose_name="ใบแจ้งคืน",
    )
    borrow_item = models.ForeignKey(
        BorrowItem, on_delete=models.CASCADE, related_name="return_items", verbose_name="รายการยืมเดิม",
    )
    qty_returned = models.PositiveIntegerField("จำนวนที่คืนในรอบนี้", default=1, validators=[MinValueValidator(1)])
    condition_status = models.CharField("สภาพ", max_length=10, choices=Condition.choices, default=Condition.NORMAL)
    fine = models.DecimalField("ค่าปรับเกินกำหนด", default=Decimal("0.00"), **MONEY)
    lost_compensation = models.DecimalField("ค่าชดใช้กรณีสูญหาย", default=Decimal("0.00"), **MONEY)
    lost_paid = models.BooleanField("ชำระค่าชดใช้แล้ว", default=False)

    class Meta:
        db_table = "return_item"
        verbose_name = "รายการคืน (RETURN_ITEM)"
        verbose_name_plural = "รายการคืน (RETURN_ITEM)"

    def __str__(self):
        return f"{self.borrow_item.item} × {self.qty_returned} ({self.get_condition_status_display()})"

    def clean(self):
        if not self.borrow_item_id:
            return
        _check_returnable(self.borrow_item.item, "การคืน")
        if self.qty_returned > self.borrow_item.qty:
            raise ValidationError({"qty_returned": "จำนวนที่คืนมากกว่าจำนวนที่ยืม"})


class Queue(models.Model):
    """ERD: QUEUE — คิวจอง (เฉพาะวัสดุคงทน / ครุภัณฑ์รายชิ้น) UC-10"""

    class Status(models.TextChoices):
        WAITING = "WAITING", "รอคิว"
        NOTIFIED = "NOTIFIED", "แจ้งเตือนแล้ว รอยืนยัน"
        CONFIRMED = "CONFIRMED", "ยืนยันรับสิทธิ์แล้ว"
        EXPIRED = "EXPIRED", "หมดอายุ"
        CANCELLED = "CANCELLED", "ยกเลิก"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="queues", verbose_name="สิ่งของที่จองคิว")
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column="user_id", related_name="queues", verbose_name="ผู้จองคิว",
    )
    status = models.CharField("สถานะ", max_length=20, choices=Status.choices, default=Status.WAITING)
    joined_at = models.DateTimeField("เวลาที่เข้าคิว", auto_now_add=True)
    notified_at = models.DateTimeField("เวลาที่แจ้งเตือน", null=True, blank=True)
    confirmed_at = models.DateTimeField("เวลาที่ยืนยันรับสิทธิ์", null=True, blank=True)
    expired_at = models.DateTimeField("เวลาหมดอายุคิว", null=True, blank=True)

    class Meta:
        db_table = "queue"
        verbose_name = "คิวจอง (QUEUE)"
        verbose_name_plural = "คิวจอง (QUEUE)"
        ordering = ["joined_at"]

    def __str__(self):
        return f"คิว {self.item} · {self.student}"

    def clean(self):
        _check_returnable(self.item if self.item_id else None, "คิวจอง")


class DamageReport(models.Model):
    """ERD: DAMAGE_REPORT — นักศึกษาแจ้งอุปกรณ์ชำรุด (UC-38)"""

    class Status(models.TextChoices):
        PENDING = "PENDING", "รอดำเนินการ"
        IN_PROGRESS = "IN_PROGRESS", "กำลังดำเนินการ"
        RESOLVED = "RESOLVED", "แก้ไขแล้ว"

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column="user_id", related_name="damage_reports", verbose_name="ผู้แจ้ง",
    )
    item = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="damage_reports", verbose_name="สิ่งของในระบบที่ชำรุด",
    )
    item_name = models.CharField("ชื่อสิ่งของที่ชำรุด", max_length=200)
    origin_location = models.CharField("ที่ตั้งเดิมในคลัง", max_length=150, blank=True)
    location = models.CharField("สถานที่พบความชำรุด", max_length=200)
    symptom = models.TextField("อาการชำรุด")
    photo = models.ImageField("รูปถ่ายความเสียหาย", upload_to="damage/", blank=True)
    status = models.CharField("สถานะ", max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField("วันที่แจ้งชำรุด", auto_now_add=True)

    class Meta:
        db_table = "damage_report"
        verbose_name = "แจ้งชำรุด (DAMAGE_REPORT)"
        verbose_name_plural = "แจ้งชำรุด (DAMAGE_REPORT)"
        ordering = ["-created_at"]

    def __str__(self):
        return f"แจ้งชำรุด #{self.pk} · {self.item_name}"
