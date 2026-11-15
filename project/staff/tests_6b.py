"""M6 รอบ 6b — UC-35 ครุภัณฑ์เสียหาย/แจ้งซ่อม, UC-19 ประวัติทั้งระบบ"""
from django.urls import reverse
from django.utils import timezone

from borrow import services as borrow
from borrow.models import DamageReport, Queue
from catalog.models import Equipment

from . import services
from .tests import ReturnFixture, student

DAMAGED = reverse("staff:damaged_equipment")
HISTORY = reverse("staff:all_history")


class DamagedTests(ReturnFixture):
    """UC-35"""

    def setUp(self):
        super().setUp()
        self.confirm([(self.proj_bi, 1, "DAMAGED")])  # คืนมาชำรุด → ขึ้นแท็บ 1 อัตโนมัติ

    def act(self, ids, action):
        return self.client.post(reverse("staff:damaged_action"),
                                {"ids": ",".join(str(i) for i in ids), "action": action}, follow=True)

    def test_returned_damaged_appears_in_tab_1(self):
        r = self.client.get(DAMAGED)
        self.assertEqual([i.pk for i in r.context["items"]], [self.proj.pk])
        menu = {m["key"]: m for m in r.context["nav_menu"]}
        self.assertTrue(menu["damaged-equipment"]["ready"])

    def test_repair_flow_and_fixed_notifies_queue(self):
        _, waiting = student(5)
        q = borrow.join_queue(waiting, self.fresh(self.proj))
        self.act([self.proj.pk], "repair")
        self.assertEqual(self.fresh(self.proj).equipment.status, Equipment.Status.MAINTENANCE)
        r = self.client.get(DAMAGED + "?f=MAINTENANCE")
        self.assertEqual(len(r.context["items"]), 1)
        self.act([self.proj.pk], "fixed")
        self.assertEqual(self.fresh(self.proj).equipment.status, Equipment.Status.AVAILABLE)
        q.refresh_from_db()
        self.assertEqual(q.status, Queue.Status.NOTIFIED)
        self.assertEqual(self.client.get(DAMAGED).context["items"].count(), 0)

    def test_batch_retire_skips_wrong_status(self):
        from catalog.models import Item
        from catalog.services import create_item
        cam = create_item(Item.ItemType.EQUIPMENT, name="กล้อง", asset_tag="UBU-EQ-003-01", status=Equipment.Status.DAMAGED)
        ok = create_item(Item.ItemType.EQUIPMENT, name="ไมค์", asset_tag="UBU-EQ-004-01")  # ปกติ ไม่อยู่ในรายการ
        r = self.act([self.proj.pk, cam.pk, ok.pk], "retire")
        self.assertContains(r, "ปลดระวาง แล้ว 2 ชิ้น")
        self.assertContains(r, "ข้าม 1 ชิ้น")
        self.assertEqual(self.fresh(cam).equipment.status, Equipment.Status.RETIRED)
        self.assertEqual(self.fresh(ok).equipment.status, Equipment.Status.AVAILABLE)

    def test_empty_tabs(self):
        self.act([self.proj.pk], "retire")
        r = self.client.get(DAMAGED + "?f=DAMAGED")
        self.assertContains(r, "ไม่มีรายการในขณะนี้")
        self.assertContains(self.client.get(DAMAGED + "?tab=reports"), "ไม่มีรายการในขณะนี้")

    def test_student_reports_accept_and_close(self):
        rep = borrow.report_damage(self.st, "room", "ไม่เย็น", "EN 304", "แอร์")
        r = self.client.get(DAMAGED + "?tab=reports")
        self.assertContains(r, "แอร์")
        self.assertContains(r, "รอตรวจสอบ")
        self.client.post(reverse("staff:damage_report_action", args=[rep.pk, "accept"]))
        rep.refresh_from_db()
        self.assertEqual(rep.status, DamageReport.Status.IN_PROGRESS)
        self.client.post(reverse("staff:damage_report_action", args=[rep.pk, "close"]))
        rep.refresh_from_db()
        self.assertEqual(rep.status, DamageReport.Status.RESOLVED)
        r = self.client.post(reverse("staff:damage_report_action", args=[rep.pk, "accept"]), follow=True)
        self.assertContains(r, "ปิดงานไปแล้ว")
        self.client.force_login(self.s_auth)
        self.assertContains(self.client.get(reverse("borrow:report_damage")), "แก้ไขแล้ว")

    def test_m7_status_change_to_available_also_notifies_queue(self):
        _, waiting = student(6)
        q = borrow.join_queue(waiting, self.fresh(self.proj))
        self.client.post(reverse("staff_inventory:equipment_status_update", args=[self.proj.pk]),
                         {"status": "AVAILABLE", "note": "ซ่อมแล้ว"})
        q.refresh_from_db()
        self.assertEqual(q.status, Queue.Status.NOTIFIED)


class HistoryTests(ReturnFixture):
    """UC-19"""

    def test_requests_tab_search_filter_dates(self):
        _, other = student(7)
        other_req = self.request_for(other, (self.paper, 1))
        r = self.client.get(HISTORY)
        self.assertEqual({x.pk for x in r.context["page"]}, {self.req.pk, other_req.pk})
        r = self.client.get(HISTORY + "?q=UBU-EQ-001-01")
        self.assertEqual([x.pk for x in r.context["page"]], [self.req.pk])
        r = self.client.get(HISTORY + "?status=PENDING")
        self.assertEqual([x.pk for x in r.context["page"]], [other_req.pk])
        tomorrow = (timezone.localdate() + timezone.timedelta(days=1)).isoformat()
        r = self.client.get(HISTORY + f"?from={tomorrow}")
        self.assertContains(r, "ไม่พบข้อมูล")

    def test_units_tab_shows_holder_and_location(self):
        from borrow.models import BorrowItem
        borrow.relocate(self.st, BorrowItem.objects.get(pk=self.proj_bi.pk), "หอพักสุขใจ ห้อง 12")
        r = self.client.get(HISTORY + "?tab=units")
        row = next(x for x in r.context["rows"] if x["item"].pk == self.proj.pk)
        self.assertEqual(row["loan"].borrow_request.student, self.st)
        self.assertContains(r, "หอพักสุขใจ ห้อง 12")
        r = self.client.get(HISTORY + "?tab=units&status=AVAILABLE")
        self.assertNotIn(self.proj.pk, [x["item"].pk for x in r.context["rows"]])

    def test_detail_shows_approver_inspector_and_fines(self):
        self.confirm([(self.proj_bi, 1, "NORMAL"), (self.hdmi_bi, 3, "LOST", "300")])
        r = self.client.get(reverse("staff:history_detail", args=[self.req.pk]))
        self.assertContains(r, self.staff.user.name or "")
        self.assertContains(r, "สูญหาย")
        self.assertContains(r, "฿300.00")
        self.assertContains(r, "ค้างชำระ")

    def test_student_cannot_access(self):
        self.client.force_login(self.s_auth)
        for url in [HISTORY, DAMAGED, reverse("staff:history_detail", args=[self.req.pk])]:
            self.assertEqual(self.client.get(url).status_code, 403)


class AdminHistoryAccessTests(ReturnFixture):
    """ข้อ H: แอดมินดูประวัติทั้งระบบได้"""

    def test_admin_menu_and_pages(self):
        from accounts.tests_shell import make_admin
        self.client.force_login(make_admin())
        r = self.client.get(HISTORY)
        self.assertEqual(r.status_code, 200)
        menu = {m["key"]: m for m in r.context["nav_menu"]}
        self.assertTrue(menu["admin-history"]["ready"] and menu["admin-history"]["active"])
        self.assertEqual(self.client.get(HISTORY + "?tab=units").status_code, 200)
        self.assertEqual(self.client.get(reverse("staff:history_detail", args=[self.req.pk])).status_code, 200)
        self.assertEqual(self.client.get(DAMAGED).status_code, 403)  # หน้าอื่นของเจ้าหน้าที่ยังเข้าไม่ได้
