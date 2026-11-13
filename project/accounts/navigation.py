"""
เมนู Side Bar ตามบทบาท — ตาม docs/proposal/mapping/00_shell_navigation.md และ MENU ใน mockup shared.js

แต่ละเมนูระบุ url_name ของหน้าจริงไว้ล่วงหน้า ถ้า module นั้นยังไม่ได้ทำ (reverse ไม่เจอ)
เมนูจะชี้ไปหน้า "ยังไม่เปิดใช้งาน" ให้เอง → ทำหน้าเสร็จเมื่อไหร่ เมนูใช้ได้ทันทีโดยไม่ต้องแก้ไฟล์นี้
"""
from dataclasses import dataclass
from typing import Callable, Optional

from django.db.models import Sum
from django.urls import NoReverseMatch, reverse

from .roles import ADMIN, STAFF, STUDENT

ROLE_LABEL = {STUDENT: "นักศึกษา", STAFF: "เจ้าหน้าที่", ADMIN: "ผู้ดูแลระบบ"}


# ---- ตัวเลขแจ้งเตือน (badge) ตามสูตรใน 00_shell_navigation.md -------------------
def _cart_qty(ubu):
    from borrow.models import CartItem
    return CartItem.objects.filter(cart__student__user=ubu).aggregate(s=Sum("qty"))["s"] or 0


def _my_queue(ubu):
    from borrow.models import Queue
    return Queue.objects.filter(
        student__user=ubu, status__in=[Queue.Status.WAITING, Queue.Status.NOTIFIED],
    ).count()


def _pending_requests(_):
    from borrow.models import BorrowRequest
    return BorrowRequest.objects.filter(status=BorrowRequest.Status.PENDING).count()


def _pending_returns(_):
    from borrow.models import ReturnRequest
    return ReturnRequest.objects.filter(status=ReturnRequest.Status.RETURN_PENDING).count()


def _damaged(_):
    from borrow.models import DamageReport
    from catalog.models import Equipment
    return (
        Equipment.objects.filter(status=Equipment.Status.DAMAGED).count()
        + DamageReport.objects.filter(status=DamageReport.Status.PENDING).count()
    )


def _new_suggestions(_):
    from suggestion.models import Suggestion
    return Suggestion.objects.filter(status=Suggestion.Status.SUBMITTED).count()


@dataclass(frozen=True)
class NavItem:
    key: str                     # ชื่อหน้าใน mockup (page-<key>.html)
    label: str
    icon: str
    url_name: str                # หน้าจริงที่จะทำในเฟส 3
    badge: Optional[Callable] = None


MENU = {
    STUDENT: [
        NavItem("request-list", "หน้าหลัก", "🏠", "borrow:request_list"),
        NavItem("profile", "โปรไฟล์ส่วนตัว", "👤", "accounts:profile"),
        NavItem("item-list", "รายการวัสดุ/ครุภัณฑ์", "📋", "catalog:item_list"),
        NavItem("cart", "ตะกร้า", "🛒", "borrow:cart", _cart_qty),
        NavItem("queue-list", "คิวของฉัน", "⏳", "borrow:queue_list", _my_queue),
        NavItem("history", "ประวัติการยืม", "📜", "borrow:history"),
        NavItem("report-damage", "แจ้งอุปกรณ์ชำรุด", "🛠️", "borrow:report_damage"),
        NavItem("suggestion", "เสนอแนะสิ่งของ", "💡", "suggestion:create"),
    ],
    STAFF: [
        NavItem("staff-dashboard", "แดชบอร์ด", "📊", "staff:dashboard"),
        NavItem("pending-requests", "คำขอรออนุมัติ", "✅", "staff:pending_requests", _pending_requests),
        NavItem("return-list", "รับคืนครุภัณฑ์", "↩️", "staff:return_list", _pending_returns),
        NavItem("damaged-equipment", "ครุภัณฑ์เสียหาย", "⚠️", "staff:damaged_equipment", _damaged),
        NavItem("all-history", "ประวัติทั้งระบบ", "📜", "staff:all_history"),
        NavItem("item-overview", "จัดการคลังสิ่งของ", "📦", "staff_inventory:item_overview"),
        NavItem("student-list", "รายชื่อนักศึกษา", "🎓", "staff_student:student_list"),
        NavItem("suggestion-review", "คำเสนอแนะสิ่งของ", "💡", "suggestion:review", _new_suggestions),
        NavItem("purchase-add", "รายการจัดซื้อ", "🧾", "suggestion:purchase_plan"),
        NavItem("report-export", "ส่งออกรายงาน", "📤", "staff_report:export"),
    ],
    ADMIN: [
        NavItem("user-list", "จัดการบัญชีและสิทธิ์ผู้ใช้", "👥", "admin_panel:user_list"),
        NavItem("personnel-export", "ส่งออกรายชื่อผู้ใช้งาน (CSV)", "📤", "admin_panel:personnel_export"),
    ],
}

NAV_BY_KEY = {item.key: (role, item) for role, items in MENU.items() for item in items}


def url_ready(name, *args):
    """หน้านี้ทำแล้วหรือยัง (ใช้เปิดปุ่มที่ชี้ไปหน้าของ module อื่นเมื่อ module นั้นเสร็จ)"""
    try:
        reverse(name, args=args)
        return True
    except NoReverseMatch:
        return False


def item_url(item):
    """URL ของหน้าจริง ถ้ายังไม่มีให้ชี้หน้า 'ยังไม่เปิดใช้งาน'"""
    try:
        return reverse(item.url_name), True
    except NoReverseMatch:
        return reverse("coming_soon", args=[item.key]), False


def home_url(role):
    """UC-15 ข้อ 5: หน้าแรกหลัง login = เมนูแรกของบทบาทนั้น"""
    return item_url(MENU[role][0])[0]


def build_menu(role, ubu_user, current_path):
    entries = []
    for item in MENU.get(role, []):
        url, ready = item_url(item)
        badge = item.badge(ubu_user) if item.badge else 0
        entries.append({
            "key": item.key, "label": item.label, "icon": item.icon,
            "url": url, "ready": ready, "active": False, "badge": badge,
        })
    # เมนูที่ตรงที่สุดเท่านั้นที่ active (เช่น /borrow/cart/ → "ตะกร้า" ไม่ใช่ "หน้าหลัก" /borrow/)
    matches = [e for e in entries if current_path == e["url"]
               or (e["ready"] and e["url"] != "/" and current_path.startswith(e["url"]))]
    if matches:
        max(matches, key=lambda e: len(e["url"]))["active"] = True
    return entries
