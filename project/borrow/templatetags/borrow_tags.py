from django import template

from borrow.models import BorrowRequest

register = template.Library()

S = BorrowRequest.Status
REQUEST_BADGE = {
    S.PENDING: ("⏳ รอเจ้าหน้าที่ตรวจของ", "bg-amber-50 text-amber-800 border-amber-200"),
    S.BORROWING: ("📦 กำลังยืม", "bg-blue-50 text-blue-700 border-blue-200"),
    S.RETURN_PENDING: ("↩️ รอตรวจรับคืน", "bg-purple-50 text-purple-700 border-purple-200"),
    S.ISSUED: ("✅ เบิกสำเร็จ", "bg-emerald-50 text-emerald-700 border-emerald-200"),
    S.RETURNED: ("✅ คืนสำเร็จ", "bg-emerald-50 text-emerald-700 border-emerald-200"),
    S.REJECTED: ("❌ ไม่อนุมัติ", "bg-red-50 text-red-700 border-red-200"),
    S.CANCELLED: ("🚫 ยกเลิกแล้ว", "bg-gray-100 text-gray-600 border-gray-200"),
    S.EXPIRED: ("⌛ หมดอายุแล้ว", "bg-gray-100 text-gray-600 border-gray-200"),
}


@register.inclusion_tag("borrow/_request_badge.html")
def request_badge(status):
    label, css = REQUEST_BADGE.get(status, (status, "bg-gray-100 text-gray-600 border-gray-200"))
    return {"label": label, "css": css}
