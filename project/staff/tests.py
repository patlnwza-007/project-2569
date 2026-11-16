"""M6 รอบ 6a — UC-16 แดชบอร์ด, UC-17 ปล่อยของ, UC-18 รับคืน, UC-36 ค่าปรับ + กันของให้คิว"""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.tests_shell import make_staff, make_student
from borrow import services as borrow
from borrow.models import BorrowItem, BorrowRequest, Queue, ReturnItem, ReturnRequest
from catalog.models import Equipment, Item
from catalog.services import create_item

from . import services

S = BorrowRequest.Status


def student(n):
    a = make_student(f"s{n}@ubu.ac.th", complete=False)
    st = a.ubu_user.student
    st.student_id, st.phone = f"661145400{n:02d}", "0812345678"
    st.save()
    return a, st


class Fixture(TestCase):
    def setUp(self):
        self.staff_auth = make_staff()
        self.staff = self.staff_auth.ubu_user.staff
        self.client.force_login(self.staff_auth)
        self.s_auth, self.st = student(1)
        self.paper = create_item(Item.ItemType.MATERIAL, name="กระดาษ", qty_total=10)
        self.hdmi = create_item(Item.ItemType.DURABLE_MATERIAL, name="สาย HDMI", qty_total=10,
                                max_borrow_days=3, fine_rate_per_day=Decimal("10"))
        self.proj = create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-01",
                                max_borrow_days=7, fine_rate_per_day=Decimal("50"), purchase_price=Decimal("18500"))

    def fresh(self, item):
        return Item.objects.select_related("material", "durablematerial", "equipment").get(pk=item.pk)

    def request_for(self, st, *pairs, special_due=None):
        for item, qty in pairs:
            borrow.cart_add(st, self.fresh(item), qty)
        return borrow.submit_request(st, bool(special_due), special_due)


class AccessTests(Fixture):
    def test_staff_only_and_menus_live(self):
        r = self.client.get(reverse("staff:dashboard"))
        self.assertEqual(r.status_code, 200)
        menu = {m["key"]: m for m in r.context["nav_menu"]}
        for key in ["staff-dashboard", "pending-requests", "return-list"]:
            self.assertTrue(menu[key]["ready"], key)
        self.client.force_login(self.s_auth)
        for name in ["staff:dashboard", "staff:pending_requests", "staff:return_list"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 403)


class DashboardTests(Fixture):
    """UC-16"""

    def test_cards(self):
        self.request_for(self.st, (self.paper, 1))
        req = self.request_for(self.st, (self.hdmi, 1))
        services.approve_request(self.staff, req, [bi.pk for bi in req.items.all()])
        BorrowItem.objects.filter(borrow_request=req).update(due_date=timezone.localdate() - timedelta(days=1))
        r = self.client.get(reverse("staff:dashboard"))
        counts = {c["label"]: c["count"] for c in r.context["cards"]}
        self.assertEqual(counts["รอตรวจของหน้าเคาน์เตอร์"], 1)
        self.assertEqual(counts["กำลังยืมอยู่"], 1)
        self.assertEqual(counts["เกินกำหนดคืน"], 1)
        self.assertEqual(len(r.context["latest"]), 1)


class ApproveTests(Fixture):
    """UC-17"""

    def test_release_all_sets_borrowing_due_dates_and_approver(self):
        req = self.request_for(self.st, (self.proj, 1), (self.hdmi, 2), (self.paper, 3))
        keep = [bi.pk for bi in req.items.all()]
        self.client.post(reverse("staff:request_approve", args=[req.pk]), {"keep": keep})
        req.refresh_from_db()
        self.assertEqual((req.status, req.approved_by, req.approved_at is not None), (S.BORROWING, self.staff, True))
        today = timezone.localdate()
        dues = {bi.item_id: bi.due_date for bi in req.items.all()}
        self.assertEqual(dues[self.proj.pk], today + timedelta(days=7))
        self.assertEqual(dues[self.hdmi.pk], today + timedelta(days=3))
        self.assertIsNone(dues[self.paper.pk])
        self.assertEqual(self.fresh(self.proj).equipment.status, Equipment.Status.BORROWED)

    def test_materials_only_issued(self):
        req = self.request_for(self.st, (self.paper, 2))
        self.client.post(reverse("staff:request_approve", args=[req.pk]), {"keep": [req.items.get().pk]})
        req.refresh_from_db()
        self.assertEqual(req.status, S.ISSUED)
        self.assertEqual(self.fresh(self.paper).material.qty_available, 8)

    def test_unticked_item_removed_and_restocked(self):
        """ตัดสินใจ M6 ข้อ 2"""
        req = self.request_for(self.st, (self.proj, 1), (self.paper, 3))
        paper_bi = req.items.get(item=self.paper)
        self.client.post(reverse("staff:request_approve", args=[req.pk]), {"keep": [req.items.get(item=self.proj).pk]})
        self.assertFalse(BorrowItem.objects.filter(pk=paper_bi.pk).exists())
        self.assertEqual(self.fresh(self.paper).material.qty_available, 10)

    def test_nothing_ticked_not_allowed(self):
        req = self.request_for(self.st, (self.proj, 1))
        r = self.client.post(reverse("staff:request_approve", args=[req.pk]), {}, follow=True)
        self.assertContains(r, "ไม่ได้เลือกสิ่งของที่จะปล่อยเลย")
        req.refresh_from_db()
        self.assertEqual(req.status, S.PENDING)

    def test_special_due_adjusted(self):
        due = timezone.localdate() + timedelta(days=30)
        req = self.request_for(self.st, (self.proj, 1), special_due=due)
        new_due = timezone.localdate() + timedelta(days=20)
        self.client.post(reverse("staff:request_approve", args=[req.pk]),
                         {"keep": [req.items.get().pk], "custom_due_date": new_due.isoformat()})
        self.assertEqual(req.items.get().due_date, new_due)

    def test_reject_requires_reason_and_restocks(self):
        req = self.request_for(self.st, (self.proj, 1), (self.paper, 2))
        self.client.post(reverse("staff:request_reject", args=[req.pk]), {"reject_reason": ""})
        req.refresh_from_db()
        self.assertEqual(req.status, S.PENDING)
        self.client.post(reverse("staff:request_reject", args=[req.pk]), {"reject_reason": "ของไม่ครบ"})
        req.refresh_from_db()
        self.assertEqual((req.status, req.reject_reason), (S.REJECTED, "ของไม่ครบ"))
        self.assertEqual(self.fresh(self.proj).equipment.status, Equipment.Status.AVAILABLE)
        self.assertEqual(self.fresh(self.paper).material.qty_available, 10)
        self.client.force_login(self.s_auth)
        self.assertContains(self.client.get(reverse("borrow:request_list")), "ของไม่ครบ")

    def test_cannot_release_cancelled(self):
        req = self.request_for(self.st, (self.proj, 1))
        borrow.cancel_request(self.st, req)
        r = self.client.post(reverse("staff:request_approve", args=[req.pk]), {"keep": [req.items.get().pk]}, follow=True)
        self.assertContains(r, "ปล่อยของไม่ได้")

    def test_dual_role_can_release_own_request(self):
        """UC-17 business rule: เจ้าหน้าที่ Dual-Role ปล่อยของให้คำขอตัวเองได้"""
        from accounts.models import Student
        Student.objects.create(user=self.staff_auth.ubu_user, student_id="66114549990", phone="0811111111")
        own = self.request_for(self.staff_auth.ubu_user.student, (self.paper, 1))
        self.client.post(reverse("staff:request_approve", args=[own.pk]), {"keep": [own.items.get().pk]})
        own.refresh_from_db()
        self.assertEqual(own.status, S.ISSUED)


class ReturnFixture(Fixture):
    def setUp(self):
        super().setUp()
        self.req = self.request_for(self.st, (self.proj, 1), (self.hdmi, 3))
        services.approve_request(self.staff, self.req, [bi.pk for bi in self.req.items.all()])
        self.proj_bi = self.req.items.get(item=self.proj)
        self.hdmi_bi = self.req.items.get(item=self.hdmi)
        self.url = reverse("staff:return_confirm", args=[self.req.pk])

    def confirm(self, rows, **extra):
        data = {"receive": [str(r[0].pk) for r in rows], **extra}
        for bi, qty, cond, *rest in rows:
            data[f"qty_{bi.pk}"] = qty
            data[f"cond_{bi.pk}"] = cond
            if rest:
                data[f"lost_{bi.pk}"] = rest[0]
        return self.client.post(self.url, data, follow=True)


class ReturnTests(ReturnFixture):
    """UC-18"""

    def test_walk_in_return_all_normal(self):
        """ตัดสินใจ M6 ข้อ 3: นักศึกษาไม่ได้แจ้งคืน → เจ้าหน้าที่รับคืนเองได้"""
        r = self.client.get(reverse("staff:return_list") + "?tab=counter")
        self.assertEqual([c["req"].pk for c in r.context["cards"]], [self.req.pk])
        self.assertContains(r, "data-not-notified")
        self.assertContains(r, "data-open-counter")      # การ์ดหุบไว้ ต้องกดเปิดก่อน
        self.assertContains(r, "🏃 รับคืนที่เคาน์เตอร์</button>")
        r = self.client.get(reverse("staff:return_list"))  # แท็บแรก = แจ้งคืนแล้ว → ยังไม่มี
        self.assertEqual((r.context["tab"], r.context["cards"]), ("notified", []))
        r = self.confirm([(self.proj_bi, 1, "NORMAL"), (self.hdmi_bi, 3, "NORMAL")])
        self.assertContains(r, "คืนครบแล้ว")
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, S.RETURNED)
        rr = ReturnRequest.objects.get()
        self.assertEqual((rr.status, rr.inspected_by, rr.note), ("RETURNED", self.staff, services.WALK_IN_NOTE))
        self.assertEqual(self.fresh(self.proj).equipment.status, Equipment.Status.AVAILABLE)
        self.assertEqual(self.fresh(self.hdmi).durablematerial.qty_available, 10)

    def test_partial_return_keeps_borrowing(self):
        r = self.confirm([(self.hdmi_bi, 2, "NORMAL")])
        self.assertContains(r, "ยังค้างส่งอีก 2 ชิ้น")
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, S.BORROWING)
        r = self.client.get(reverse("staff:return_list") + "?tab=partial")
        self.assertEqual([c["req"].pk for c in r.context["cards"]], [self.req.pk])

    def test_student_notified_round_prechecked_and_unticked_goes_back(self):
        from borrow.tests_m3b import png
        from django.test import override_settings
        with override_settings(MEDIA_ROOT="/tmp/yuemdee-test-media-6a"):
            borrow.notify_return(self.st, self.req, [(self.proj_bi.pk, 1, "NORMAL", "", png()),
                                                     (self.hdmi_bi.pk, 1, "NORMAL", "", png())])
        r = self.client.get(reverse("staff:return_list"))
        self.assertEqual(r.context["tab"], "notified")
        self.assertContains(r, 'data-source="notified"')
        self.assertNotContains(r, "data-open-counter")
        r2 = self.client.get(reverse("staff:return_list") + "?tab=counter")
        self.assertEqual(r2.context["cards"], [])           # แจ้งแล้ว → ไม่ปนในแท็บเคาน์เตอร์
        rows = {row["bi"].pk: row for row in r.context["cards"][0]["rows"]}
        self.assertIsNotNone(rows[self.proj_bi.pk]["declared"])
        self.assertContains(r, "data-return-photo", count=2)  # เจ้าหน้าที่เห็นรูปรายชิ้นที่ นศ. แนบ
        with override_settings(MEDIA_ROOT="/tmp/yuemdee-test-media-6a"):
            self.confirm([(self.hdmi_bi, 1, "NORMAL")])  # โปรเจกเตอร์ไม่ได้นำมาจริง
        self.assertEqual(self.fresh(self.proj).equipment.status, Equipment.Status.BORROWED)
        kept = ReturnRequest.objects.get().items.get()
        self.assertEqual(kept.borrow_item_id, self.hdmi_bi.pk)
        self.assertTrue(kept.photo)  # รูปของ นศ. ยังอยู่หลังเจ้าหน้าที่ตรวจรับ

    def test_damaged_and_lost_effects(self):
        """UC-18 ข้อ 3 + ตัดสินใจ M6 ข้อ 4, 5"""
        self.client.post(self.url, {"receive": [self.proj_bi.pk, self.hdmi_bi.pk],
                                    f"qty_{self.proj_bi.pk}": 1, f"cond_{self.proj_bi.pk}": "DAMAGED",
                                    f"note_{self.proj_bi.pk}": "เลนส์แตก",
                                    f"qty_{self.hdmi_bi.pk}": 3, f"cond_{self.hdmi_bi.pk}": "LOST"})
        eq = self.fresh(self.proj).equipment
        self.assertEqual((eq.status, eq.note), (Equipment.Status.DAMAGED, "เลนส์แตก"))
        d = self.fresh(self.hdmi).durablematerial
        self.assertEqual((d.qty_total, d.qty_available), (7, 7))
        lost = ReturnItem.objects.get(borrow_item=self.hdmi_bi)
        self.assertEqual(lost.lost_compensation, Decimal("0.00"))  # ราคาจัดซื้อ 0 × 3
        from borrow.models import DamageReport
        self.assertFalse(DamageReport.objects.exists())

    def test_lost_equipment_default_compensation_from_price(self):
        self.confirm([(self.proj_bi, 1, "LOST")])
        self.assertEqual(self.fresh(self.proj).equipment.status, Equipment.Status.LOST)
        self.assertEqual(ReturnItem.objects.get().lost_compensation, Decimal("18500.00"))

    def test_durable_damaged_removed_from_total(self):
        self.confirm([(self.hdmi_bi, 3, "DAMAGED")])
        d = self.fresh(self.hdmi).durablematerial
        self.assertEqual((d.qty_total, d.qty_available), (7, 7))


class FineTests(ReturnFixture):
    """UC-36"""

    def make_late(self, days=4):
        BorrowItem.objects.filter(borrow_request=self.req).update(due_date=timezone.localdate() - timedelta(days=days))
        self.proj_bi.refresh_from_db()
        self.hdmi_bi.refresh_from_db()

    def test_auto_fine_per_item(self):
        self.make_late(4)
        r = self.client.get(reverse("staff:return_list") + "?tab=overdue")
        self.assertEqual(len(r.context["cards"]), 1)
        self.confirm([(self.proj_bi, 1, "NORMAL"), (self.hdmi_bi, 2, "NORMAL")])
        rr = ReturnRequest.objects.get()
        self.assertEqual(rr.total_fine, Decimal("280.00"))  # 4×50×1 + 4×10×2

    def test_custom_fine_and_unpaid_tab_then_paid(self):
        self.make_late(2)
        self.confirm([(self.proj_bi, 1, "NORMAL")], custom_fine="50", fine_reason="ลดให้ครึ่งหนึ่ง")
        rr = ReturnRequest.objects.get()
        self.assertEqual((rr.total_fine, rr.fine_reason, rr.fine_paid), (Decimal("50.00"), "ลดให้ครึ่งหนึ่ง", False))
        r = self.client.get(reverse("staff:return_list") + "?tab=unpaid")
        self.assertEqual([x.pk for x in r.context["unpaid"]], [rr.pk])
        self.client.force_login(self.s_auth)
        self.assertContains(self.client.get(reverse("borrow:request_list")), "data-unpaid")
        self.client.force_login(self.staff_auth)
        self.client.post(reverse("staff:edit_fine", args=[rr.pk]), {"action": "fine", "custom_fine": "0"})
        rr.refresh_from_db()
        self.assertEqual(rr.total_fine, Decimal("0.00"))
        self.client.post(reverse("staff:edit_fine", args=[rr.pk]), {"action": "fine", "custom_fine": ""})
        rr.refresh_from_db()
        self.assertEqual(rr.total_fine, Decimal("100.00"))  # กลับไปใช้ยอดอัตโนมัติ 2×50
        self.client.post(reverse("staff:edit_fine", args=[rr.pk]), {"action": "fine_paid", "paid": "1"})
        r = self.client.get(reverse("staff:return_list") + "?tab=unpaid")
        self.assertEqual(r.context["unpaid"], [])

    def test_lost_compensation_edit_and_paid(self):
        self.confirm([(self.proj_bi, 1, "LOST", "15000")])
        ri = ReturnItem.objects.get()
        self.assertEqual(ri.lost_compensation, Decimal("15000.00"))
        rr = ri.return_request
        self.client.post(reverse("staff:edit_fine", args=[rr.pk]), {"action": "lost", "item": ri.pk, "paid": "1"})
        ri.refresh_from_db()
        self.assertTrue(ri.lost_paid)

    def test_negative_fine_rejected(self):
        r = self.confirm([(self.proj_bi, 1, "NORMAL")], custom_fine="-5")
        self.assertContains(r, "ต้องไม่ติดลบ")
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, S.BORROWING)


class QueueHoldTests(ReturnFixture):
    """ตัดสินใจ M6 ข้อ 6: คืนแล้ว → แจ้งคิว → กันของไว้ให้ผู้ถึงคิว"""

    def test_return_notifies_and_holds_for_queue(self):
        _, waiting = student(2)
        _, other = student(3)
        q = borrow.join_queue(waiting, self.fresh(self.proj))
        self.confirm([(self.proj_bi, 1, "NORMAL")])
        q.refresh_from_db()
        self.assertEqual(q.status, Queue.Status.NOTIFIED)
        from django.core.exceptions import ValidationError
        with self.assertRaisesMessage(ValidationError, "จองไว้ให้ผู้รอคิว"):
            borrow.cart_add(other, self.fresh(self.proj), 1)
        borrow.cart_add(waiting, self.fresh(self.proj), 1)  # ผู้ถึงคิวยืมได้

    def test_hold_expires_after_one_day(self):
        _, waiting = student(2)
        _, other = student(3)
        q = borrow.join_queue(waiting, self.fresh(self.proj))
        self.confirm([(self.proj_bi, 1, "NORMAL")])
        Queue.objects.filter(pk=q.pk).update(notified_at=timezone.now() - timedelta(days=2))
        borrow.expire_and_advance()
        q.refresh_from_db()
        self.assertEqual(q.status, Queue.Status.EXPIRED)
        borrow.cart_add(other, self.fresh(self.proj), 1)


def tearDownModule():
    import shutil
    shutil.rmtree("/tmp/yuemdee-test-media-6a", ignore_errors=True)


class QueueHoldDisplayTests(ReturnFixture):
    """ของที่กันไว้ให้ผู้รอคิว: การ์ด/รายละเอียดแสดง "จองไว้ให้ผู้รอคิว" + ถึงคิวแล้วไปหน้าส่งคำขอทันที"""

    def setUp(self):
        super().setUp()
        self.w_auth, self.waiting = student(2)
        self.o_auth, self.other = student(3)
        self.q = borrow.join_queue(self.waiting, self.fresh(self.proj))
        self.confirm([(self.proj_bi, 1, "NORMAL")])  # คืนแล้ว → แจ้งคิว

    def list_status(self, auth, qs=""):
        self.client.force_login(auth)
        r = self.client.get(reverse("catalog:item_list") + qs)
        return {i.pk: i.availability for i in r.context["page"]}, r

    def test_others_see_held_holder_sees_available(self):
        status, r = self.list_status(self.o_auth)
        self.assertEqual(status[self.proj.pk], "held")
        self.assertContains(r, "จองไว้ให้ผู้รอคิว")
        self.assertContains(r, "จองคิวต่อ")
        status, _ = self.list_status(self.w_auth)
        self.assertEqual(status[self.proj.pk], "available")
        self.client.force_login(self.o_auth)
        r = self.client.get(reverse("catalog:item_detail", args=[self.proj.pk]))
        self.assertContains(r, "ว่างแล้ว แต่จองไว้ให้ผู้รอคิว")

    def test_status_filters(self):
        status, _ = self.list_status(self.o_auth, "?status=available")
        self.assertNotIn(self.proj.pk, status)
        status, _ = self.list_status(self.o_auth, "?status=empty")
        self.assertIn(self.proj.pk, status)

    def test_others_can_queue_behind(self):
        self.client.force_login(self.o_auth)
        self.client.post(reverse("borrow:queue_join", args=[self.proj.pk]))
        self.assertTrue(Queue.objects.filter(student=self.other, item=self.proj, status="WAITING").exists())

    def test_banner_on_every_student_page_and_confirm_goes_to_request_form(self):
        self.client.force_login(self.w_auth)
        for name in ["borrow:request_list", "catalog:item_list", "accounts:profile"]:
            self.assertContains(self.client.get(reverse(name)), "data-queue-alert")
        r = self.client.post(reverse("borrow:queue_action", args=[self.q.pk, "confirm"]))
        self.assertRedirects(r, reverse("borrow:request_create"))
        self.q.refresh_from_db()
        self.assertEqual(self.q.status, Queue.Status.CONFIRMED)
        from borrow.models import CartItem
        self.assertTrue(CartItem.objects.filter(cart__student=self.waiting, item=self.proj).exists())
        self.client.post(reverse("borrow:request_create"), {})
        self.assertEqual(self.fresh(self.proj).equipment.status, Equipment.Status.BORROWED)
        self.assertNotContains(self.client.get(reverse("borrow:request_list")), "data-queue-alert")

    def test_others_do_not_see_banner(self):
        self.client.force_login(self.o_auth)
        self.assertNotContains(self.client.get(reverse("borrow:request_list")), "data-queue-alert")



class ReturnSourceBadgeTests(ReturnFixture):
    """ป้ายวิธีคืนในประวัติ: รับคืนที่เคาน์เตอร์ vs แจ้งคืนผ่านระบบ"""

    def test_walk_in_badge_in_history(self):
        self.confirm([(self.proj_bi, 1, "NORMAL")])
        rr = ReturnRequest.objects.get()
        self.assertTrue(rr.is_walk_in)
        r = self.client.get(reverse("staff:history_detail", args=[self.req.pk]))
        self.assertContains(r, 'data-source="counter"')
        r = self.client.get(reverse("staff:all_history"))
        self.assertContains(r, "รับคืนที่เคาน์เตอร์")

    def test_notified_badge(self):
        from borrow.tests_m3b import png
        from django.test import override_settings
        with override_settings(MEDIA_ROOT="/tmp/yuemdee-test-media-6a"):
            borrow.notify_return(self.st, self.req, [(self.proj_bi.pk, 1, "NORMAL", "", png())])
            self.confirm([(self.proj_bi, 1, "NORMAL")])
        self.assertFalse(ReturnRequest.objects.get().is_walk_in)
        r = self.client.get(reverse("staff:history_detail", args=[self.req.pk]))
        self.assertContains(r, 'data-source="notified"')
