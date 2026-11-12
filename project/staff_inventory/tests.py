"""M7 · staff_inventory — UC-20, UC-21, UC-22, UC-23"""
import io
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from accounts.tests_shell import make_staff, make_student
from borrow.models import BorrowItem, BorrowRequest
from catalog.models import Equipment, Item
from catalog.services import create_item

OVERVIEW = reverse("staff_inventory:item_overview")
ADD = reverse("staff_inventory:item_add")


def url(name, item):
    return reverse(f"staff_inventory:{name}", args=[item.pk])


def png(size=(10, 10)):
    buf = io.BytesIO()
    Image.new("RGB", size, "blue").save(buf, "PNG")
    return SimpleUploadedFile("x.png", buf.getvalue(), content_type="image/png")


class Fixture(TestCase):
    def setUp(self):
        self.staff = make_staff()
        self.client.force_login(self.staff)
        self.paper = create_item(Item.ItemType.MATERIAL, name="กระดาษ", qty_total=10)
        self.hdmi = create_item(Item.ItemType.DURABLE_MATERIAL, name="สาย HDMI", qty_total=5,
                                max_borrow_days=7, fine_rate_per_day=Decimal("10"))
        self.p1 = create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-01")
        self.p2 = create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-02",
                              status=Equipment.Status.BORROWED)

    def borrow_once(self, item, qty=1):
        student = make_student(f"b{BorrowItem.objects.count()}@ubu.ac.th", complete=False).ubu_user.student
        req = BorrowRequest.objects.create(student=student, status=BorrowRequest.Status.ISSUED)
        BorrowItem.objects.create(borrow_request=req, item=item, qty=qty)


class AccessTests(Fixture):
    def test_staff_only(self):
        self.client.force_login(make_student("st@ubu.ac.th"))
        for u in [OVERVIEW, ADD, url("item_edit", self.paper), url("equipment_status_update", self.p1),
                  url("consumable_delete", self.paper)]:
            self.assertEqual(self.client.get(u).status_code, 403, u)

    def test_menu_live_and_back_link_from_catalog(self):
        r = self.client.get(OVERVIEW)
        menu = {m["key"]: m for m in r.context["nav_menu"]}
        self.assertTrue(menu["item-overview"]["ready"] and menu["item-overview"]["active"])
        r = self.client.get(reverse("catalog:item_detail", args=[self.p1.pk]))
        self.assertEqual(r.context["back_url"], OVERVIEW)


class OverviewTests(Fixture):
    """UC-21"""

    def rows(self, qs=""):
        return [i.pk for i in self.client.get(OVERVIEW + qs).context["page"]]

    def test_rows_and_equipment_shows_dash(self):
        r = self.client.get(OVERVIEW)
        self.assertEqual(len(r.context["page"]), 4)
        self.assertContains(r, "UBU-EQ-001-01")
        self.assertContains(r, "10</strong>/10")
        self.assertContains(r, "กำลังถูกยืม")

    def test_search_type_status(self):
        self.assertEqual(self.rows("?q=001-02"), [self.p2.pk])
        self.assertEqual(set(self.rows("?type=EQUIPMENT")), {self.p1.pk, self.p2.pk})
        self.assertEqual(self.rows("?status=empty"), [self.p2.pk])
        Equipment.objects.filter(pk=self.p1.pk).update(status=Equipment.Status.RETIRED)
        self.assertEqual(self.rows("?status=retired"), [self.p1.pk])
        self.assertIn(self.p1.pk, self.rows())  # เจ้าหน้าที่เห็นของที่ปลดระวางด้วย

    def test_empty(self):
        Item.objects.all().delete()
        self.assertContains(self.client.get(OVERVIEW), "ยังไม่มีสิ่งของในคลัง")


class AddItemTests(Fixture):
    """UC-20 เพิ่ม"""

    def post(self, **data):
        base = {"name": "ของใหม่", "unit": "ชิ้น", "location": "ตู้ A", "purchase_price": "100",
                "description": "", "max_borrow_days": "7", "fine_rate_per_day": "5"}
        return self.client.post(ADD, base | data)

    def test_add_material(self):
        r = self.post(item_type="MATERIAL", name="ปากกา", qty_total="20")
        self.assertRedirects(r, OVERVIEW)
        item = Item.objects.get(name="ปากกา")
        self.assertEqual((item.material.qty_total, item.material.qty_available), (20, 20))
        self.assertEqual(item.base_status, Item.BaseStatus.AVAILABLE)

    def test_add_one_equipment_piece(self):
        """เพิ่มครุภัณฑ์ได้ครั้งละ 1 ชิ้น (ผู้ใช้เลือก) · มีช่องรหัสช่องเดียว"""
        r = self.client.get(ADD)
        self.assertContains(r, 'name="asset_tag"', count=1)
        r = self.client.post(ADD, {"item_type": "EQUIPMENT", "name": "กล้อง", "unit": "ตัว", "purchase_price": "30000",
                                   "max_borrow_days": "3", "fine_rate_per_day": "150", "asset_tag": "UBU-EQ-003-01"})
        self.assertRedirects(r, OVERVIEW)
        cam = Item.objects.get(name="กล้อง")
        self.assertEqual((cam.equipment.asset_tag, cam.equipment.max_borrow_days, cam.equipment.status),
                         ("UBU-EQ-003-01", 3, Equipment.Status.AVAILABLE))

    def test_tag_errors(self):
        before = Item.objects.count()
        self.assertContains(self.post(item_type="EQUIPMENT", asset_tag="UBU-EQ-001-01"), "มีในระบบแล้ว: UBU-EQ-001-01")
        self.assertContains(self.post(item_type="EQUIPMENT", asset_tag="  "), "กรุณากรอกรหัสครุภัณฑ์")
        self.assertContains(self.post(item_type="EQUIPMENT", asset_tag=["UBU-EQ-009-01", "UBU-EQ-009-02"]),
                            "เพิ่มครุภัณฑ์ได้ครั้งละ 1 ชิ้น")
        self.assertEqual(Item.objects.count(), before)

    def test_required_fields_by_type(self):
        r = self.post(item_type="MATERIAL", qty_total="", name="")
        self.assertIn("qty_total", r.context["form"].errors)
        self.assertIn("name", r.context["form"].errors)

    @override_settings(MEDIA_ROOT="/tmp/yuemdee-test-media")
    def test_image_upload_and_size_limit(self):
        r = self.post(item_type="MATERIAL", name="มีรูป", qty_total="1", image=png())
        self.assertRedirects(r, OVERVIEW)
        self.assertTrue(Item.objects.get(name="มีรูป").image)
        big = SimpleUploadedFile("big.png", png().read() + b"0" * (5 * 1024 * 1024 + 1), content_type="image/png")
        r = self.post(item_type="MATERIAL", name="รูปใหญ่", qty_total="1", image=big)
        self.assertContains(r, "ไม่เกิน 5 MB")


class EditItemTests(Fixture):
    """UC-20 แก้ไข"""

    def test_edit_equipment_only_this_piece_no_tag_field(self):
        """ตัดสินใจ M7 ข้อ 4: แก้เฉพาะชิ้นนี้"""
        r = self.client.get(url("item_edit", self.p1))
        self.assertNotContains(r, 'name="asset_tag"')
        r = self.client.post(url("item_edit", self.p1), {"name": "โปรเจกเตอร์ Epson", "unit": "เครื่อง", "purchase_price": "1",
                                                         "max_borrow_days": "10", "fine_rate_per_day": "50",
                                                         "item_type": "MATERIAL"})  # ส่งประเภทมาก็ไม่เปลี่ยน
        self.assertRedirects(r, OVERVIEW)
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.assertEqual((self.p1.name, self.p1.item_type, self.p1.equipment.max_borrow_days),
                         ("โปรเจกเตอร์ Epson", Item.ItemType.EQUIPMENT, 10))
        self.assertEqual(self.p1.equipment.asset_tag, "UBU-EQ-001-01")
        self.assertEqual(self.p2.name, "โปรเจกเตอร์")

    def test_qty_total_shifts_available_and_never_negative(self):
        """ตัดสินใจ M7 ข้อ 5"""
        self.hdmi.durablematerial.qty_available = 2  # ยืมไป 3
        self.hdmi.durablematerial.save()
        data = {"name": "สาย HDMI", "unit": "เส้น", "purchase_price": "0", "max_borrow_days": "7", "fine_rate_per_day": "10"}
        self.client.post(url("item_edit", self.hdmi), data | {"qty_total": "8"})
        self.hdmi.durablematerial.refresh_from_db()
        self.assertEqual((self.hdmi.durablematerial.qty_total, self.hdmi.durablematerial.qty_available), (8, 5))
        r = self.client.post(url("item_edit", self.hdmi), data | {"qty_total": "2"})
        self.assertContains(r, "ต้องไม่น้อยกว่า 3")
        self.hdmi.durablematerial.refresh_from_db()
        self.assertEqual(self.hdmi.durablematerial.qty_total, 8)


class StatusTests(Fixture):
    """UC-23"""

    def test_single_requires_note_except_retired(self):
        r = self.client.post(url("equipment_status_update", self.p1), {"status": "DAMAGED", "note": ""})
        self.assertIn("note", r.context["form"].errors)
        r = self.client.post(url("equipment_status_update", self.p1), {"status": "DAMAGED", "note": "เลนส์แตก"})
        self.assertRedirects(r, OVERVIEW)
        self.p1.equipment.refresh_from_db()
        self.assertEqual((self.p1.equipment.status, self.p1.equipment.note), ("DAMAGED", "เลนส์แตก"))
        self.client.post(url("equipment_status_update", self.p1), {"status": "RETIRED"})
        self.p1.equipment.refresh_from_db()
        self.assertEqual(self.p1.equipment.status, "RETIRED")

    def test_cannot_change_borrowed_or_pick_system_statuses(self):
        r = self.client.get(url("equipment_status_update", self.p2))
        self.assertContains(r, "กำลังถูกยืมอยู่")
        self.client.post(url("equipment_status_update", self.p2), {"status": "AVAILABLE", "note": "x"})
        self.p2.equipment.refresh_from_db()
        self.assertEqual(self.p2.equipment.status, "BORROWED")
        r = self.client.post(url("equipment_status_update", self.p1), {"status": "BORROWED", "note": "x"})
        self.assertIn("status", r.context["form"].errors)

    def test_durable_choices(self):
        """ตัดสินใจ M7 ข้อ 3"""
        r = self.client.get(url("equipment_status_update", self.hdmi))
        self.assertNotContains(r, "ปลดระวาง")
        self.client.post(url("equipment_status_update", self.hdmi), {"status": "INACTIVE"})
        self.hdmi.refresh_from_db()
        self.assertEqual(self.hdmi.base_status, Item.BaseStatus.INACTIVE)

    def test_material_has_no_status_page(self):
        self.assertRedirects(self.client.get(url("equipment_status_update", self.paper)), OVERVIEW)

    def test_bulk_skips_borrowed_and_non_equipment(self):
        """ตัดสินใจ M7 ข้อ 7"""
        ids = f"{self.p1.pk},{self.p2.pk},{self.paper.pk}"
        r = self.client.post(reverse("staff_inventory:bulk_status_update"), {"ids": ids, "status": "MAINTENANCE"}, follow=True)
        self.assertContains(r, "เปลี่ยนสถานะแล้ว 1 ชิ้น")
        self.assertContains(r, "ข้าม 1 ชิ้นที่กำลังถูกยืม: UBU-EQ-001-02")
        self.p1.equipment.refresh_from_db()
        self.p2.equipment.refresh_from_db()
        self.assertEqual((self.p1.equipment.status, self.p2.equipment.status), ("MAINTENANCE", "BORROWED"))


class DeleteTests(Fixture):
    """UC-22 + ตัดสินใจ M7 ข้อ 2"""

    def test_delete_unused_material(self):
        r = self.client.post(url("consumable_delete", self.paper))
        self.assertRedirects(r, OVERVIEW)
        self.assertFalse(Item.objects.filter(pk=self.paper.pk).exists())

    def test_cannot_delete_equipment_or_durable(self):
        for item in [self.p1, self.hdmi]:
            self.client.post(url("consumable_delete", item))
            self.assertTrue(Item.objects.filter(pk=item.pk).exists())

    def test_used_material_cannot_be_deleted_but_can_be_deactivated(self):
        self.borrow_once(self.paper)
        r = self.client.get(url("consumable_delete", self.paper))
        self.assertContains(r, "เคยถูกเบิกแล้ว")
        self.client.post(url("consumable_delete", self.paper))
        self.assertTrue(Item.objects.filter(pk=self.paper.pk).exists())
        self.client.post(url("toggle_active", self.paper), {"active": "0"})
        self.paper.refresh_from_db()
        self.assertEqual(self.paper.base_status, Item.BaseStatus.INACTIVE)
        # นักศึกษามองไม่เห็นของที่ปิดใช้งาน
        self.client.force_login(make_student("v@ubu.ac.th"))
        self.assertEqual(self.client.get(reverse("catalog:item_detail", args=[self.paper.pk])).status_code, 404)

    def test_bulk_delete_reports_kept(self):
        pen = create_item(Item.ItemType.MATERIAL, name="ปากกา", qty_total=1)
        self.borrow_once(self.paper)
        r = self.client.post(reverse("staff_inventory:bulk_delete"),
                             {"ids": f"{pen.pk},{self.paper.pk},{self.p1.pk}"}, follow=True)
        self.assertContains(r, "ลบแล้ว 1 รายการ")
        self.assertContains(r, "ลบไม่ได้ 2 รายการ")
        self.assertFalse(Item.objects.filter(pk=pen.pk).exists())
