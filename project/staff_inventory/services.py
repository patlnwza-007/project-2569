"""
M7 · staff_inventory — กฎธุรกิจของการจัดการคลัง (UC-20, UC-22, UC-23)
ข้อตัดสินใจอยู่ที่ docs/generated_mapping/M7_staff_inventory.md หัวข้อ 9
"""
from django.core.exceptions import ValidationError
from django.db import transaction

from borrow.models import BorrowItem
from catalog.models import Equipment, Item
from catalog.services import create_item

COMMON_FIELDS = ("name", "location", "unit", "purchase_price", "description", "image")
LOANED = (Equipment.Status.BORROWED, Equipment.Status.RETURN_PENDING)

# สถานะที่เจ้าหน้าที่เลือกเองได้ (BORROWED / RETURN_PENDING / LOST ระบบตั้งเองจากการยืม-คืน)
EQUIPMENT_CHOICES = [
    (Equipment.Status.AVAILABLE, "✅ พร้อมใช้งาน (พร้อมให้ยืม)"),
    (Equipment.Status.DAMAGED, "⚠️ ครุภัณฑ์เสียหาย"),
    (Equipment.Status.MAINTENANCE, "🛠️ ส่งซ่อมคลัง"),
    (Equipment.Status.RETIRED, "📦 ปลดระวาง (ไม่ต้องระบุเหตุผล)"),
]
DURABLE_CHOICES = [  # ตัดสินใจ M7 ข้อ 3
    (Item.BaseStatus.AVAILABLE, "✅ พร้อมใช้งาน"),
    (Item.BaseStatus.DAMAGED, "⚠️ ชำรุด"),
    (Item.BaseStatus.INACTIVE, "⏸️ งดให้ยืม"),
]


# ---- UC-20 เพิ่ม / แก้ไข -----------------------------------------------------
@transaction.atomic
def add_items(item_type, common, sub, asset_tags=()):
    """เพิ่มสิ่งของ · ครุภัณฑ์ N ชิ้น = N แถว คัดลอกข้อมูลรุ่นให้ทุกชิ้น (รหัสซ้ำ → ไม่บันทึกทั้งชุด)"""
    if item_type == Item.ItemType.EQUIPMENT:
        tags = [t.strip() for t in asset_tags]
        if not tags or any(not t for t in tags):
            raise ValidationError({"asset_tag": "กรุณากรอกรหัสครุภัณฑ์ให้ครบทุกชิ้น"})
        dup_in_form = sorted({t for t in tags if tags.count(t) > 1})
        if dup_in_form:
            raise ValidationError({"asset_tag": f"รหัสครุภัณฑ์ซ้ำกันในฟอร์ม: {', '.join(dup_in_form)}"})
        dup_in_db = list(Equipment.objects.filter(asset_tag__in=tags).values_list("asset_tag", flat=True))
        if dup_in_db:
            raise ValidationError({"asset_tag": f"รหัสครุภัณฑ์นี้มีในระบบแล้ว: {', '.join(sorted(dup_in_db))}"})
        return [create_item(item_type, **common, **sub, asset_tag=t) for t in tags]
    return [create_item(item_type, **common, **sub)]


@transaction.atomic
def update_item(item, common, sub):
    """แก้ไขข้อมูลหลัก (เฉพาะชิ้นนี้ — ตัดสินใจ M7 ข้อ 4) · ไม่แก้ประเภทและ asset tag"""
    for k, v in common.items():
        setattr(item, k, v)
    item.full_clean()
    item.save()
    detail = item.detail
    if "qty_total" in sub:  # ตัดสินใจ M7 ข้อ 5: ปรับคงเหลือตามส่วนต่าง ห้ามติดลบ
        new_total = sub.pop("qty_total")
        new_available = detail.qty_available + (new_total - detail.qty_total)
        if new_available < 0:
            in_use = detail.qty_total - detail.qty_available
            raise ValidationError({"qty_total": f"จำนวนทั้งหมดต้องไม่น้อยกว่า {in_use} เพราะกำลังถูกยืม/เบิกอยู่ {in_use} {item.unit}"})
        detail.qty_total, detail.qty_available = new_total, new_available
    for k, v in sub.items():
        setattr(detail, k, v)
    detail.full_clean()
    detail.save()
    return item


# ---- UC-23 เปลี่ยนสถานะ ------------------------------------------------------
def is_on_loan(item):
    return item.is_equipment and item.equipment.status in LOANED


def change_status(item, status, note=""):
    """เปลี่ยนสถานะรายชิ้น · ครุภัณฑ์ → Equipment.status (+note) · วัสดุคงทน → Item.base_status"""
    note = (note or "").strip()
    if item.is_equipment:
        if is_on_loan(item):
            raise ValidationError("ครุภัณฑ์ชิ้นนี้กำลังถูกยืมอยู่ เปลี่ยนสถานะได้หลังตรวจรับคืนสำเร็จ")
        if status not in dict(EQUIPMENT_CHOICES):
            raise ValidationError({"status": "สถานะไม่ถูกต้อง"})
        eq = item.equipment
        eq.status = status
        if note:
            eq.note = note
        eq.save(update_fields=["status", "note"])
    elif item.item_type == Item.ItemType.DURABLE_MATERIAL:
        if status not in dict(DURABLE_CHOICES):
            raise ValidationError({"status": "สถานะไม่ถูกต้อง"})
        item.base_status = status
        item.save(update_fields=["base_status"])
    else:
        raise ValidationError("เปลี่ยนสถานะได้เฉพาะครุภัณฑ์และวัสดุคงทน")


@transaction.atomic
def bulk_change_status(items, status, note=""):
    """UC-23 รูปแบบ 2: เปลี่ยนเฉพาะครุภัณฑ์ที่ไม่ได้ถูกยืม · คืน (เปลี่ยนแล้ว, ข้ามเพราะถูกยืม, ข้ามเพราะไม่ใช่ครุภัณฑ์)"""
    changed, on_loan, not_equipment = [], [], []
    for item in items:
        if not item.is_equipment:
            not_equipment.append(item)
        elif is_on_loan(item):
            on_loan.append(item)
        else:
            change_status(item, status, note)
            changed.append(item)
    return changed, on_loan, not_equipment


# ---- UC-22 ลบวัสดุ / ปิดการใช้งาน -------------------------------------------
def has_history(item):
    return BorrowItem.objects.filter(item=item).exists()


def can_delete(item):
    """ลบถาวรได้เฉพาะวัสดุสิ้นเปลืองที่ไม่เคยถูกเบิก (ตัดสินใจ M7 ข้อ 2)"""
    return item.is_material and not has_history(item)


def delete_material(item):
    if not item.is_material:
        raise ValidationError("ลบได้เฉพาะวัสดุสิ้นเปลือง ครุภัณฑ์และวัสดุคงทนให้ใช้การเปลี่ยนสถานะแทน")
    if has_history(item):
        raise ValidationError("วัสดุนี้เคยถูกเบิกแล้ว ลบไม่ได้เพื่อรักษาประวัติ ให้ใช้ \"ปิดการใช้งาน\" แทน")
    item.delete()


@transaction.atomic
def bulk_delete_materials(items):
    deleted, kept = [], []
    for item in items:
        if can_delete(item):
            deleted.append(item.name)
            item.delete()
        else:
            kept.append(item)
    return deleted, kept


def set_active(item, active):
    """ปิด / เปิดการใช้งานวัสดุสิ้นเปลือง (INACTIVE = นักศึกษามองไม่เห็น แต่ประวัติอยู่ครบ)"""
    if not item.is_material:
        raise ValidationError("ใช้ได้เฉพาะวัสดุสิ้นเปลือง")
    item.base_status = Item.BaseStatus.AVAILABLE if active else Item.BaseStatus.INACTIVE
    item.save(update_fields=["base_status"])
