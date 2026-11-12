from django import template

from catalog.models import Equipment, Item

register = template.Library()

GREEN = "bg-emerald-50 text-emerald-700 border-emerald-200"
RED = "bg-slate-800 text-white border-slate-800"
AMBER = "bg-amber-50 text-amber-800 border-amber-200"
GRAY = "bg-gray-100 text-gray-600 border-gray-200"

EQUIPMENT_BADGE = {
    Equipment.Status.AVAILABLE: ("✅ พร้อมใช้งาน", GREEN),
    Equipment.Status.BORROWED: ("📦 กำลังถูกยืม", RED),
    Equipment.Status.RETURN_PENDING: ("↩️ รอตรวจรับคืน", RED),
    Equipment.Status.DAMAGED: ("⚠️ ครุภัณฑ์เสียหาย", AMBER),
    Equipment.Status.MAINTENANCE: ("🛠️ ส่งซ่อมคลัง", AMBER),
    Equipment.Status.RETIRED: ("📦 ปลดระวาง", GRAY),
    Equipment.Status.LOST: ("❓ สูญหาย", GRAY),
}
BASE_BADGE = {
    Item.BaseStatus.DAMAGED: ("⚠️ ชำรุด", AMBER),
    Item.BaseStatus.INACTIVE: ("⏸️ ปิดใช้งาน / งดให้ยืม", GRAY),
    Item.BaseStatus.RETIRED: ("📦 ปลดระวาง", GRAY),
}


@register.inclusion_tag("staff_inventory/_status_badge.html")
def inventory_status(item):
    """ป้ายสถานะรายแถวของภาพรวมคลัง (UC-21)"""
    if item.is_equipment:
        label, css = EQUIPMENT_BADGE[item.equipment.status]
    elif item.base_status in BASE_BADGE:
        label, css = BASE_BADGE[item.base_status]
    elif item.detail.qty_available == 0:
        label, css = ("🔴 หมดคลัง", RED)
    else:
        label, css = ("✅ พร้อมใช้งาน", GREEN)
    return {"label": label, "css": css}
