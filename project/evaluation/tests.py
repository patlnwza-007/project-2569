from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import Student, UbuUser
from borrow.models import BorrowItem, BorrowRequest
from catalog.models import Item
from catalog.services import create_item

from .models import Review


class ReviewTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(user=UbuUser.objects.create(email="r@ubu.ac.th"))
        item = create_item(Item.ItemType.EQUIPMENT, name="กล้อง", asset_tag="UBU-EQ-003-01")
        req = BorrowRequest.objects.create(student=self.student)
        self.bi = BorrowItem.objects.create(borrow_request=req, item=item)

    def test_reviewer_and_item_derived_from_borrow_item(self):
        """ERD REVIEW แบบ 3NF: ผู้รีวิว/สิ่งของหาผ่าน BORROW_ITEM"""
        r = Review.objects.create(borrow_item=self.bi, rating=5)
        self.assertEqual(r.reviewer, self.student)
        self.assertEqual(r.item, self.bi.item)

    def test_one_review_per_borrow_item(self):
        Review.objects.create(borrow_item=self.bi, rating=4)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(borrow_item=self.bi, rating=3)

    def test_rating_1_to_5(self):
        with self.assertRaises(ValidationError):
            Review(borrow_item=self.bi, rating=6).full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(borrow_item=self.bi, rating=0)
