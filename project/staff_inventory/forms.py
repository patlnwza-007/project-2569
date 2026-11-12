from decimal import Decimal

from django import forms
from django.core.validators import FileExtensionValidator

from catalog.models import Item

from .services import DURABLE_CHOICES, EQUIPMENT_CHOICES

MAX_IMAGE_MB = 5  # ตัดสินใจ M7 ข้อ 8
INPUT = ("w-full border border-gray-300 rounded-xl px-3.5 py-2 text-sm focus:outline-none "
         "focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500")


def _style(form):
    for name, field in form.fields.items():
        if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput, forms.RadioSelect)):
            field.widget.attrs.setdefault("class", INPUT)


class ItemForm(forms.Form):
    """UC-20 · ฟอร์มเดียวใช้ทั้งเพิ่มและแก้ไข · ช่องตามประเภทแสดงด้วย Alpine.js"""

    item_type = forms.ChoiceField(label="ประเภทสิ่งของ", choices=Item.ItemType.choices)
    name = forms.CharField(label="ชื่อสิ่งของ", max_length=200)
    location = forms.CharField(label="ตำแหน่งจัดเก็บในคลัง", max_length=150, required=False)
    unit = forms.CharField(label="หน่วยนับ", max_length=30, initial="ชิ้น")
    purchase_price = forms.DecimalField(label="ราคาจัดซื้อเดิม (บาท)", max_digits=10, decimal_places=2,
                                        min_value=Decimal("0"), initial=Decimal("0"), required=False)
    description = forms.CharField(label="รายละเอียดและคุณลักษณะ", widget=forms.Textarea(attrs={"rows": 3}), required=False)
    image = forms.ImageField(label="รูปภาพ", required=False,
                             validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])])
    remove_image = forms.BooleanField(label="ลบรูปเดิม", required=False)

    qty_total = forms.IntegerField(label="จำนวนทั้งหมด", min_value=0, required=False)
    max_borrow_days = forms.IntegerField(label="จำนวนวันยืมสูงสุด", min_value=1, initial=7, required=False)
    fine_rate_per_day = forms.DecimalField(label="อัตราค่าปรับต่อวัน (บาท)", max_digits=10, decimal_places=2,
                                           min_value=Decimal("0"), initial=Decimal("0"), required=False)

    def __init__(self, *args, item=None, **kwargs):
        self.item = item
        super().__init__(*args, **kwargs)
        _style(self)
        self.fields["item_type"].widget.attrs["x-model"] = "type"
        if item is not None:  # แก้ไข: เปลี่ยนประเภทไม่ได้ (ISA disjoint)
            self.fields["item_type"].disabled = True
        else:
            del self.fields["remove_image"]

    def clean_image(self):
        img = self.cleaned_data.get("image")
        if img and hasattr(img, "size") and img.size > MAX_IMAGE_MB * 1024 * 1024:
            raise forms.ValidationError(f"ไฟล์รูปภาพต้องไม่เกิน {MAX_IMAGE_MB} MB")
        return img

    def clean(self):
        data = super().clean()
        t = data.get("item_type") or (self.item.item_type if self.item else None)
        need = {
            Item.ItemType.MATERIAL: ["qty_total"],
            Item.ItemType.DURABLE_MATERIAL: ["qty_total", "max_borrow_days"],
            Item.ItemType.EQUIPMENT: ["max_borrow_days"],
        }.get(t, [])
        for f in need:
            if data.get(f) in (None, ""):
                self.add_error(f, "กรุณากรอกช่องนี้")
        if data.get("purchase_price") is None:
            data["purchase_price"] = Decimal("0")
        if data.get("fine_rate_per_day") is None:
            data["fine_rate_per_day"] = Decimal("0")
        return data

    def split(self):
        """แยกข้อมูลเป็น (ส่วนกลาง ITEM, ส่วน subtype) ตามประเภท"""
        d = self.cleaned_data
        t = self.item.item_type if self.item else d["item_type"]
        common = {k: d[k] for k in ("name", "location", "unit", "purchase_price", "description")}
        if d.get("image"):
            common["image"] = d["image"]
        elif d.get("remove_image"):
            common["image"] = None
        sub = {}
        if t in (Item.ItemType.MATERIAL, Item.ItemType.DURABLE_MATERIAL):
            sub["qty_total"] = d["qty_total"]
        if t in (Item.ItemType.DURABLE_MATERIAL, Item.ItemType.EQUIPMENT):
            sub["max_borrow_days"] = d["max_borrow_days"]
            sub["fine_rate_per_day"] = d["fine_rate_per_day"]
        return t, common, sub


class StatusForm(forms.Form):
    """UC-23 รายชิ้น · หมายเหตุบังคับ ยกเว้นปลดระวาง (ครุภัณฑ์) · วัสดุคงทนไม่มีช่องหมายเหตุ (ERD ไม่มีคอลัมน์)"""

    status = forms.ChoiceField(label="สถานะใหม่", widget=forms.RadioSelect)
    note = forms.CharField(label="หมายเหตุสภาพ / เหตุผล", widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def __init__(self, *args, item, **kwargs):
        self.item = item
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = EQUIPMENT_CHOICES if item.is_equipment else DURABLE_CHOICES
        if not item.is_equipment:
            del self.fields["note"]
        _style(self)

    def clean(self):
        data = super().clean()
        if self.item.is_equipment and data.get("status") and data["status"] != "RETIRED" \
                and not (data.get("note") or "").strip():
            self.add_error("note", "กรุณาระบุหมายเหตุ/สาเหตุ (ยกเว้นการปลดระวาง)")
        return data


class BulkStatusForm(forms.Form):
    """UC-23 แบบกลุ่ม · หมายเหตุไม่บังคับ (ตาม mockup)"""

    ids = forms.CharField()
    status = forms.ChoiceField(choices=EQUIPMENT_CHOICES)
    note = forms.CharField(required=False)

    def clean_ids(self):
        try:
            return [int(x) for x in self.cleaned_data["ids"].split(",") if x.strip()]
        except ValueError:
            raise forms.ValidationError("รายการที่เลือกไม่ถูกต้อง")
