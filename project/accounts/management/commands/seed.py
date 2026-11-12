"""
python manage.py seed — สร้างข้อมูลตัวอย่างสำหรับพัฒนา (รันซ้ำได้ ไม่สร้างซ้ำ)

- นักศึกษา 5 คน (s001–s005@ubu.ac.th), เจ้าหน้าที่ 2 คน (staff1–staff2@ubu.ac.th)
- สิ่งของ 3 ประเภท ประเภทละ 5 รายการ (ครุภัณฑ์ 5 ชิ้น = 3 รุ่น)
- คำขอยืม 1 ใบในสถานะ BORROWING (เพื่อดูข้อมูลยืม-คืนใน /admin/)

บัญชีตัวอย่างใช้รหัสผ่านจาก env SEED_PASSWORD (ค่าเริ่มต้นอยู่ใน DEFAULT_DEV_PASSWORD)
มีไว้ login ทดสอบระหว่างยังไม่เชื่อม SSO เท่านั้น — สร้างได้เฉพาะตอน DEBUG=True
"""
import os
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import Staff, Student, UbuUser
from borrow.models import BorrowItem, BorrowRequest
from borrow.services import compute_due_date
from catalog.models import Equipment, Item
from catalog.services import create_item

DEFAULT_DEV_PASSWORD = "yuemdee-dev-1234"

STUDENTS = [
    ("s001@ubu.ac.th", "สมชาย ใจดี", "66114540001", "0812345601"),
    ("s002@ubu.ac.th", "สมหญิง รักเรียน", "66114540002", "0812345602"),
    ("s003@ubu.ac.th", "ณัฐพล ขยันยิ่ง", "66114540003", "0812345603"),
    ("s004@ubu.ac.th", "กมลวรรณ ศรีสุข", "66114540004", "0812345604"),
    ("s005@ubu.ac.th", "ธนากร มีสุข", None, ""),  # ยังไม่กรอกข้อมูล onboarding (ทดสอบ UC-06 ส่งคำขอไม่ได้)
]
STAFF = [
    ("staff1@ubu.ac.th", "วิชัย เจ้าหน้าที่"),
    ("staff2@ubu.ac.th", "อรุณี ผู้ดูแลคลัง"),
]
MATERIALS = [
    ("กระดาษ A4 80 แกรม", "รีม", 50),
    ("ปากกาไวท์บอร์ด", "ด้าม", 40),
    ("เทปกาวสองหน้า", "ม้วน", 30),
    ("แบตเตอรี่ AA", "ก้อน", 60),
    ("สมุดบันทึก", "เล่ม", 25),
]
DURABLES = [
    ("สาย HDMI 5 เมตร", "เส้น", 10, 7, "10.00"),
    ("ปลั๊กพ่วง 5 ช่อง", "อัน", 8, 7, "10.00"),
    ("ขาตั้งกล้อง", "อัน", 4, 3, "20.00"),
    ("ไมโครโฟนไร้สาย", "ชุด", 6, 3, "20.00"),
    ("เครื่องคิดเลขวิทยาศาสตร์", "เครื่อง", 15, 14, "5.00"),
]
EQUIPMENT = [  # (ชื่อรุ่น, asset_tag, ราคา, วันยืมสูงสุด, ค่าปรับ/วัน)
    ("โปรเจกเตอร์ Epson", "UBU-EQ-001-01", "18500.00", 7, "50.00"),
    ("โปรเจกเตอร์ Epson", "UBU-EQ-001-02", "18500.00", 7, "50.00"),
    ("โน้ตบุ๊ก Dell Latitude", "UBU-EQ-002-01", "28900.00", 7, "100.00"),
    ("โน้ตบุ๊ก Dell Latitude", "UBU-EQ-002-02", "28900.00", 7, "100.00"),
    ("กล้อง DSLR Canon", "UBU-EQ-003-01", "32000.00", 3, "150.00"),
]


class Command(BaseCommand):
    help = "สร้างข้อมูลตัวอย่าง YuemDee สำหรับพัฒนา"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed ใช้ได้เฉพาะตอน DEBUG=True")
        password = os.environ.get("SEED_PASSWORD", DEFAULT_DEV_PASSWORD)
        with transaction.atomic():
            students = [self._student(*row, password) for row in STUDENTS]
            staff = [self._staff(*row, password) for row in STAFF]
            self._items()
            self._sample_borrow(students[0], staff[0])
        self.stdout.write(self.style.SUCCESS(
            f"seed เสร็จ: นักศึกษา {Student.objects.count()} · เจ้าหน้าที่ {Staff.objects.count()} · "
            f"สิ่งของ {Item.objects.count()} · คำขอยืม {BorrowRequest.objects.count()}"
        ))

    def _auth_user(self, email, name, password):
        User = get_user_model()
        user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name})
        if created:
            user.set_password(password)
            user.save()
        return user

    def _ubu_user(self, email, name, password):
        ubu, _ = UbuUser.objects.get_or_create(
            email=email,
            defaults={"name": name, "auth_user": self._auth_user(email, name, password), "first_login": timezone.now()},
        )
        return ubu

    def _student(self, email, name, student_id, phone, password):
        student, _ = Student.objects.get_or_create(
            user=self._ubu_user(email, name, password), defaults={"student_id": student_id, "phone": phone},
        )
        return student

    def _staff(self, email, name, password):
        staff, _ = Staff.objects.get_or_create(user=self._ubu_user(email, name, password))
        return staff

    def _items(self):
        for name, unit, qty in MATERIALS:
            if not Item.objects.filter(name=name, item_type=Item.ItemType.MATERIAL).exists():
                create_item(Item.ItemType.MATERIAL, name=name, unit=unit, location="คลังวัสดุ ชั้น 1", qty_total=qty)
        for name, unit, qty, days, rate in DURABLES:
            if not Item.objects.filter(name=name, item_type=Item.ItemType.DURABLE_MATERIAL).exists():
                create_item(
                    Item.ItemType.DURABLE_MATERIAL, name=name, unit=unit, location="คลังวัสดุ ชั้น 2",
                    qty_total=qty, max_borrow_days=days, fine_rate_per_day=Decimal(rate),
                )
        for name, tag, price, days, rate in EQUIPMENT:
            if not Equipment.objects.filter(asset_tag=tag).exists():
                create_item(
                    Item.ItemType.EQUIPMENT, name=name, unit="เครื่อง", location="ห้องครุภัณฑ์ EN6-101",
                    purchase_price=Decimal(price), asset_tag=tag, max_borrow_days=days,
                    fine_rate_per_day=Decimal(rate),
                )

    def _sample_borrow(self, student, staff):
        """คำขอที่ปล่อยของไปแล้ว: โปรเจกเตอร์ 1 เครื่อง + สาย HDMI 2 เส้น + กระดาษ 1 รีม"""
        if BorrowRequest.objects.filter(student=student).exists():
            return
        released = timezone.localdate() - timedelta(days=3)
        req = BorrowRequest.objects.create(
            student=student, approved_by=staff, use_date=released,
            status=BorrowRequest.Status.BORROWING, approved_at=timezone.now() - timedelta(days=3),
        )
        projector = Item.objects.get(equipment__asset_tag="UBU-EQ-001-01")
        hdmi = Item.objects.get(name="สาย HDMI 5 เมตร")
        paper = Item.objects.get(name="กระดาษ A4 80 แกรม")
        for item, qty in [(projector, 1), (hdmi, 2), (paper, 1)]:
            bi = BorrowItem(borrow_request=req, item=item, qty=qty, current_location="ตึก EN6 ห้อง EN6-204")
            bi.due_date = compute_due_date(bi, released)
            bi.full_clean()
            bi.save()
            if item.is_equipment:
                item.equipment.status = Equipment.Status.BORROWED
                item.equipment.save(update_fields=["status"])
            else:
                detail = item.detail
                detail.qty_available -= qty
                detail.save(update_fields=["qty_available"])
