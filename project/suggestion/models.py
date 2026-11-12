"""M4 · suggestion — ERD: SUGGESTION, PURCHASE_PLAN"""
from django.db import models

from accounts.models import Staff, Student


class Suggestion(models.Model):
    """ERD: SUGGESTION — นักศึกษาเสนอแนะสิ่งของใหม่ (UC-12)"""

    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "ส่งแล้ว"
        ACKNOWLEDGED = "ACKNOWLEDGED", "รับทราบแล้ว"
        REJECTED = "REJECTED", "ไม่อนุมัติ"
        PURCHASE_PLAN = "PURCHASE_PLAN", "เข้าแผนจัดซื้อ"

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column="user_id", related_name="suggestions", verbose_name="ผู้เสนอแนะ",
    )
    name = models.CharField("ชื่อสิ่งของที่เสนอ", max_length=200)
    detail = models.TextField("รายละเอียด/เหตุผล", blank=True)
    status = models.CharField("สถานะ", max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    created_at = models.DateTimeField("วันที่เสนอแนะ", auto_now_add=True)

    class Meta:
        db_table = "suggestion"
        verbose_name = "ข้อเสนอแนะ (SUGGESTION)"
        verbose_name_plural = "ข้อเสนอแนะ (SUGGESTION)"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class PurchasePlan(models.Model):
    """ERD: PURCHASE_PLAN — แผนจัดซื้อ (UC-28, UC-29) · มาจากข้อเสนอแนะหรือเพิ่มเองก็ได้"""

    suggestion = models.OneToOneField(
        Suggestion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="purchase_plan", verbose_name="ข้อเสนอแนะ",
    )
    name = models.CharField("ชื่อสิ่งของที่จะจัดซื้อ", max_length=200)
    detail = models.TextField("รายละเอียดการจัดซื้อ", blank=True)
    created_by = models.ForeignKey(
        Staff, on_delete=models.PROTECT, related_name="purchase_plans", verbose_name="ผู้บันทึก",
    )
    created_at = models.DateTimeField("วันที่บันทึก", auto_now_add=True)

    class Meta:
        db_table = "purchase_plan"
        verbose_name = "แผนจัดซื้อ (PURCHASE_PLAN)"
        verbose_name_plural = "แผนจัดซื้อ (PURCHASE_PLAN)"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
