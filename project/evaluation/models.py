"""M5 · evaluation — ERD: REVIEW (3NF: ผู้รีวิวและสิ่งของหาผ่าน BORROW_ITEM)"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from borrow.models import BorrowItem


class Review(models.Model):
    """ERD: REVIEW — รีวิวรายชิ้น 1 รายการยืมรีวิวได้ 1 ครั้ง (UC-14, UC-37)"""

    borrow_item = models.OneToOneField(
        BorrowItem, on_delete=models.CASCADE, related_name="review", verbose_name="รายการที่ยืม",
    )
    rating = models.PositiveSmallIntegerField(
        "คะแนนดาว", validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("ความคิดเห็น", blank=True)
    created_at = models.DateTimeField("วันที่รีวิว", auto_now_add=True)

    class Meta:
        db_table = "review"
        verbose_name = "รีวิว (REVIEW)"
        verbose_name_plural = "รีวิว (REVIEW)"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5), name="review_rating_1_to_5"),
        ]

    def __str__(self):
        return f"{self.rating}★ · {self.borrow_item.item}"

    @property
    def reviewer(self):
        return self.borrow_item.borrow_request.student

    @property
    def item(self):
        return self.borrow_item.item
