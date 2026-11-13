"""M3 รอบ 3a — UC-05 ตะกร้า, UC-06 ส่งคำขอ, UC-07 ยกเลิก, UC-09 หน้าหลัก, แจ้งย้ายที่ตั้ง"""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Student
from accounts.tests_shell import make_staff, make_student
from catalog.models import Equipment, Item
from catalog.services import create_item

from . import services
from .models import BorrowItem, BorrowRequest, CartItem

CART = reverse("borrow:cart")
NEW = reverse("borrow:request_create")
HOME = reverse("borrow:request_list")


def add(item):
    return reverse("borrow:cart_add", args=[item.pk])


class Fixture(TestCase):
    def setUp(self):
        self.auth = make_student()
        self.student = self.auth.ubu_user.student
        self.client.force_login(self.auth)
        self.paper = create_item(Item.ItemType.MATERIAL, name="กระดาษ", qty_total=10)
        self.hdmi = create_item(Item.ItemType.DURABLE_MATERIAL, name="สาย HDMI", qty_total=3,
                                max_borrow_days=7, fine_rate_per_day=Decimal("10"))
        self.proj = create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-01", max_borrow_days=7)

    def other_student(self, n=2):
        a = make_student(f"o{n}@ubu.ac.th", complete=False)
        s = a.ubu_user.student
        s.student_id, s.phone = f"6611454000{n}", "0899999999"
        s.save()
        return a, s

    def reload(self, *items):
        return [Item.objects.select_related("material", "durablematerial", "equipment").get(pk=i.pk) for i in items]


class CartTests(Fixture):
    """UC-05"""

    def test_add_with_qty_from_popup_and_increment(self):
        self.client.post(add(self.paper), {"qty": "3"})
        self.client.post(add(self.paper), {"qty": "2"})
        self.assertEqual(CartItem.objects.get(item=self.paper).qty, 5)

    def test_equipment_once_qty_one(self):
        self.client.post(add(self.proj), {"qty": "5"})
        self.assertEqual(CartItem.objects.get(item=self.proj).qty, 1)
        r = self.client.post(add(self.proj), {"qty": "1"}, follow=True)
        self.assertContains(r, "อยู่ในตะกร้าแล้ว")

    def test_cannot_exceed_stock(self):
        r = self.client.post(add(self.hdmi), {"qty": "4"}, follow=True)
        self.assertContains(r, "คงเหลือ 3")
        self.assertFalse(CartItem.objects.exists())
        self.client.post(add(self.hdmi), {"qty": "2"})
        line = CartItem.objects.get()
        self.client.post(reverse("borrow:cart_update", args=[line.pk]), {"qty": "9"})
        line.refresh_from_db()
        self.assertEqual(line.qty, 2)
        self.client.post(reverse("borrow:cart_update", args=[line.pk]), {"qty": "3"})
        line.refresh_from_db()
        self.assertEqual(line.qty, 3)

    def test_remove(self):
        self.client.post(add(self.paper), {"qty": "1"})
        line = CartItem.objects.get()
        self.client.post(reverse("borrow:cart_remove", args=[line.pk]))
        self.assertFalse(CartItem.objects.exists())

    def test_snipe_detected_and_submit_blocked(self):
        """UC-05 Alternative: มีคนยืมตัดหน้า → ป้ายแดง + บล็อกปุ่มส่ง"""
        self.client.post(add(self.proj), {"qty": "1"})
        self.client.post(add(self.paper), {"qty": "1"})
        Equipment.objects.filter(pk=self.proj.pk).update(status=Equipment.Status.BORROWED)
        r = self.client.get(CART)
        self.assertEqual(r.context["sniped_count"], 1)
        self.assertContains(r, "ครุภัณฑ์นี้ถูกยืมไปแล้ว")
        self.assertContains(r, 'id="p_cart_submit-btn" disabled')
        self.assertRedirects(self.client.get(NEW), CART)
        self.client.post(reverse("borrow:cart_remove", args=[0]), {"all_sniped": "1"})
        self.assertEqual(list(CartItem.objects.values_list("item_id", flat=True)), [self.paper.pk])

    def test_m2_buttons_open_popup_and_show_in_cart(self):
        r = self.client.get(reverse("catalog:item_list"))
        self.assertContains(r, "data-cart-modal")
        self.assertNotContains(r, "ยืมชิ้นนี้ · เปิดใช้เร็ว ๆ นี้")
        self.client.post(add(self.proj), {"qty": "1"})
        self.assertContains(self.client.get(reverse("catalog:item_list")), "ในตะกร้าแล้ว (1 ชิ้น)")

    def test_staff_cannot_use_cart(self):
        self.client.force_login(make_staff())
        self.assertEqual(self.client.post(add(self.paper), {"qty": "1"}).status_code, 403)
        self.assertEqual(self.client.get(CART).status_code, 403)


class SubmitTests(Fixture):
    """UC-06"""

    def fill(self):
        self.client.post(add(self.paper), {"qty": "4"})
        self.client.post(add(self.hdmi), {"qty": "2"})
        self.client.post(add(self.proj), {"qty": "1"})

    def test_submit_creates_pending_reserves_stock_and_clears_cart(self):
        self.fill()
        r = self.client.post(NEW, {})
        self.assertRedirects(r, HOME)
        req = BorrowRequest.objects.get()
        self.assertEqual((req.status, req.use_date, req.is_special), ("PENDING", timezone.localdate(), False))
        self.assertEqual(req.items.count(), 3)
        paper, hdmi, proj = self.reload(self.paper, self.hdmi, self.proj)
        self.assertEqual((paper.material.qty_available, hdmi.durablematerial.qty_available), (6, 1))
        self.assertEqual(proj.equipment.status, Equipment.Status.BORROWED)
        self.assertFalse(CartItem.objects.exists())

    def test_special_requires_future_date(self):
        self.fill()
        r = self.client.post(NEW, {"is_special": "on"})
        self.assertIn("custom_due_date", r.context["form"].errors)
        r = self.client.post(NEW, {"is_special": "on", "custom_due_date": timezone.localdate().isoformat()})
        self.assertIn("custom_due_date", r.context["form"].errors)
        due = timezone.localdate() + timedelta(days=30)
        self.client.post(NEW, {"is_special": "on", "custom_due_date": due.isoformat()})
        req = BorrowRequest.objects.get()
        self.assertEqual((req.is_special, req.custom_due_date), (True, due))

    def test_incomplete_profile_goes_to_profile_and_back(self):
        """UC-06 Alternative → UC-13"""
        Student.objects.filter(pk=self.student.pk).update(phone="")
        self.client.post(add(self.paper), {"qty": "1"})
        # middleware ส่งไปหน้ากรอกข้อมูลครั้งแรกเพราะข้อมูลไม่ครบ (นศ. ที่ไม่มีเบอร์ = ข้อมูลไม่ครบ)
        r = self.client.get(NEW)
        self.assertEqual(r.status_code, 302)
        self.assertFalse(BorrowRequest.objects.exists())

    def test_empty_cart(self):
        self.assertRedirects(self.client.get(NEW), CART)

    def test_snipe_between_open_and_confirm(self):
        """UC-06 Alternative: ถูกตัดหน้าระหว่างกดยืนยัน → ไม่สร้างคำขอ ของในตะกร้ายังอยู่"""
        self.fill()
        self.client.get(NEW)
        _, other = self.other_student()
        services.cart_add(other, self.reload(self.proj)[0], 1)
        services.submit_request(other)
        r = self.client.post(NEW, {}, follow=True)
        self.assertEqual(r.redirect_chain[-1][0], CART)
        self.assertContains(r, "ถูกยืม/เบิกตัดหน้า")
        self.assertEqual(BorrowRequest.objects.filter(student=self.student).count(), 0)
        self.assertEqual(CartItem.objects.filter(cart__student=self.student).count(), 3)

    def test_two_students_cannot_get_same_piece(self):
        """ตัดสินใจ M3 ข้อ 1: จองตอนส่งคำขอ → ไม่มีคำขอซ้อนกัน"""
        _, other = self.other_student()
        services.cart_add(self.student, self.proj, 1)
        services.cart_add(other, self.proj, 1)
        services.submit_request(self.student)
        with self.assertRaises(services.SnipedError):
            services.submit_request(other)


class CancelTests(Fixture):
    """UC-07"""

    def setUp(self):
        super().setUp()
        services.cart_add(self.student, self.paper, 4)
        services.cart_add(self.student, self.proj, 1)
        self.req = services.submit_request(self.student)

    def test_cancel_pending_returns_stock(self):
        self.client.post(reverse("borrow:request_cancel", args=[self.req.pk]))
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "CANCELLED")
        paper, proj = self.reload(self.paper, self.proj)
        self.assertEqual(paper.material.qty_available, 10)
        self.assertEqual(proj.equipment.status, Equipment.Status.AVAILABLE)

    def test_cannot_cancel_after_release(self):
        BorrowRequest.objects.filter(pk=self.req.pk).update(status=BorrowRequest.Status.BORROWING)
        r = self.client.post(reverse("borrow:request_cancel", args=[self.req.pk]), follow=True)
        self.assertContains(r, "ยกเลิกไม่ได้")
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "BORROWING")

    def test_cannot_cancel_someone_elses(self):
        a, _ = self.other_student()
        self.client.force_login(a)
        self.assertEqual(self.client.post(reverse("borrow:request_cancel", args=[self.req.pk])).status_code, 404)


class DashboardTests(Fixture):
    """UC-09 + แจ้งย้ายที่ตั้ง"""

    def test_empty(self):
        self.assertContains(self.client.get(HOME), "ยังไม่มีรายการยืม")

    def test_cards_status_and_menu(self):
        services.cart_add(self.student, self.proj, 1)
        req = services.submit_request(self.student)
        r = self.client.get(HOME)
        self.assertContains(r, f"คำขอ #{req.pk}")
        self.assertContains(r, "รอเจ้าหน้าที่ตรวจของ")
        self.assertContains(r, "ยกเลิกคำขอ")
        menu = {m["key"]: m for m in r.context["nav_menu"]}
        self.assertTrue(menu["request-list"]["ready"] and menu["request-list"]["active"])
        self.assertTrue(menu["cart"]["ready"])
        self.assertRedirects(self.client.get("/"), HOME)

    def test_old_finished_requests_move_out(self):
        """ตัดสินใจ M3 ข้อ 9: จบเกิน 7 วัน ไม่แสดงในหน้าหลัก"""
        old = BorrowRequest.objects.create(student=self.student, status=BorrowRequest.Status.RETURNED)
        BorrowRequest.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=10))
        recent = BorrowRequest.objects.create(student=self.student, status=BorrowRequest.Status.CANCELLED)
        keys = [c["req"].pk for c in self.client.get(HOME).context["cards"]]
        self.assertEqual(keys, [recent.pk])

    def test_relocate_only_active_returnable(self):
        services.cart_add(self.student, self.proj, 1)
        services.cart_add(self.student, self.paper, 1)
        req = services.submit_request(self.student)
        proj_bi = req.items.get(item=self.proj)
        paper_bi = req.items.get(item=self.paper)
        self.client.post(reverse("borrow:relocate", args=[proj_bi.pk]), {"location": "หอพัก"})
        proj_bi.refresh_from_db()
        self.assertEqual(proj_bi.current_location, "")  # ยัง PENDING ย้ายไม่ได้
        BorrowRequest.objects.filter(pk=req.pk).update(status=BorrowRequest.Status.BORROWING)
        self.client.post(reverse("borrow:relocate", args=[proj_bi.pk]), {"location": "หอพักสุขใจ ห้อง 12"})
        proj_bi.refresh_from_db()
        self.assertEqual(proj_bi.current_location, "หอพักสุขใจ ห้อง 12")
        self.assertIsNotNone(proj_bi.moved_at)
        r = self.client.post(reverse("borrow:relocate", args=[paper_bi.pk]), {"location": "x"}, follow=True)
        self.assertContains(r, "แจ้งย้ายได้เฉพาะของที่ต้องคืน")
        self.assertContains(self.client.get(HOME), "หอพักสุขใจ ห้อง 12")
