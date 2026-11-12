"""M7 · staff_inventory — UC-20, UC-21, UC-22, UC-23 (UC-24 นำเข้า CSV เลื่อนไปก่อน)"""
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.permissions import role_required
from accounts.roles import STAFF
from catalog.models import Item
from catalog.selectors import AVAILABLE, EMPTY, HIDDEN, UNAVAILABLE, annotated_items, search_items

from . import services
from .forms import BulkStatusForm, ItemForm, StatusForm

PAGE_SIZE = 50
STATUS_FILTERS = {  # ตาม mockup page-item-overview.html
    AVAILABLE: "พร้อมให้ยืม", EMPTY: "กำลังยืมหมด", UNAVAILABLE: "ไม่พร้อมใช้งาน / ส่งซ่อม", "retired": "ปลดระวาง / ปิดใช้งาน",
}
TYPE_TAGS = [("", "ทั้งหมด"), (Item.ItemType.EQUIPMENT, "ครุภัณฑ์"),
             (Item.ItemType.DURABLE_MATERIAL, "วัสดุคงทน"), (Item.ItemType.MATERIAL, "วัสดุสิ้นเปลือง")]
OVERVIEW = "staff_inventory:item_overview"


def _apply_errors(form, err):
    errors = err.message_dict if hasattr(err, "error_dict") else {None: err.messages}
    for field, msgs in errors.items():
        form.add_error(field if field in form.fields else None, msgs)


@role_required(STAFF)
def item_overview_view(request):
    """UC-21 (InventoryOverviewView) · วัสดุ = แถวรวมจำนวน · ครุภัณฑ์ = 1 แถวต่อ asset tag"""
    q, item_type, status = request.GET.get("q", ""), request.GET.get("type", ""), request.GET.get("status", "")
    qs = search_items(annotated_items(), q=q, item_type=item_type, sort="name-asc")
    if status == "retired":
        qs = qs.filter(HIDDEN)
    elif status in (AVAILABLE, EMPTY, UNAVAILABLE):
        qs = qs.exclude(HIDDEN).filter(availability=status)
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    keep = request.GET.copy()
    keep.pop("page", None)
    return render(request, "staff_inventory/item_overview.html", {
        "page": page, "total": Item.objects.count(), "q": q, "item_type": item_type, "status": status,
        "status_filters": STATUS_FILTERS, "type_tags": TYPE_TAGS, "page_query": keep.urlencode(),
        "bulk_choices": services.EQUIPMENT_CHOICES,
    })


@role_required(STAFF)
def item_add_view(request):
    """UC-20 เพิ่มสิ่งของ (ItemAddEditView) · ครุภัณฑ์กรอก asset tag ทีละชิ้น"""
    form = ItemForm(request.POST or None, request.FILES or None, initial={"item_type": Item.ItemType.MATERIAL})
    asset_tags = request.POST.getlist("asset_tag")  # เพิ่มครุภัณฑ์ได้ครั้งละ 1 ชิ้น
    tag_error = None
    if request.method == "POST" and form.is_valid():
        t, common, sub = form.split()
        try:
            created = services.add_items(t, common, sub, asset_tags)
        except ValidationError as err:
            errors = err.message_dict if hasattr(err, "error_dict") else {None: err.messages}
            tag_error = (errors.pop("asset_tag", None) or [None])[0]
            for field, msgs in errors.items():
                form.add_error(field if field in form.fields else None, msgs)
        else:
            messages.success(request, f"เพิ่ม \"{created[0]}\" เข้าคลังเรียบร้อย")
            return redirect(OVERVIEW)
    return render(request, "staff_inventory/item_form.html", {
        "form": form, "item": None, "asset_tag": (asset_tags or [""])[0], "tag_error": tag_error,
        "type": form["item_type"].value() or Item.ItemType.MATERIAL,
    })


@role_required(STAFF)
def item_edit_view(request, pk):
    """UC-20 แก้ไขข้อมูลหลัก · เฉพาะชิ้นนี้ · ไม่แสดง/ไม่แก้ asset tag"""
    item = get_object_or_404(Item.objects.select_related("material", "durablematerial", "equipment"), pk=pk)
    d = item.detail
    initial = {
        "item_type": item.item_type, "name": item.name, "location": item.location, "unit": item.unit,
        "purchase_price": item.purchase_price, "description": item.description,
        "qty_total": getattr(d, "qty_total", None), "max_borrow_days": getattr(d, "max_borrow_days", None),
        "fine_rate_per_day": getattr(d, "fine_rate_per_day", None),
    }
    form = ItemForm(request.POST or None, request.FILES or None, item=item, initial=initial)
    if request.method == "POST" and form.is_valid():
        _, common, sub = form.split()
        try:
            services.update_item(item, common, sub)
        except ValidationError as err:
            _apply_errors(form, err)
        else:
            messages.success(request, f"บันทึกการแก้ไข \"{item.name}\" เรียบร้อย")
            return redirect(OVERVIEW)
    return render(request, "staff_inventory/item_form.html",
                  {"form": form, "item": item, "type": item.item_type})


@role_required(STAFF)
def equipment_status_view(request, pk):
    """UC-23 รูปแบบ 1 (EquipmentStatusUpdateView) · เฉพาะครุภัณฑ์ / วัสดุคงทน ชิ้นที่เลือก"""
    item = get_object_or_404(Item.objects.select_related("equipment", "durablematerial"), pk=pk)
    if item.is_material:
        messages.error(request, "วัสดุสิ้นเปลืองเปลี่ยนสถานะไม่ได้ ใช้การลบหรือปิดการใช้งานแทน")
        return redirect(OVERVIEW)
    current = item.equipment.status if item.is_equipment else item.base_status
    form = StatusForm(request.POST or None, item=item, initial={"status": current})
    on_loan = services.is_on_loan(item)
    if request.method == "POST" and not on_loan and form.is_valid():
        try:
            services.change_status(item, form.cleaned_data["status"], form.cleaned_data.get("note", ""))
        except ValidationError as err:
            form.add_error(None, err.messages)
        else:
            messages.success(request, f"เปลี่ยนสถานะ \"{item}\" เรียบร้อย")
            return redirect(OVERVIEW)
    return render(request, "staff_inventory/item_status.html", {"form": form, "item": item, "on_loan": on_loan})


@require_POST
@role_required(STAFF)
def bulk_status_view(request):
    """UC-23 รูปแบบ 2 · ข้ามชิ้นที่ถูกยืมแล้วแจ้งรายชื่อ (ตัดสินใจ M7 ข้อ 7)"""
    form = BulkStatusForm(request.POST)
    if not form.is_valid():
        messages.error(request, "กรุณาเลือกรายการและสถานะใหม่")
        return redirect(OVERVIEW)
    items = Item.objects.filter(pk__in=form.cleaned_data["ids"]).select_related("equipment")
    changed, on_loan, other = services.bulk_change_status(items, form.cleaned_data["status"], form.cleaned_data["note"])
    msg = f"เปลี่ยนสถานะแล้ว {len(changed)} ชิ้น"
    if on_loan:
        msg += f" · ข้าม {len(on_loan)} ชิ้นที่กำลังถูกยืม: {', '.join(i.equipment.asset_tag for i in on_loan)}"
    if other:
        msg += f" · ข้าม {len(other)} รายการที่ไม่ใช่ครุภัณฑ์"
    (messages.warning if (on_loan or other) else messages.success)(request, msg)
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect(OVERVIEW)


@role_required(STAFF)
def consumable_delete_view(request, pk):
    """UC-22 (ConsumableDeleteView) · ลบเฉพาะวัสดุสิ้นเปลืองที่ไม่เคยถูกเบิก"""
    item = get_object_or_404(Item.objects.select_related("material"), pk=pk)
    if not item.is_material:
        messages.error(request, "ลบได้เฉพาะวัสดุสิ้นเปลือง ครุภัณฑ์และวัสดุคงทนให้ใช้การเปลี่ยนสถานะแทน")
        return redirect(OVERVIEW)
    if request.method == "POST":
        try:
            name = item.name
            services.delete_material(item)
        except ValidationError as err:
            messages.error(request, err.messages[0])
        else:
            messages.success(request, f"ลบ \"{name}\" ออกจากระบบแล้ว")
            return redirect(OVERVIEW)
    return render(request, "staff_inventory/item_delete.html",
                  {"item": item, "has_history": services.has_history(item)})


@require_POST
@role_required(STAFF)
def bulk_delete_view(request):
    try:
        ids = [int(x) for x in request.POST.get("ids", "").split(",") if x.strip()]
    except ValueError:
        ids = []
    deleted, kept = services.bulk_delete_materials(Item.objects.filter(pk__in=ids))
    msg = f"ลบแล้ว {len(deleted)} รายการ"
    if kept:
        msg += f" · ลบไม่ได้ {len(kept)} รายการ (ไม่ใช่วัสดุสิ้นเปลือง หรือเคยถูกเบิกแล้ว): {', '.join(i.name for i in kept)}"
    (messages.warning if kept else messages.success)(request, msg)
    return redirect(OVERVIEW)


@require_POST
@role_required(STAFF)
def toggle_active_view(request, pk):
    """ปิด / เปิดการใช้งานวัสดุสิ้นเปลือง (ตัดสินใจ M7 ข้อ 2)"""
    item = get_object_or_404(Item, pk=pk)
    active = request.POST.get("active") == "1"
    try:
        services.set_active(item, active)
    except ValidationError as err:
        messages.error(request, err.messages[0])
    else:
        messages.success(request, f"{'เปิด' if active else 'ปิด'}การใช้งาน \"{item.name}\" แล้ว")
    return redirect(OVERVIEW)
