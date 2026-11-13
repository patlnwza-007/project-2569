"""
กำหนดคืนและค่าปรับรายชิ้น (ERD หัวข้อ "กำหนดคืนและค่าปรับรายชิ้น")
ฟังก์ชันล้วน ทดสอบได้โดยไม่ต้องมีหน้าจอ · ใช้ตอน UC-17 (ปล่อยของ) และ UC-18 (ตรวจรับคืน)
"""
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import Queue

QUEUE_CONFIRM_WINDOW = timedelta(days=1)


def compute_due_date(borrow_item, release_date):
    """UC-17: วันครบกำหนดคืนของ BORROW_ITEM

    วัสดุสิ้นเปลือง → None · คำขอกรณีพิเศษ → custom_due_date · อื่น ๆ → วันปล่อยของ + max_borrow_days
    """
    item = borrow_item.item
    if not item.is_returnable:
        return None
    request = borrow_item.borrow_request
    if request.is_special and request.custom_due_date:
        return request.custom_due_date
    return release_date + timedelta(days=item.detail.max_borrow_days)


def compute_fine(borrow_item, return_date, qty_returned):
    """UC-18: ค่าปรับ = max(0, วันที่คืน − due_date) × fine_rate_per_day × qty_returned"""
    if borrow_item.due_date is None:
        return Decimal("0.00")
    days_late = max(0, (return_date - borrow_item.due_date).days)
    rate = borrow_item.item.detail.fine_rate_per_day
    return (Decimal(days_late) * rate * qty_returned).quantize(Decimal("0.01"))


def expire_queues(now=None):
    """UC-10: คิวที่แจ้งเตือนแล้วแต่ไม่ยืนยันภายใน 1 วัน → EXPIRED · คืนจำนวนคิวที่หมดอายุ"""
    now = now or timezone.now()
    return Queue.objects.filter(
        status=Queue.Status.NOTIFIED, notified_at__lte=now - QUEUE_CONFIRM_WINDOW,
    ).update(status=Queue.Status.EXPIRED, expired_at=now)


# =============================================================================
# M3 รอบ 3a · ตะกร้า (UC-05) · ส่งคำขอ (UC-06) · ยกเลิก (UC-07) · แจ้งย้ายที่ตั้ง
# ข้อตัดสินใจ: docs/generated_mapping/M3_borrow.md หัวข้อ 8
# =============================================================================
from django.core.exceptions import ValidationError  # noqa: E402
from django.db import transaction  # noqa: E402

from catalog.models import DurableMaterial, Equipment, Item, Material  # noqa: E402

from .models import BorrowItem, BorrowRequest, Cart, CartItem  # noqa: E402

HIDDEN_BASE = (Item.BaseStatus.INACTIVE, Item.BaseStatus.RETIRED)


def available_qty(item):
    """จำนวนที่ยืม/เบิกได้ตอนนี้ (ครุภัณฑ์ = 1 หรือ 0) · ใช้ตรวจ "ตัดหน้า" ทุกครั้ง (Anti-Snipe)"""
    if item.base_status != Item.BaseStatus.AVAILABLE:
        return 0
    if item.is_equipment:
        return 1 if item.equipment.status == Equipment.Status.AVAILABLE else 0
    return item.detail.qty_available


def get_cart(student):
    cart, _ = Cart.objects.get_or_create(student=student)
    return cart


def cart_add(student, item, qty=1):
    """UC-05: ใส่ตะกร้า · กดซ้ำ = เพิ่มจำนวน · ครุภัณฑ์ได้ 1 ชิ้น · ห้ามเกินคงเหลือ"""
    if item.base_status in HIDDEN_BASE or (item.is_equipment and item.equipment.status in
                                            (Equipment.Status.RETIRED, Equipment.Status.LOST)):
        raise ValidationError("ไม่พบสิ่งของนี้")
    qty = int(qty)
    if qty < 1:
        raise ValidationError("จำนวนต้องมากกว่า 0")
    available = available_qty(item)
    if available == 0:
        raise ValidationError(f"\"{item}\" ไม่พร้อมให้ยืมในขณะนี้")
    cart = get_cart(student)
    line = cart.items.filter(item=item).first()
    if item.is_equipment:
        if line:
            raise ValidationError(f"\"{item}\" อยู่ในตะกร้าแล้ว")
        qty = 1
    new_qty = (line.qty if line else 0) + qty
    if new_qty > available:
        raise ValidationError(f"\"{item.name}\" คงเหลือ {available} {item.unit} (ในตะกร้ามีแล้ว {line.qty if line else 0})")
    if line:
        line.qty = new_qty
        line.save(update_fields=["qty"])
    else:
        line = CartItem.objects.create(cart=cart, item=item, qty=qty)
    cart.save(update_fields=["updated_at"])
    return line


def cart_update(line, qty):
    """UC-05 ข้อ 4: แก้จำนวน (เฉพาะวัสดุ/วัสดุคงทน)"""
    qty = int(qty)
    if line.item.is_equipment:
        raise ValidationError("ครุภัณฑ์ยืมได้ครั้งละ 1 ชิ้น")
    if qty < 1:
        raise ValidationError("จำนวนต้องมากกว่า 0 (ถ้าไม่ต้องการ ให้ลบออกจากตะกร้า)")
    available = available_qty(line.item)
    if qty > available:
        raise ValidationError(f"\"{line.item.name}\" คงเหลือ {available} {line.item.unit}")
    line.qty = qty
    line.save(update_fields=["qty"])


def cart_lines(student):
    """รายการในตะกร้าพร้อมผลตรวจตัดหน้า: [(line, available, snipped)]"""
    cart = Cart.objects.filter(student=student).first()
    if not cart:
        return []
    lines = cart.items.select_related("item", "item__material", "item__durablematerial", "item__equipment") \
        .order_by("added_at", "id")
    out = []
    for line in lines:
        available = available_qty(line.item)
        out.append((line, available, line.qty > available))
    return out


def cart_qty_map(student):
    """{item_id: qty} สำหรับป้าย "ในตะกร้าแล้ว" ในหน้า M2"""
    return dict(CartItem.objects.filter(cart__student=student).values_list("item_id", "qty"))


def _reserve(item, qty):
    """จองของทันทีตอนส่งคำขอ (ตัดสินใจ M3 ข้อ 1) · ต้องเรียกใน transaction ที่ล็อกแถวแล้ว"""
    if item.is_equipment:
        eq = item.equipment
        eq.status = Equipment.Status.BORROWED
        eq.save(update_fields=["status"])
    else:
        detail = item.detail
        detail.qty_available -= qty
        detail.save(update_fields=["qty_available"])


def release_stock(borrow_request):
    """คืนของที่จองไว้เข้าคลัง (ยกเลิก UC-07 / ปฏิเสธ UC-17)"""
    for bi in borrow_request.items.select_related("item", "item__equipment", "item__material", "item__durablematerial"):
        item = bi.item
        if item.is_equipment:
            eq = Equipment.objects.select_for_update().get(pk=item.pk)
            if eq.status == Equipment.Status.BORROWED:
                eq.status = Equipment.Status.AVAILABLE
                eq.save(update_fields=["status"])
        else:
            model = Material if item.is_material else DurableMaterial
            detail = model.objects.select_for_update().get(pk=item.pk)
            detail.qty_available = min(detail.qty_total, detail.qty_available + bi.qty)
            detail.save(update_fields=["qty_available"])


class SnipedError(ValidationError):
    """มีรายการในตะกร้าถูกยืม/เบิกตัดหน้า"""


@transaction.atomic
def submit_request(student, is_special=False, custom_due_date=None, photos=None):
    """UC-06: สร้างคำขอ PENDING จากตะกร้า + จองของ + ล้างตะกร้า

    photos = {cart_item_id: uploaded_file} (ไม่บังคับ → BorrowItem.initial_photo)
    """
    if not student.is_profile_complete:
        raise ValidationError("กรุณากรอกรหัสนักศึกษาและเบอร์โทรศัพท์ให้ครบก่อนส่งคำขอ")
    if student.user.blocked:
        raise ValidationError("บัญชีนี้ถูกระงับสิทธิ์ ไม่สามารถส่งคำขอยืมได้")
    if is_special:
        if not custom_due_date:
            raise ValidationError({"custom_due_date": "กรุณาระบุวันที่ต้องการคืน"})
        if custom_due_date <= timezone.localdate():
            raise ValidationError({"custom_due_date": "วันที่ต้องการคืนต้องเป็นวันในอนาคต"})
    cart = Cart.objects.select_for_update().filter(student=student).first()
    lines = list(cart.items.select_related("item").order_by("id")) if cart else []
    if not lines:
        raise ValidationError("ตะกร้าว่าง กรุณาเลือกสิ่งของก่อนส่งคำขอ")

    # ล็อกแถวสต็อกก่อนตรวจ ป้องกันคนอื่นยืมตัดหน้าพร้อมกัน
    ids = [line.item_id for line in lines]
    list(Item.objects.select_for_update().filter(pk__in=ids).order_by("pk"))
    list(Equipment.objects.select_for_update().filter(pk__in=ids))
    list(Material.objects.select_for_update().filter(pk__in=ids))
    list(DurableMaterial.objects.select_for_update().filter(pk__in=ids))
    sniped = []
    for line in lines:
        line.item = Item.objects.select_related("material", "durablematerial", "equipment").get(pk=line.item_id)
        if line.qty > available_qty(line.item):
            sniped.append(str(line.item))
    if sniped:
        raise SnipedError("มีรายการถูกยืม/เบิกตัดหน้า: " + ", ".join(sniped))

    req = BorrowRequest(
        student=student, use_date=timezone.localdate(), is_special=bool(is_special),
        custom_due_date=custom_due_date if is_special else None, status=BorrowRequest.Status.PENDING,
    )
    req.full_clean()
    req.save()
    photos = photos or {}
    for line in lines:
        bi = BorrowItem(borrow_request=req, item=line.item, qty=line.qty)
        if photos.get(line.pk):
            bi.initial_photo = photos[line.pk]
        bi.full_clean()
        bi.save()
        _reserve(line.item, line.qty)
    cart.items.all().delete()
    return req


@transaction.atomic
def cancel_request(student, borrow_request):
    """UC-07: ยกเลิกได้เฉพาะ PENDING ของตัวเอง → CANCELLED + คืนของเข้าคลัง"""
    req = BorrowRequest.objects.select_for_update().get(pk=borrow_request.pk)
    if req.student_id != student.pk:
        raise ValidationError("ไม่พบคำขอนี้")
    if req.status != BorrowRequest.Status.PENDING:
        raise ValidationError(f"ยกเลิกไม่ได้ เพราะคำขอนี้อยู่ในสถานะ \"{req.get_status_display()}\" แล้ว")
    release_stock(req)
    req.status = BorrowRequest.Status.CANCELLED
    req.save(update_fields=["status"])
    return req


ACTIVE_LOAN = (BorrowRequest.Status.BORROWING, BorrowRequest.Status.RETURN_PENDING)


def relocate(student, borrow_item, location):
    """แจ้งย้ายที่ตั้งของที่กำลังยืม (ตัดสินใจ M3 ข้อ 6 · ไม่มี UC รองรับ)"""
    location = (location or "").strip()
    req = borrow_item.borrow_request
    if req.student_id != student.pk:
        raise ValidationError("ไม่พบรายการนี้")
    if req.status not in ACTIVE_LOAN or not borrow_item.item.is_returnable or borrow_item.qty_outstanding <= 0:
        raise ValidationError("แจ้งย้ายได้เฉพาะของที่ต้องคืนและยังอยู่ระหว่างยืม")
    if not location:
        raise ValidationError("กรุณาระบุสถานที่ใหม่")
    borrow_item.current_location = location[:200]
    borrow_item.moved_at = timezone.now()
    borrow_item.save(update_fields=["current_location", "moved_at"])


# =============================================================================
# M3 รอบ 3b · แจ้งคืน (UC-08) · คิว (UC-10) · ประวัติ (UC-11) · แจ้งชำรุด (UC-38)
# =============================================================================
from .models import DamageReport, Queue, ReturnItem, ReturnRequest  # noqa: E402

CONDITION_LABEL = dict(ReturnItem.Condition.choices)
FINISHED = (BorrowRequest.Status.RETURNED, BorrowRequest.Status.ISSUED, BorrowRequest.Status.REJECTED,
            BorrowRequest.Status.CANCELLED, BorrowRequest.Status.EXPIRED)
ACTIVE_QUEUE = (Queue.Status.WAITING, Queue.Status.NOTIFIED)


# ---- UC-08 แจ้งคืน -----------------------------------------------------------
def returnable_lines(borrow_request):
    """รายการที่ยังต้องคืนในคำขอ: [(borrow_item, outstanding_qty)]"""
    out = []
    for bi in borrow_request.items.select_related("item", "item__equipment", "item__durablematerial"):
        if bi.item.is_returnable and bi.qty_outstanding > 0:
            out.append((bi, bi.qty_outstanding))
    return out


def pending_return(borrow_request):
    return borrow_request.return_requests.filter(status=ReturnRequest.Status.RETURN_PENDING).first()


@transaction.atomic
def notify_return(student, borrow_request, selections, photo, note=""):
    """UC-08: แจ้งคืนบางส่วน/ทั้งหมด → RETURN_PENDING

    selections = [(borrow_item_id, qty, condition, description)]
    ตัดสินใจ M3 ข้อ 7: แจ้งรอบใหม่ได้เมื่อรอบก่อนตรวจรับแล้วเท่านั้น · ข้อ 8: อาการ/สาเหตุ รวมเก็บใน note
    """
    req = BorrowRequest.objects.select_for_update().get(pk=borrow_request.pk)
    if req.student_id != student.pk:
        raise ValidationError("ไม่พบคำขอนี้")
    if req.status != BorrowRequest.Status.BORROWING:
        raise ValidationError(f"แจ้งคืนไม่ได้ เพราะคำขอนี้อยู่ในสถานะ \"{req.get_status_display()}\"")
    if pending_return(req):
        raise ValidationError("มีการแจ้งคืนที่รอเจ้าหน้าที่ตรวจรับอยู่แล้ว")
    if not selections:
        raise ValidationError({"selection": "กรุณาเลือกสิ่งของที่จะคืนอย่างน้อย 1 รายการ"})
    if not photo:
        raise ValidationError({"return_photo": "กรุณาแนบรูปหลักฐานสภาพสิ่งของ ณ วันคืน"})

    outstanding = {bi.pk: (bi, qty) for bi, qty in returnable_lines(req)}
    notes = []
    rr = ReturnRequest.objects.create(borrow_request=req, status=ReturnRequest.Status.RETURN_PENDING,
                                      return_photo=photo)
    for bi_id, qty, condition, desc in selections:
        if bi_id not in outstanding:
            raise ValidationError("มีรายการที่เลือกคืนไม่ได้")
        bi, left = outstanding[bi_id]
        qty = int(qty)
        if qty < 1 or qty > left:
            raise ValidationError({"selection": f"\"{bi.item}\" คืนได้ 1–{left} {bi.item.unit}"})
        if condition not in CONDITION_LABEL:
            raise ValidationError({"selection": "กรุณาเลือกสภาพของสิ่งของที่คืน"})
        ReturnItem.objects.create(return_request=rr, borrow_item=bi, qty_returned=qty, condition_status=condition)
        if bi.item.is_equipment:
            Equipment.objects.filter(pk=bi.item_id).update(status=Equipment.Status.RETURN_PENDING)
        desc = (desc or "").strip()
        if condition != ReturnItem.Condition.NORMAL:
            tag = bi.item.equipment.asset_tag if bi.item.is_equipment else bi.item.name
            notes.append(f"{tag} ({CONDITION_LABEL[condition]}): {desc or '-'}")
    if (note or "").strip():
        notes.append(note.strip())
    rr.note = "\n".join(notes)
    rr.save(update_fields=["note"])
    req.status = BorrowRequest.Status.RETURN_PENDING
    req.save(update_fields=["status"])
    return rr


@transaction.atomic
def cancel_return(student, return_request):
    """UC-08 Alternative: ยกเลิกการแจ้งคืน (ยังไม่ตรวจรับ) → กลับเป็นกำลังยืม"""
    rr = ReturnRequest.objects.select_for_update().select_related("borrow_request").get(pk=return_request.pk)
    req = rr.borrow_request
    if req.student_id != student.pk:
        raise ValidationError("ไม่พบการแจ้งคืนนี้")
    if rr.status != ReturnRequest.Status.RETURN_PENDING or rr.inspected_by_id:
        raise ValidationError("ยกเลิกไม่ได้ เพราะเจ้าหน้าที่ตรวจรับแล้ว")
    for ri in rr.items.select_related("borrow_item__item"):
        if ri.borrow_item.item.is_equipment:
            Equipment.objects.filter(pk=ri.borrow_item.item_id, status=Equipment.Status.RETURN_PENDING) \
                .update(status=Equipment.Status.BORROWED)
    rr.delete()
    req.status = BorrowRequest.Status.BORROWING
    req.save(update_fields=["status"])


# ---- UC-10 คิว ---------------------------------------------------------------
def queue_position(queue):
    return Queue.objects.filter(item_id=queue.item_id, status__in=ACTIVE_QUEUE, joined_at__lt=queue.joined_at).count() + 1


def current_loan(item):
    """รายการยืมที่ยังไม่คืนของสิ่งของนี้ที่กำหนดคืนเร็วที่สุด (ใช้ประมาณวันได้ยืม)"""
    loans = BorrowItem.objects.filter(
        item=item, due_date__isnull=False, borrow_request__status__in=ACTIVE_LOAN,
    ).select_related("borrow_request").order_by("due_date")
    for bi in loans:
        if bi.qty_outstanding > 0:
            return bi
    return None


def estimate_available(queue, position=None):
    """UC-10 ข้อ 2 (ตัดสินใจ M3 ข้อ 4): กำหนดคืนผู้ยืมปัจจุบัน + (ลำดับ − 1) × วันยืมสูงสุด

    คืน (วันที่ หรือ None, ข้อความชี้แจง)
    """
    item = queue.item
    position = position or queue_position(queue)
    loan = current_loan(item)
    if not loan:
        return None, "ยังประเมินไม่ได้ (ยังไม่มีกำหนดคืนของผู้ยืมปัจจุบัน)"
    days = item.detail.max_borrow_days
    date = loan.due_date + timedelta(days=(position - 1) * days)
    if loan.borrow_request.is_special:
        note = f"ผู้ยืมปัจจุบันได้รับอนุมัติยืมนานพิเศษถึง {loan.due_date:%d/%m/%Y}"
    else:
        note = f"ผู้ยืมปัจจุบันมีกำหนดคืน {loan.due_date:%d/%m/%Y}"
    if position > 1:
        note += f" · มีคิวก่อนหน้า {position - 1} คิว (คิวละประมาณ {days} วัน)"
    return date, note


@transaction.atomic
def join_queue(student, item):
    """UC-10: จองคิว (วัสดุคงทนหมด = ระดับ item · ครุภัณฑ์ถูกยืม = ระดับชิ้น)"""
    item = Item.objects.select_for_update(of=("self",)).select_related("equipment", "durablematerial", "material") \
        .get(pk=item.pk)
    if not item.is_returnable:
        raise ValidationError("วัสดุสิ้นเปลืองจองคิวไม่ได้")
    if item.base_status in HIDDEN_BASE or (item.is_equipment and item.equipment.status in
                                            (Equipment.Status.RETIRED, Equipment.Status.LOST)):
        raise ValidationError("ไม่พบสิ่งของนี้")
    if available_qty(item) > 0:
        raise ValidationError(f"\"{item}\" ยังว่างอยู่ ยืมได้ทันทีโดยไม่ต้องจองคิว")
    if Queue.objects.filter(item=item, student=student, status__in=ACTIVE_QUEUE + (Queue.Status.CONFIRMED,)).exists():
        raise ValidationError("คุณอยู่ในคิวแล้ว")
    q = Queue(item=item, student=student, status=Queue.Status.WAITING)
    q.full_clean()
    q.save()
    return q


def leave_queue(student, queue):
    if queue.student_id != student.pk or queue.status not in ACTIVE_QUEUE + (Queue.Status.CONFIRMED,):
        raise ValidationError("ออกจากคิวนี้ไม่ได้")
    queue.status = Queue.Status.CANCELLED
    queue.save(update_fields=["status"])


def confirm_queue(student, queue, now=None):
    """UC-10 ข้อ 4: ยืนยันรับสิทธิ์ภายใน 1 วันหลังแจ้งเตือน"""
    now = now or timezone.now()
    if queue.student_id != student.pk or queue.status != Queue.Status.NOTIFIED:
        raise ValidationError("ยังไม่ถึงคิวของคุณ")
    if queue.notified_at and now > queue.notified_at + QUEUE_CONFIRM_WINDOW:
        raise ValidationError("เลยเวลายืนยันรับสิทธิ์ (1 วัน) แล้ว")
    queue.status = Queue.Status.CONFIRMED
    queue.confirmed_at = now
    queue.save(update_fields=["status", "confirmed_at"])


def notify_next(item, now=None):
    """แจ้งคิวถัดไปเมื่อสิ่งของว่าง (เรียกจาก M6 ตอนตรวจรับคืน และหลังคิวหมดอายุ)

    ตัดสินใจ M3 ข้อ 5: แจ้งบนหน้าเว็บ (สถานะ NOTIFIED → แบนเนอร์/ป้ายเมนู) · อีเมลต่อเติมที่ฟังก์ชันนี้ภายหลัง
    """
    if Queue.objects.filter(item=item, status=Queue.Status.NOTIFIED).exists():
        return None
    nxt = Queue.objects.filter(item=item, status=Queue.Status.WAITING).order_by("joined_at", "id").first()
    if nxt and available_qty(Item.objects.select_related("equipment", "durablematerial", "material").get(pk=item.pk)) > 0:
        nxt.status = Queue.Status.NOTIFIED
        nxt.notified_at = now or timezone.now()
        nxt.expired_at = nxt.notified_at + QUEUE_CONFIRM_WINDOW
        nxt.save(update_fields=["status", "notified_at", "expired_at"])
        return nxt
    return None


def expire_and_advance(now=None):
    """คิวที่ไม่ยืนยันใน 1 วัน → EXPIRED แล้วแจ้งคิวถัดไปของสิ่งของนั้น"""
    now = now or timezone.now()
    stale = list(Queue.objects.filter(status=Queue.Status.NOTIFIED, notified_at__lte=now - QUEUE_CONFIRM_WINDOW)
                 .values_list("item_id", flat=True))
    expire_queues(now)
    for item_id in set(stale):
        notify_next(Item.objects.get(pk=item_id), now)


# ---- UC-11 ประวัติ (ใช้ร่วมกับ UC-14 ใน M5) -------------------------------------
def is_reviewable(borrow_item):
    """ประเมินได้เมื่อ "คืนสำเร็จแล้ว" (ของที่ต้องคืน) หรือเบิกสำเร็จแล้ว (วัสดุสิ้นเปลือง)"""
    if borrow_item.item.is_returnable:
        return borrow_item.qty_returned > 0
    return borrow_item.borrow_request.status in (BorrowRequest.Status.ISSUED, BorrowRequest.Status.BORROWING,
                                                  BorrowRequest.Status.RETURN_PENDING, BorrowRequest.Status.RETURNED)


# ---- UC-38 แจ้งชำรุด ---------------------------------------------------------
ROOM, SYSTEM = "room", "system"


def report_damage(student, kind, symptom, location="", item_name="", asset_tag="", photo=None):
    """UC-38: แจ้งอุปกรณ์ชำรุด (ไม่ต้องมีประวัติการยืม)"""
    symptom, location = (symptom or "").strip(), (location or "").strip()
    errors = {}
    item = None
    if not symptom:
        errors["symptom"] = "กรุณาอธิบายอาการที่พบ"
    if kind == ROOM:
        item_name = (item_name or "").strip()
        if not item_name:
            errors["item_name"] = "กรุณาระบุชื่ออุปกรณ์"
        if not location:
            errors["location"] = "กรุณาระบุตึก/ห้องที่พบ"
    elif kind == SYSTEM:
        tag = (asset_tag or "").strip()
        eq = Equipment.objects.select_related("item").filter(asset_tag__iexact=tag).first() if tag else None
        if not eq:
            errors["asset_tag"] = "ไม่พบรหัสครุภัณฑ์นี้ในระบบ" if tag else "กรุณาระบุรหัสครุภัณฑ์"
        else:
            item, item_name = eq.item, eq.item.name
    else:
        errors["kind"] = "กรุณาเลือกประเภทที่จะแจ้ง"
    if errors:
        raise ValidationError(errors)
    return DamageReport.objects.create(
        student=student, item=item, item_name=item_name[:200],
        origin_location=item.location if item else "", location=(location or (item.location if item else ""))[:200] or "-",
        symptom=symptom, photo=photo or "", status=DamageReport.Status.PENDING,
    )
