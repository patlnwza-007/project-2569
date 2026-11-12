from django.db import transaction

from .models import DurableMaterial, Equipment, Item, Material

SUBTYPE_MODEL = {
    Item.ItemType.MATERIAL: Material,
    Item.ItemType.DURABLE_MATERIAL: DurableMaterial,
    Item.ItemType.EQUIPMENT: Equipment,
}
SUBTYPE_FIELDS = {
    Item.ItemType.MATERIAL: {"qty_total", "qty_available"},
    Item.ItemType.DURABLE_MATERIAL: {"qty_total", "qty_available", "max_borrow_days", "fine_rate_per_day"},
    Item.ItemType.EQUIPMENT: {"asset_tag", "max_borrow_days", "fine_rate_per_day", "status", "note"},
}


@transaction.atomic
def create_item(item_type, **fields):
    """สร้าง ITEM + subtype พร้อมกัน (Total participation ของ ISA)

    ตัวอย่าง: create_item(Item.ItemType.EQUIPMENT, name="โปรเจกเตอร์", asset_tag="UBU-EQ-001-01")
    ถ้าไม่ระบุ qty_available ให้เท่ากับ qty_total
    """
    item_type = Item.ItemType(item_type)
    sub_fields = {k: fields.pop(k) for k in list(fields) if k in SUBTYPE_FIELDS[item_type]}
    if "qty_total" in sub_fields:
        sub_fields.setdefault("qty_available", sub_fields["qty_total"])

    item = Item(item_type=item_type, **fields)
    item.full_clean()
    item.save()

    sub = SUBTYPE_MODEL[item_type](item=item, **sub_fields)
    sub.full_clean()
    sub.save()
    return item
