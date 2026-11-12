"""
M2 · catalog — สิ่งของตาม ERD: ITEM (supertype) + MATERIAL / DURABLE_MATERIAL / EQUIPMENT

ISA แบบ Disjoint + Total, subtype ใช้ shared primary key (`item_id`)
สร้างสิ่งของผ่าน catalog.services.create_item() เท่านั้น เพื่อให้มี subtype คู่กันเสมอ
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

MONEY = dict(max_digits=10, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0)])


class Item(models.Model):
    """ERD: ITEM — ข้อมูลที่ทั้ง 3 ประเภทใช้ร่วมกัน"""

    class ItemType(models.TextChoices):
        MATERIAL = "MATERIAL", "วัสดุสิ้นเปลือง"
        DURABLE_MATERIAL = "DURABLE_MATERIAL", "วัสดุคงทน"
        EQUIPMENT = "EQUIPMENT", "ครุภัณฑ์"

    class BaseStatus(models.TextChoices):
        AVAILABLE = "AVAILABLE", "พร้อมให้บริการ"
        DAMAGED = "DAMAGED", "ชำรุด"
        INACTIVE = "INACTIVE", "ปิดการใช้งาน"
        RETIRED = "RETIRED", "ปลดระวาง"

    item_type = models.CharField("ประเภทสิ่งของ", max_length=20, choices=ItemType.choices)
    name = models.CharField("ชื่อสิ่งของ", max_length=200)
    location = models.CharField("สถานที่ตั้งวางในคลัง", max_length=150, blank=True)
    unit = models.CharField("หน่วยนับ", max_length=30, default="ชิ้น")
    purchase_price = models.DecimalField("ราคาจัดซื้อ", **MONEY)
    base_status = models.CharField(
        "สถานะพื้นฐาน", max_length=20, choices=BaseStatus.choices, default=BaseStatus.AVAILABLE,
    )
    description = models.TextField("รายละเอียด", blank=True)
    image = models.ImageField("รูปภาพ", upload_to="items/", blank=True)

    class Meta:
        db_table = "item"
        verbose_name = "สิ่งของ (ITEM)"
        verbose_name_plural = "สิ่งของ (ITEM)"
        ordering = ["name", "id"]

    def __str__(self):
        if self.item_type == self.ItemType.EQUIPMENT and hasattr(self, "equipment"):
            return f"{self.name} [{self.equipment.asset_tag}]"
        return self.name

    # ---- ISA helpers -------------------------------------------------------
    SUBTYPE_ATTR = {
        ItemType.MATERIAL: "material",
        ItemType.DURABLE_MATERIAL: "durablematerial",
        ItemType.EQUIPMENT: "equipment",
    }

    @property
    def detail(self):
        """คืนแถว subtype ที่ตรงกับ item_type (Material / DurableMaterial / Equipment)"""
        return getattr(self, self.SUBTYPE_ATTR[self.item_type], None)

    @property
    def is_returnable(self):
        """ต้องส่งคืน: วัสดุคงทนและครุภัณฑ์"""
        return self.item_type in (self.ItemType.DURABLE_MATERIAL, self.ItemType.EQUIPMENT)

    @property
    def is_equipment(self):
        return self.item_type == self.ItemType.EQUIPMENT

    @property
    def is_material(self):
        return self.item_type == self.ItemType.MATERIAL

    def clean(self):
        """Disjoint: มี subtype ได้ตัวเดียวและต้องตรงกับ item_type"""
        if not self.pk:
            return
        present = [t for t, attr in self.SUBTYPE_ATTR.items() if hasattr(self, attr)]
        if len(present) > 1:
            raise ValidationError("สิ่งของ 1 รายการเป็นได้เพียง 1 ประเภทเท่านั้น")
        if present and present[0] != self.item_type:
            raise ValidationError({"item_type": "ประเภทสิ่งของไม่ตรงกับข้อมูลประเภทย่อย"})


class _Subtype(models.Model):
    """ฐานร่วมของ subtype: shared primary key + ตรวจว่า item_type ตรงกัน"""

    ITEM_TYPE = None

    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, primary_key=True, db_column="item_id", verbose_name="สิ่งของ",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.item)

    def clean(self):
        if self.item_id and self.item.item_type != self.ITEM_TYPE:
            raise ValidationError({"item": f"สิ่งของนี้ไม่ใช่ประเภท {Item.ItemType(self.ITEM_TYPE).label}"})


def _qty_constraints(prefix):
    return [
        models.CheckConstraint(condition=Q(qty_available__gte=0), name=f"{prefix}_qty_available_gte_0"),
        models.CheckConstraint(condition=Q(qty_available__lte=F("qty_total")), name=f"{prefix}_qty_available_lte_total"),
    ]


class Material(_Subtype):
    """ERD: MATERIAL — วัสดุสิ้นเปลือง นับจำนวน ไม่ต้องคืน"""

    ITEM_TYPE = Item.ItemType.MATERIAL

    qty_total = models.PositiveIntegerField("จำนวนทั้งหมด", default=0)
    qty_available = models.PositiveIntegerField("จำนวนคงเหลือ", default=0)

    class Meta:
        db_table = "material"
        verbose_name = "วัสดุสิ้นเปลือง (MATERIAL)"
        verbose_name_plural = "วัสดุสิ้นเปลือง (MATERIAL)"
        constraints = _qty_constraints("material")


class DurableMaterial(_Subtype):
    """ERD: DURABLE_MATERIAL — วัสดุคงทน นับจำนวน ต้องคืน มีค่าปรับ"""

    ITEM_TYPE = Item.ItemType.DURABLE_MATERIAL

    qty_total = models.PositiveIntegerField("จำนวนทั้งหมด", default=0)
    qty_available = models.PositiveIntegerField("จำนวนคงเหลือ", default=0)
    max_borrow_days = models.PositiveIntegerField("จำนวนวันยืมสูงสุด", default=7)
    fine_rate_per_day = models.DecimalField("อัตราค่าปรับต่อวัน", **MONEY)

    class Meta:
        db_table = "durable_material"
        verbose_name = "วัสดุคงทน (DURABLE_MATERIAL)"
        verbose_name_plural = "วัสดุคงทน (DURABLE_MATERIAL)"
        constraints = _qty_constraints("durable_material")


class Equipment(_Subtype):
    """ERD: EQUIPMENT — ครุภัณฑ์ 1 แถว = 1 ชิ้นตาม asset_tag"""

    ITEM_TYPE = Item.ItemType.EQUIPMENT

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "พร้อมให้ยืม"
        BORROWED = "BORROWED", "กำลังถูกยืม"
        RETURN_PENDING = "RETURN_PENDING", "รอตรวจรับคืน"
        DAMAGED = "DAMAGED", "ชำรุด"
        MAINTENANCE = "MAINTENANCE", "ส่งซ่อม"
        RETIRED = "RETIRED", "ปลดระวาง"
        LOST = "LOST", "สูญหาย"

    asset_tag = models.CharField("เลขครุภัณฑ์ประจำชิ้น", max_length=50, unique=True)
    max_borrow_days = models.PositiveIntegerField("จำนวนวันยืมสูงสุด", default=7)
    fine_rate_per_day = models.DecimalField("อัตราค่าปรับต่อวัน", **MONEY)
    status = models.CharField("สถานะรายชิ้น", max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    note = models.TextField("หมายเหตุสภาพ/ความเสียหาย", blank=True)

    class Meta:
        db_table = "equipment"
        verbose_name = "ครุภัณฑ์ (EQUIPMENT)"
        verbose_name_plural = "ครุภัณฑ์ (EQUIPMENT)"
        ordering = ["asset_tag"]
