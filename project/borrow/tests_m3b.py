"""M3 รอบ 3b — UC-08 แจ้งคืน, UC-10 คิว, UC-11 ประวัติ, UC-38 แจ้งชำรุด"""
import io
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from catalog.models import Equipment, Item

from . import services
from .models import BorrowRequest, CartItem, DamageReport, Queue, ReturnRequest
from .tests_m3a import Fixture

MEDIA = "/tmp/yuemdee-test-media-3b"


def png():
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), "red").save(buf, "PNG")
    return SimpleUploadedFile("p.png", buf.getvalue(), content_type="image/png")


def release(req, days=7):
    """จำลอง UC-17 (M6): ปล่อยของ → BORROWING + กำหนดคืน"""
    req.status = BorrowRequest.Status.BORROWING
    req.save()
    for bi in req.items.select_related("item", "borrow_request"):
        bi.due_date = services.compute_due_date(bi, timezone.localdate())
        bi.save()


def inspect(rr):
    """จำลอง UC-18 (M6): ตรวจรับคืนรอบนี้สำเร็จ"""
    rr.status = ReturnRequest.Status.RETURNED
    rr.returned_at = timezone.now()
    rr.save()
    req = rr.borrow_request
    req.status = BorrowRequest.Status.BORROWING if services.returnable_lines(req) else BorrowRequest.Status.RETURNED
    req.save()


@override_settings(MEDIA_ROOT=MEDIA)
class ReturnTests(Fixture):
    """UC-08"""

    def setUp(self):
        super().setUp()
        services.cart_add(self.student, self.proj, 1)
        services.cart_add(self.student, self.hdmi, 3)
        services.cart_add(self.student, self.paper, 2)
        self.req = services.submit_request(self.student)
        release(self.req)
        self.proj_bi = self.req.items.get(item=self.proj)
        self.hdmi_bi = self.req.items.get(item=self.hdmi)
        self.url = reverse("borrow:return_notify", args=[self.req.pk])

    def test_page_lists_only_returnable(self):
        r = self.client.get(self.url)
        self.assertEqual({bi.pk for bi, _ in r.context["lines"]}, {self.proj_bi.pk, self.hdmi_bi.pk})

    def test_partial_return_with_conditions(self):
        r = self.client.post(self.url, {
            f"pick_{self.hdmi_bi.pk}": "1", f"qty_{self.hdmi_bi.pk}": "2", f"cond_{self.hdmi_bi.pk}": "DAMAGED",
            f"desc_{self.hdmi_bi.pk}": "หัวงอ", "return_photo": png(), "note": "มาคืนช่วงบ่าย"})
        self.assertRedirects(r, reverse("borrow:request_list"))
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "RETURN_PENDING")
        rr = ReturnRequest.objects.get()
        self.assertTrue(rr.return_photo)
        self.assertIn("หัวงอ", rr.note)
        self.assertIn("มาคืนช่วงบ่าย", rr.note)
        ri = rr.items.get()
        self.assertEqual((ri.qty_returned, ri.condition_status), (2, "DAMAGED"))
        self.assertEqual(Equipment.objects.get(pk=self.proj.pk).status, Equipment.Status.BORROWED)  # ไม่ได้คืนชิ้นนี้

    def test_equipment_goes_return_pending(self):
        self.client.post(self.url, {f"pick_{self.proj_bi.pk}": "1", f"qty_{self.proj_bi.pk}": "1",
                                    f"cond_{self.proj_bi.pk}": "NORMAL", "return_photo": png()})
        self.assertEqual(Equipment.objects.get(pk=self.proj.pk).status, Equipment.Status.RETURN_PENDING)

    def test_photo_required_and_pick_required(self):
        r = self.client.post(self.url, {f"pick_{self.proj_bi.pk}": "1", f"cond_{self.proj_bi.pk}": "NORMAL"})
        self.assertContains(r, "กรุณาแนบรูปหลักฐาน")
        r = self.client.post(self.url, {"return_photo": png()})
        self.assertContains(r, "เลือกสิ่งของที่จะคืนอย่างน้อย 1 รายการ")
        self.assertFalse(ReturnRequest.objects.exists())

    def test_over_qty_rejected(self):
        r = self.client.post(self.url, {f"pick_{self.hdmi_bi.pk}": "1", f"qty_{self.hdmi_bi.pk}": "9",
                                        f"cond_{self.hdmi_bi.pk}": "NORMAL", "return_photo": png()})
        self.assertContains(r, "คืนได้ 1–3")
        self.assertFalse(ReturnRequest.objects.exists())

    def test_one_round_at_a_time_then_next_round(self):
        """ตัดสินใจ M3 ข้อ 7"""
        self.client.post(self.url, {f"pick_{self.hdmi_bi.pk}": "1", f"qty_{self.hdmi_bi.pk}": "1",
                                    f"cond_{self.hdmi_bi.pk}": "NORMAL", "return_photo": png()})
        r = self.client.get(self.url)
        self.assertContains(r, "รอเจ้าหน้าที่ตรวจรับอยู่แล้ว")
        inspect(ReturnRequest.objects.get())
        r = self.client.get(self.url)
        left = dict((bi.pk, q) for bi, q in r.context["lines"])
        self.assertEqual(left[self.hdmi_bi.pk], 2)

    def test_cancel_notification(self):
        """UC-08 Alternative: ยกเลิกแจ้งคืน → กลับเป็นกำลังยืม"""
        self.client.post(self.url, {f"pick_{self.proj_bi.pk}": "1", f"cond_{self.proj_bi.pk}": "NORMAL",
                                    f"qty_{self.proj_bi.pk}": "1", "return_photo": png()})
        rr = ReturnRequest.objects.get()
        self.assertContains(self.client.get(reverse("borrow:request_list")), "ยกเลิกการแจ้งคืน")
        self.client.post(reverse("borrow:return_cancel", args=[rr.pk]))
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "BORROWING")
        self.assertFalse(ReturnRequest.objects.exists())
        self.assertEqual(Equipment.objects.get(pk=self.proj.pk).status, Equipment.Status.BORROWED)

    def test_not_borrowing_yet(self):
        services.cart_add(self.student, self.reload(self.paper)[0], 1)
        pending = services.submit_request(self.student)
        r = self.client.get(reverse("borrow:return_notify", args=[pending.pk]), follow=True)
        self.assertContains(r, "แจ้งคืนไม่ได้")


class QueueTests(Fixture):
    """UC-10"""

    def setUp(self):
        super().setUp()
        _, self.other = self.other_student()
        services.cart_add(self.other, self.proj, 1)
        self.loan = services.submit_request(self.other)
        release(self.loan)

    def join(self, item):
        return self.client.post(reverse("borrow:queue_join", args=[item.pk]), follow=True)

    def test_join_borrowed_equipment_shows_position_and_estimate(self):
        r = self.join(self.proj)
        q = Queue.objects.get(student=self.student)
        self.assertEqual(q.status, "WAITING")
        due = self.loan.items.get().due_date
        self.assertContains(r, "ลำดับที่ 1")
        self.assertContains(r, f"{due:%d/%m/%Y}")
        row = r.context["active"][0]
        self.assertEqual((row["pos"], row["date"]), (1, due))

    def test_second_in_line_adds_borrow_days(self):
        """ตัดสินใจ M3 ข้อ 4"""
        a3, s3 = self.other_student(3)
        services.join_queue(s3, self.proj)
        self.join(self.proj)
        q = Queue.objects.get(student=self.student)
        date, _ = services.estimate_available(q)
        self.assertEqual(date, self.loan.items.get().due_date + timedelta(days=7))

    def test_cannot_join_when_available_material_or_twice(self):
        r = self.join(self.hdmi)
        self.assertContains(r, "ยืมได้ทันที")
        r = self.join(self.paper)
        self.assertContains(r, "วัสดุสิ้นเปลืองจองคิวไม่ได้")
        self.join(self.proj)
        r = self.join(self.proj)
        self.assertContains(r, "คุณอยู่ในคิวแล้ว")
        self.assertEqual(Queue.objects.filter(student=self.student).count(), 1)

    def test_queue_instead_from_cart_removes_line(self):
        """UC-05 → UC-10: จองคิวแทนเมื่อถูกตัดหน้า"""
        Equipment.objects.filter(pk=self.proj.pk).update(status=Equipment.Status.AVAILABLE)
        services.cart_add(self.student, self.reload(self.proj)[0], 1)
        Equipment.objects.filter(pk=self.proj.pk).update(status=Equipment.Status.BORROWED)
        line = CartItem.objects.get(cart__student=self.student)
        self.assertContains(self.client.get(reverse("borrow:cart")), "⏳ จองคิวแทน</button>")
        self.client.post(reverse("borrow:queue_join", args=[self.proj.pk]), {"from_cart": line.pk})
        self.assertFalse(CartItem.objects.filter(pk=line.pk).exists())
        self.assertTrue(Queue.objects.filter(student=self.student, item=self.proj).exists())

    def test_notify_confirm_leave(self):
        self.join(self.proj)
        q = Queue.objects.get(student=self.student)
        Equipment.objects.filter(pk=self.proj.pk).update(status=Equipment.Status.AVAILABLE)  # คืนแล้ว (M6)
        services.notify_next(self.reload(self.proj)[0])
        q.refresh_from_db()
        self.assertEqual(q.status, "NOTIFIED")
        r = self.client.get(reverse("borrow:queue_list"))
        self.assertContains(r, "ถึงคิวของคุณแล้ว")
        menu = {m["key"]: m for m in r.context["nav_menu"]}
        self.assertEqual(menu["queue-list"]["badge"], 1)
        self.client.post(reverse("borrow:queue_action", args=[q.pk, "confirm"]))
        q.refresh_from_db()
        self.assertEqual(q.status, "CONFIRMED")
        self.client.post(reverse("borrow:queue_action", args=[q.pk, "leave"]))
        q.refresh_from_db()
        self.assertEqual(q.status, "CANCELLED")

    def test_expired_after_one_day_and_next_notified(self):
        """UC-10 Alternative: ไม่ยืนยันใน 1 วัน → EXPIRED + แจ้งคิวถัดไป"""
        self.join(self.proj)
        _, s3 = self.other_student(3)
        q3 = services.join_queue(s3, self.proj)
        Equipment.objects.filter(pk=self.proj.pk).update(status=Equipment.Status.AVAILABLE)
        services.notify_next(self.reload(self.proj)[0], now=timezone.now() - timedelta(days=2))
        self.client.get(reverse("borrow:queue_list"))
        mine = Queue.objects.get(student=self.student)
        q3.refresh_from_db()
        self.assertEqual((mine.status, q3.status), ("EXPIRED", "NOTIFIED"))
        r = self.client.post(reverse("borrow:queue_action", args=[mine.pk, "confirm"]), follow=True)
        self.assertContains(r, "ยังไม่ถึงคิวของคุณ")

    def test_m2_queue_button_live(self):
        r = self.client.get(reverse("catalog:item_detail", args=[self.proj.pk]))
        self.assertContains(r, "จองคิวรหัสนี้")
        self.assertNotContains(r, "จองคิว · เปิดใช้เร็ว ๆ นี้")


class HistoryTests(Fixture):
    """UC-11"""

    def test_empty(self):
        self.assertContains(self.client.get(reverse("borrow:history")), "ยังไม่มีประวัติการยืม")

    @override_settings(MEDIA_ROOT=MEDIA)
    def test_finished_requests_with_review_progress(self):
        services.cart_add(self.student, self.proj, 1)
        services.cart_add(self.student, self.hdmi, 1)
        req = services.submit_request(self.student)
        release(req)
        rr = services.notify_return(self.student, req, [(bi.pk, bi.qty, "NORMAL", "") for bi in req.items.all()], png())
        inspect(rr)
        services.cart_add(self.student, self.reload(self.paper)[0], 1)
        services.cancel_request(self.student, services.submit_request(self.student))
        r = self.client.get(reverse("borrow:history"))
        rows = {row["req"].status: row for row in r.context["rows"]}
        self.assertEqual(set(rows), {"RETURNED", "CANCELLED"})
        self.assertEqual((rows["RETURNED"]["reviewed"], rows["RETURNED"]["review_total"]), (0, 2))
        self.assertContains(r, "ประเมินแล้ว 0/2 ชิ้น")
        self.assertNotContains(r, f"คำขอ #{req.pk + 99}")
        r = self.client.get(reverse("borrow:history") + "?status=CANCELLED")
        self.assertEqual([row["req"].status for row in r.context["rows"]], ["CANCELLED"])


@override_settings(MEDIA_ROOT=MEDIA)
class ReportDamageTests(Fixture):
    """UC-38"""

    URL = reverse("borrow:report_damage")

    def test_room_device(self):
        r = self.client.post(self.URL, {"kind": "room", "item_name": "แอร์", "location": "ตึก EN ห้อง 304",
                                        "symptom": "ไม่เย็น", "photo": png()}, follow=True)
        d = DamageReport.objects.get()
        self.assertEqual((d.item, d.item_name, d.location, d.status), (None, "แอร์", "ตึก EN ห้อง 304", "PENDING"))
        self.assertTrue(d.photo)
        self.assertContains(r, "รอตรวจสอบ")

    def test_system_equipment_by_tag_without_borrow_history(self):
        self.client.post(self.URL, {"kind": "system", "asset_tag": "ubu-eq-001-01", "symptom": "เปิดไม่ติด"})
        d = DamageReport.objects.get()
        self.assertEqual(d.item_id, self.proj.pk)
        self.assertEqual(d.item_name, "โปรเจกเตอร์")

    def test_required_fields(self):
        r = self.client.post(self.URL, {"kind": "room", "symptom": ""})
        for k in ("item_name", "location", "symptom"):
            self.assertIn(k, r.context["errors"])
        r = self.client.post(self.URL, {"kind": "system", "asset_tag": "NOPE", "symptom": "x"})
        self.assertIn("ไม่พบรหัสครุภัณฑ์", r.context["errors"]["asset_tag"])
        self.assertFalse(DamageReport.objects.exists())

    def test_staff_damage_badge_counts_report(self):
        self.client.post(self.URL, {"kind": "room", "item_name": "ปลั๊ก", "location": "EN-1", "symptom": "ไหม้"})
        from accounts.tests_shell import make_staff
        self.client.force_login(make_staff())
        r = self.client.get(reverse("staff_inventory:item_overview"))
        menu = {m["key"]: m for m in r.context["nav_menu"]}
        self.assertEqual(menu["damaged-equipment"]["badge"], 1)


def tearDownModule():
    import shutil
    shutil.rmtree(MEDIA, ignore_errors=True)
