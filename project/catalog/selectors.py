"""
คำค้นสิ่งของสำหรับหน้ารายการ / รายละเอียด (M2 · UC-01, UC-02, UC-03, UC-37)
สูตรสถานะอยู่ที่ docs/generated_mapping/M2_catalog.md หัวข้อ 2
"""
from django.db.models import Avg, Case, CharField, Count, IntegerField, Q, Value, When
from django.db.models.functions import Coalesce

from .models import Equipment, Item

AVAILABLE, EMPTY, UNAVAILABLE = "available", "empty", "unavailable"
STATUS_CHOICES = {AVAILABLE: "พร้อมให้ยืม", EMPTY: "ถูกยืมหมด", UNAVAILABLE: "ไม่พร้อมใช้งาน"}
SORTS = {
    "qty-desc": ("-qty_now", "name", "id"),
    "qty-asc": ("qty_now", "name", "id"),
    "name-asc": ("name", "id"),
    "days-desc": ("-borrow_days", "name", "id"),
}
DEFAULT_SORT = "qty-desc"

# ซ่อนจากนักศึกษา (ตัดสินใจ M2 ข้อ 3)
HIDDEN = Q(base_status__in=[Item.BaseStatus.INACTIVE, Item.BaseStatus.RETIRED]) | Q(
    equipment__status__in=[Equipment.Status.RETIRED, Equipment.Status.LOST]
)

_EQ = Item.ItemType.EQUIPMENT
_availability = Case(
    When(base_status=Item.BaseStatus.DAMAGED, then=Value(UNAVAILABLE)),
    When(item_type=_EQ, equipment__status=Equipment.Status.AVAILABLE, then=Value(AVAILABLE)),
    When(item_type=_EQ, equipment__status__in=[Equipment.Status.BORROWED, Equipment.Status.RETURN_PENDING],
         then=Value(EMPTY)),
    When(item_type=_EQ, then=Value(UNAVAILABLE)),  # DAMAGED / MAINTENANCE
    When(material__qty_available__gt=0, then=Value(AVAILABLE)),
    When(durablematerial__qty_available__gt=0, then=Value(AVAILABLE)),
    default=Value(EMPTY),
    output_field=CharField(),
)


def annotated_items():
    """Item + subtype พร้อมค่า availability, qty_now, borrow_days, rating_avg, review_count"""
    return (
        Item.objects.select_related("material", "durablematerial", "equipment")
        .annotate(
            availability=_availability,
            qty_now=Coalesce(
                "material__qty_available", "durablematerial__qty_available",
                Case(When(item_type=_EQ, equipment__status=Equipment.Status.AVAILABLE, then=Value(1)),
                     default=Value(0), output_field=IntegerField()),
            ),
            borrow_days=Coalesce("durablematerial__max_borrow_days", "equipment__max_borrow_days", Value(0)),
            rating_avg=Avg("borrow_items__review__rating"),
            review_count=Count("borrow_items__review", distinct=True),
        )
    )


def student_items():
    return annotated_items().exclude(HIDDEN)


def search_items(qs, q="", item_type="", status="", sort=DEFAULT_SORT):
    """UC-02: ค้นหาชื่อ / asset tag, กรองประเภทและสถานะ, เรียงลำดับ"""
    q = (q or "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(equipment__asset_tag__icontains=q))
    if item_type in Item.ItemType.values:
        qs = qs.filter(item_type=item_type)
    if status in STATUS_CHOICES:
        qs = qs.filter(availability=status)
    return qs.order_by(*SORTS.get(sort, SORTS[DEFAULT_SORT]))
