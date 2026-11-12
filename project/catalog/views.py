"""M2 · catalog — UC-01, UC-02, UC-03, UC-37"""
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.urls import NoReverseMatch, reverse

from accounts.navigation import NAV_BY_KEY, _cart_qty, item_url
from accounts.permissions import role_required
from accounts.roles import STAFF, STUDENT, get_role, get_ubu_user
from borrow.models import BorrowItem, BorrowRequest
from evaluation.models import Review

from .models import Item
from .selectors import DEFAULT_SORT, SORTS, STATUS_CHOICES, annotated_items, search_items, student_items

PAGE_SIZE = 24  # ตัดสินใจ M2 ข้อ 6
TYPE_TAGS = [  # ปุ่มทางลัด (ตัดสินใจ M2 ข้อ 2)
    ("", "", "ทั้งหมด"),
    ("", "available", "พร้อมให้ยืม"),
    (Item.ItemType.EQUIPMENT, "", "ครุภัณฑ์"),
    (Item.ItemType.DURABLE_MATERIAL, "", "วัสดุคงทน"),
    (Item.ItemType.MATERIAL, "", "วัสดุสิ้นเปลือง"),
]
SORT_LABELS = {
    "qty-desc": "จำนวนคงเหลือมากสุด", "qty-asc": "จำนวนคงเหลือน้อยสุด",
    "name-asc": "ชื่อสิ่งของ (ก-ฮ)", "days-desc": "ยืมได้นานที่สุด",
}


def _url_or_none(name):
    """ปุ่มตะกร้า/คิวกดได้เมื่อ M3 สร้าง URL แล้ว (ตัดสินใจ M2 ข้อ 4)"""
    try:
        reverse(name, args=[0])
        return True
    except NoReverseMatch:
        return False


def _borrow_actions_ready():
    return {"cart_ready": _url_or_none("borrow:cart_add"), "queue_ready": _url_or_none("borrow:queue_join")}


@role_required(STUDENT)
def item_list_view(request):
    """UC-01 ดูรายการ + UC-02 ค้นหา/กรอง (ItemListView) · ?q=&type=&status=&sort=&page="""
    q = request.GET.get("q", "")
    item_type = request.GET.get("type", "")
    status = request.GET.get("status", "")
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in SORTS:
        sort = DEFAULT_SORT

    base = student_items()
    total = base.count()
    results = search_items(base, q=q, item_type=item_type, status=status, sort=sort)
    page = Paginator(results, PAGE_SIZE).get_page(request.GET.get("page"))

    keep = request.GET.copy()
    keep.pop("page", None)
    filtering = bool(q.strip() or item_type or status)
    return render(request, "catalog/item_list.html", {
        "page": page, "total": total, "filtering": filtering,
        "q": q, "item_type": item_type, "status": status, "sort": sort,
        "status_choices": STATUS_CHOICES, "sort_labels": SORT_LABELS, "type_tags": TYPE_TAGS,
        "page_query": keep.urlencode(),
        "cart_qty": _cart_qty(get_ubu_user(request.user)),
        "cart_url": item_url(NAV_BY_KEY["cart"][1])[0],
        **_borrow_actions_ready(),
    })


@role_required(STUDENT, STAFF)
def item_detail_view(request, pk):
    """UC-03 รายละเอียด + UC-37 แท็บรีวิว (ItemDetailView / UnitReviewListView) · ?tab=reviews&stars=N"""
    role = get_role(request.user)
    qs = student_items() if role == STUDENT else annotated_items()  # นักศึกษาไม่เห็นของที่ซ่อน (ข้อ 3)
    item = get_object_or_404(qs, pk=pk)

    ctx = {"item": item, "role": role, "tab": "details"}
    if item.is_equipment:
        reviews = Review.objects.filter(borrow_item__item=item).select_related(
            "borrow_item__borrow_request__student__user")
        counts = dict(reviews.values_list("rating").annotate(n=Count("id")))
        total = sum(counts.values())
        stars = request.GET.get("stars", "")
        shown = reviews.filter(rating=int(stars)) if stars in {"1", "2", "3", "4", "5"} else reviews
        ctx.update({
            "tab": "reviews" if request.GET.get("tab") == "reviews" else "details",
            "reviews": shown, "stars": stars, "review_total": total,
            "star_rows": [(n, counts.get(n, 0), round(counts.get(n, 0) * 100 / total) if total else 0)
                          for n in range(5, 0, -1)],
        })
    if role == STAFF and item.is_returnable:  # ที่ตั้งปัจจุบัน: เจ้าหน้าที่เท่านั้น (ข้อ 7)
        ctx["active_loan"] = (
            BorrowItem.objects.filter(
                item=item,
                borrow_request__status__in=[BorrowRequest.Status.BORROWING, BorrowRequest.Status.RETURN_PENDING],
            ).exclude(current_location="").select_related("borrow_request__student__user")
            .order_by("-moved_at").first()
        )
    back_key = "item-list" if role == STUDENT else "item-overview"
    ctx["back_url"] = item_url(NAV_BY_KEY[back_key][1])[0]
    ctx.update(_borrow_actions_ready())
    return render(request, "catalog/item_detail.html", ctx)
