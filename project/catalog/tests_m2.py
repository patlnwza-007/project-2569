"""M2 · catalog — UC-01, UC-02, UC-03, UC-37"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.tests_shell import make_staff, make_student
from borrow.models import BorrowItem, BorrowRequest
from evaluation.models import Review

from .models import Equipment, Item
from .selectors import AVAILABLE, EMPTY, UNAVAILABLE, student_items
from .services import create_item

LIST = reverse("catalog:item_list")


def detail(item, qs=""):
    return reverse("catalog:item_detail", args=[item.pk]) + qs


class CatalogFixture(TestCase):
    def setUp(self):
        self.student = make_student()
        self.client.force_login(self.student)
        self.paper = create_item(Item.ItemType.MATERIAL, name="กระดาษ A4", qty_total=10)
        self.pen = create_item(Item.ItemType.MATERIAL, name="ปากกา", qty_total=5, qty_available=0)
        self.hdmi = create_item(Item.ItemType.DURABLE_MATERIAL, name="สาย HDMI", qty_total=4,
                                max_borrow_days=7, fine_rate_per_day=Decimal("10"))
        self.proj = create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-01",
                                max_borrow_days=7, purchase_price=Decimal("18500"))
        self.proj_out = create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-02",
                                    status=Equipment.Status.BORROWED)
        self.cam_broken = create_item(Item.ItemType.EQUIPMENT, name="กล้อง", asset_tag="UBU-EQ-003-01",
                                      status=Equipment.Status.MAINTENANCE)
        self.lost = create_item(Item.ItemType.EQUIPMENT, name="ไมค์หาย", asset_tag="UBU-EQ-009-01",
                                status=Equipment.Status.LOST)
        self.retired = create_item(Item.ItemType.MATERIAL, name="ของปลดระวาง", qty_total=1,
                                   base_status=Item.BaseStatus.RETIRED)

    def keys(self, r):
        return [i.pk for i in r.context["page"]]


class AvailabilityTests(CatalogFixture):
    """สูตรสถานะ (M2 mapping หัวข้อ 2)"""

    def test_status_per_item(self):
        got = {i.pk: i.availability for i in student_items()}
        self.assertEqual(got[self.paper.pk], AVAILABLE)
        self.assertEqual(got[self.pen.pk], EMPTY)
        self.assertEqual(got[self.hdmi.pk], AVAILABLE)
        self.assertEqual(got[self.proj.pk], AVAILABLE)
        self.assertEqual(got[self.proj_out.pk], EMPTY)
        self.assertEqual(got[self.cam_broken.pk], UNAVAILABLE)

    def test_hidden_items_not_listed(self):
        """ตัดสินใจ M2 ข้อ 3: ซ่อนของที่ปลดระวาง / สูญหาย"""
        pks = set(student_items().values_list("pk", flat=True))
        self.assertNotIn(self.lost.pk, pks)
        self.assertNotIn(self.retired.pk, pks)
        self.assertIn(self.cam_broken.pk, pks)


class ItemListTests(CatalogFixture):
    """UC-01, UC-02"""

    def test_lists_each_equipment_piece_separately(self):
        r = self.client.get(LIST)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(self.keys(r)), 6)
        self.assertContains(r, "UBU-EQ-001-01")
        self.assertContains(r, "UBU-EQ-001-02")

    def test_search_by_name_and_asset_tag(self):
        self.assertEqual(set(self.keys(self.client.get(LIST + "?q=HDMI"))), {self.hdmi.pk})
        self.assertEqual(set(self.keys(self.client.get(LIST + "?q=eq-001-02"))), {self.proj_out.pk})

    def test_filter_type_and_status(self):
        self.assertEqual(set(self.keys(self.client.get(LIST + "?type=EQUIPMENT"))),
                         {self.proj.pk, self.proj_out.pk, self.cam_broken.pk})
        self.assertEqual(set(self.keys(self.client.get(LIST + "?status=empty"))), {self.pen.pk, self.proj_out.pk})
        self.assertEqual(set(self.keys(self.client.get(LIST + "?status=unavailable"))), {self.cam_broken.pk})

    def test_sort_name(self):
        """เรียงตามพจนานุกรมไทยของฐานข้อมูล (สระหน้า เช่น โ ไม่นับ: โปรเจกเตอร์ อยู่หมวด ป)"""
        names = [i.name for i in self.client.get(LIST + "?sort=name-asc").context["page"]]
        self.assertEqual(names, ["กระดาษ A4", "กล้อง", "ปากกา", "โปรเจกเตอร์", "โปรเจกเตอร์", "สาย HDMI"])

    def test_not_found_message(self):
        self.assertContains(self.client.get(LIST + "?q=ไม่มีแน่นอน"), "ไม่พบรายการที่ค้นหา")

    def test_empty_catalog_message(self):
        Item.objects.all().delete()
        self.assertContains(self.client.get(LIST), "ยังไม่มีรายการสิ่งของ")

    def test_pagination_24(self):
        for n in range(25):
            create_item(Item.ItemType.MATERIAL, name=f"วัสดุ {n:02d}", qty_total=1)
        r = self.client.get(LIST)
        self.assertEqual(len(self.keys(r)), 24)
        self.assertEqual(len(self.keys(self.client.get(LIST + "?page=2"))), 31 - 24)

    def test_buttons_follow_status(self):
        """ตัดสินใจ M2 ข้อ 4 — ปุ่มตามสถานะ (ตะกร้าเปิดใช้แล้วใน M3 รอบ 3a)"""
        r = self.client.get(LIST)
        self.assertContains(r, "+ ยืมชิ้นนี้")
        self.assertContains(r, "วัสดุหมดคลัง (ไม่ต้องคืน)")   # วัสดุสิ้นเปลืองหมด → จองคิวไม่ได้
        self.assertContains(r, "ไม่พร้อมให้บริการ")

    def test_no_image_placeholder(self):
        """สิ่งของที่ไม่มีรูป → ขึ้นว่า "ไม่มีรูป" (ผู้ใช้เลือก ข.) ไม่ใช้อิโมจิตามประเภท"""
        r = self.client.get(LIST)
        self.assertGreaterEqual(r.content.decode().count("data-no-image"), 6)  # การ์ด 6 ใบ + popup
        self.assertContains(r, "ไม่มีรูป")
        self.assertNotContains(r, "📽️")

    def test_menu_is_live(self):
        menu = {m["key"]: m for m in self.client.get(LIST).context["nav_menu"]}
        self.assertTrue(menu["item-list"]["ready"] and menu["item-list"]["active"])

    def test_staff_cannot_open_student_list(self):
        self.client.force_login(make_staff())
        self.assertEqual(self.client.get(LIST).status_code, 403)


class ItemDetailTests(CatalogFixture):
    """UC-03, UC-37"""

    def _review(self, item, rating, comment="", name="ผู้ยืม"):
        s = make_student(f"r{Review.objects.count()}@ubu.ac.th", complete=False)
        s.ubu_user.name = name
        s.ubu_user.save()
        s.ubu_user.student.student_id = f"6799999{Review.objects.count():04d}"
        s.ubu_user.student.save()
        req = BorrowRequest.objects.create(student=s.ubu_user.student, status=BorrowRequest.Status.RETURNED)
        bi = BorrowItem.objects.create(borrow_request=req, item=item)
        return Review.objects.create(borrow_item=bi, rating=rating, comment=comment)

    def test_material_detail(self):
        r = self.client.get(detail(self.paper))
        self.assertContains(r, "กระดาษ A4")
        self.assertContains(r, "คงเหลือ 10 / 10")
        self.assertNotContains(r, 'id="p_item_detail_tab_reviews"')  # รีวิวเฉพาะครุภัณฑ์

    def test_equipment_detail_shows_tag_price_tabs(self):
        r = self.client.get(detail(self.proj))
        self.assertContains(r, "UBU-EQ-001-01")
        self.assertContains(r, "฿18,500.00")
        self.assertContains(r, 'id="p_item_detail_tab_reviews"')
        self.assertContains(r, "ยังไม่มีรีวิว")

    def test_hidden_item_404_for_student(self):
        """UC-03 Alternative: ปลดระวาง/สูญหาย → ไม่พบสิ่งของนี้"""
        self.assertEqual(self.client.get(detail(self.lost)).status_code, 404)
        self.assertEqual(self.client.get(detail(self.retired)).status_code, 404)
        self.assertEqual(self.client.get(reverse("catalog:item_detail", args=[99999])).status_code, 404)

    def test_reviews_average_filter_and_names(self):
        """UC-37 + ตัดสินใจ M2 ข้อ 8 (ชื่อเต็ม)"""
        self._review(self.proj, 5, "สภาพดีมาก", name="สมชาย ใจดี")
        self._review(self.proj, 3, "รีโมทหลวม", name="สมหญิง รักเรียน")
        r = self.client.get(detail(self.proj, "?tab=reviews"))
        self.assertEqual(r.context["tab"], "reviews")
        self.assertContains(r, "4.0")
        self.assertContains(r, "สมชาย ใจดี")
        self.assertContains(r, "รีโมทหลวม")
        r = self.client.get(detail(self.proj, "?tab=reviews&stars=5"))
        self.assertEqual([x.rating for x in r.context["reviews"]], [5])
        r = self.client.get(detail(self.proj, "?tab=reviews&stars=1"))
        self.assertContains(r, "ไม่มีรีวิวระดับ 1 ดาว")

    def test_reviews_are_per_asset_tag(self):
        """UC-37: รีวิวผูกกับรหัสชิ้น ไม่รวมทั้งรุ่น"""
        self._review(self.proj_out, 1, "ชิ้นอื่น")
        r = self.client.get(detail(self.proj, "?tab=reviews"))
        self.assertNotContains(r, "ชิ้นอื่น")

    def test_staff_sees_detail_without_cart_buttons_and_current_location(self):
        """ตัดสินใจ M2 ข้อ 5, 7"""
        req = BorrowRequest.objects.create(student=self.student.ubu_user.student,
                                           status=BorrowRequest.Status.BORROWING)
        BorrowItem.objects.create(borrow_request=req, item=self.proj_out, current_location="หอพักสุขใจ ห้อง 12")
        r = self.client.get(detail(self.proj_out))
        self.assertNotContains(r, "หอพักสุขใจ")                       # นักศึกษาไม่เห็น
        self.client.force_login(make_staff())
        r = self.client.get(detail(self.proj_out))
        self.assertContains(r, "หอพักสุขใจ ห้อง 12")
        self.assertNotContains(r, "จองคิว")
        self.assertContains(r, "กลับไปหน้าจัดการคลังสิ่งของ")
        self.assertEqual(self.client.get(detail(self.lost)).status_code, 200)  # เจ้าหน้าที่เห็นของที่ซ่อน
