from django import template

from catalog.models import Item

register = template.Library()

ICONS = {Item.ItemType.EQUIPMENT: "📽️", Item.ItemType.DURABLE_MATERIAL: "🔌", Item.ItemType.MATERIAL: "📦"}


@register.filter
def item_icon(item):
    """emoji แทนรูปเมื่อสิ่งของยังไม่มีรูป (แบบ mockup)"""
    return ICONS.get(item.item_type, "📦")


@register.filter
def stock_pct(item):
    d = item.detail
    if not hasattr(d, "qty_total") or not d.qty_total:
        return 0
    return min(100, round(d.qty_available * 100 / d.qty_total))


@register.simple_tag
def query_with(page_query, **kwargs):
    """สร้าง query string ใหม่จากค่าเดิม + ค่าที่เปลี่ยน (ใช้กับปุ่มทางลัด / แบ่งหน้า)"""
    from django.http import QueryDict
    qd = QueryDict(page_query, mutable=True)
    for k, v in kwargs.items():
        if v in ("", None):
            qd.pop(k, None)
        else:
            qd[k] = v
    return qd.urlencode()
