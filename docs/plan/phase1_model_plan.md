# เฟส 1.1 · แผน Models (รอยืนยันก่อนเขียนโค้ด)

อ้างอิง: `docs/proposal/mapping/00_erd_reference.md` (19 ตาราง), `use_case_description.md` (ตาราง "สรุป Module", UC-15), mockup
สถานะ: **แผนเท่านั้น ยังไม่ได้แก้ models**

---

## 1. การวาง model ลงแต่ละ app

| App (Module) | Models | ตาราง ERD |
|---|---|---|
| `accounts` (M1) | `Admin`, `UbuUser`, `Student`, `Staff` | ADMIN, USER, STUDENT, STAFF |
| `catalog` (M2) | `Item`, `Material`, `DurableMaterial`, `Equipment` | ITEM + 3 subtype |
| `borrow` (M3) | `Cart`, `CartItem`, `BorrowRequest`, `BorrowItem`, `ReturnRequest`, `ReturnItem`, `Queue`, `DamageReport` | 8 ตาราง (DAMAGE_REPORT อยู่ที่นี่เพราะ UC-38 อยู่ใน M3) |
| `suggestion` (M4) | `Suggestion`, `PurchasePlan` | SUGGESTION, PURCHASE_PLAN |
| `evaluation` (M5) | `Review` | REVIEW |
| `staff`, `staff_inventory`, `staff_student`, `staff_report`, `admin_panel` (M6–M10) | — ไม่มี model ของตัวเอง | ใช้ model จาก app ข้างบน มีแค่ views |

รวม 19 model = 19 ตารางตาม ERD (+ `auth_user` ของ Django สำหรับ login ซึ่งไม่อยู่ใน ERD)
app M6–M10 สร้างเป็น app เปล่าไว้ในเฟส 1.2 (มีแค่ `apps.py`, `urls.py`) เพื่อให้ sidebar ชี้ URL ได้

---

## 2. ผู้ใช้งาน: USER / STUDENT / STAFF / ADMIN

**ADMIN เป็นตารางแยกจริงตาม ERD** (ตัดสินใจแล้ว: ข้อ 3 = ข.)

Django ต้องมีตาราง login กลาง 1 ตาราง (`auth_user`) เพื่อสร้าง session และเข้า `/admin/` จึงแบ่งเป็น 2 ชั้น:
- **ชั้น login (ไม่อยู่ใน ERD):** `auth_user` ของ Django ใช้แบบเดิม ไม่ทำ custom user · ใช้แค่ยืนยันตัวตนและเก็บ session
- **ชั้นข้อมูล (ตาม ERD ครบ 4 ตาราง):** `Admin`, `UbuUser`, `Student`, `Staff` แต่ละตารางผูกกับ `auth_user` ของตัวเอง

| ERD | Django model (`accounts`) |
|---|---|
| `ADMIN` | `Admin` — `auth_user = OneToOneField(auth.User)` (ต้องเป็น superuser), `name`, `email` (ไม่บังคับ @ubu), `created_at` · `username` และ `last_login` อ่านผ่าน `auth_user` (property) ไม่เก็บซ้ำ เพื่อไม่ให้ข้อมูลสองที่ไม่ตรงกัน |
| `USER` | `UbuUser` — `auth_user = OneToOneField(auth.User)`, `name`, `email` unique (@ubu.ac.th), `first_login`, `created_at`, `blocked`, `block_reason`, `blocked_by_staff` → `Staff` (null), `blocked_by_admin` → `Admin` (null) · `last_login` อ่านผ่าน `auth_user` · ตั้งชื่อ `UbuUser` เพราะชื่อ `User` ชนกับ `User` ของ Django · `db_table = "user"` |
| `STUDENT` | `Student` — `user = OneToOneField(UbuUser, primary_key=True)`, `student_id` unique + regex `^\d{11}$`, `phone` regex `^0[689]\d{8}$` · null ได้จนกว่าจะกรอกตอน onboarding (UC-15) |
| `STAFF` | `Staff` — `user = OneToOneField(UbuUser, primary_key=True)`, `is_override`, `override_reason`, `assigned_by` → `Admin` (null), `assigned_at` |

**การสร้างแถว:**
- `createsuperuser` → signal สร้างแถว `Admin` คู่กันอัตโนมัติ
- login SSO ครั้งแรก → สร้าง `auth_user` (ไม่มีรหัสผ่าน: `set_unusable_password()` ตาม UC-15 ข้อ 1) + `UbuUser` + `Student` (ตัดสินใจแล้ว: ข้อ 1 = ก. ทุกคนเริ่มเป็นนักศึกษา)
- staff ช่วงพัฒนา → สร้างแถว `Staff` ผ่าน Django admin หรือ `seed` · ภายหลังทำผ่าน Role Override (UC-33, M10)
- Role Override ให้อีเมลที่ยังไม่เคย login → สร้าง `UbuUser` + `Staff` ไว้ก่อน (ยังไม่มี `auth_user`, จึงตั้ง `auth_user` ให้ null ได้) แล้วผูกเมื่อ login ครั้งแรก

**role ที่ใช้งานจริง** (helper `accounts/roles.py → get_role(request.user)`):
มีแถว `Admin` → admin · มี `Staff` → staff · มีแค่ `Student` → student
Overlapping ISA: 1 `UbuUser` มีได้ทั้ง `Student` และ `Staff`

**ข้อดี / ข้อเสีย:** ตรงกับ ERD และ Chen diagram ในเล่มทุกตาราง แต่โค้ดต้องผ่านชั้น `request.user.ubuuser` อีกหนึ่งชั้น (ซ่อนไว้ใน helper ไม่ต้องเขียนซ้ำทุก view)

**ลบ `UserProfile` เดิม** พร้อม signal สร้างโปรไฟล์อัตโนมัติ

---

## 3. สิ่งของ: ITEM ISA

ใช้ `OneToOneField(Item, primary_key=True, db_column="item_id")` แบบระบุเอง **ไม่ใช้** Django multi-table inheritance
ได้ชื่อคอลัมน์ `item_id` ตรงกับ ERD และ query ฝั่ง `Item` ไม่โดน JOIN อัตโนมัติ

| Model | ฟิลด์ |
|---|---|
| `Item` | `item_type` (MATERIAL / DURABLE_MATERIAL / EQUIPMENT), `name`, `location`, `unit`, `purchase_price`, `base_status` (AVAILABLE / DAMAGED / INACTIVE / RETIRED), `description`, `image` (ImageField) |
| `Material` | `qty_total`, `qty_available` |
| `DurableMaterial` | `qty_total`, `qty_available`, `max_borrow_days`, `fine_rate_per_day` |
| `Equipment` | `asset_tag` unique, `max_borrow_days`, `fine_rate_per_day`, `status` (AVAILABLE / BORROWED / RETURN_PENDING / DAMAGED / MAINTENANCE / RETIRED / LOST), `note` |

**บังคับ ISA:**
- **Disjoint**: `Item.clean()` เช็กว่ามี subtype ตรงกับ `item_type` เพียงตัวเดียว · subtype `clean()` เช็กว่า `item.item_type` ตรงกับตัวเอง
- **Total**: สร้างสิ่งของผ่าน `catalog/services.py → create_item(item_type, **fields)` ใน `transaction.atomic()` เท่านั้น (สร้าง Item + subtype พร้อมกัน) และมี test ยืนยัน
- helper `item.detail` คืน subtype ที่ถูกต้อง, `item.is_returnable` (DURABLE_MATERIAL / EQUIPMENT)
- DB constraint: `qty_available >= 0` และ `qty_available <= qty_total`

---

## 4. ยืม-คืน และตารางอื่น

| Model | ฟิลด์ / ความสัมพันธ์ |
|---|---|
| `Cart` | `student = OneToOneField(Student)` (1 คน 1 ตะกร้า), `created_at`, `updated_at` |
| `CartItem` | `cart` FK, `item` FK, `qty`, `added_at` · unique (`cart`, `item`) |
| `BorrowRequest` | `student` FK, `approved_by` → Staff (null), `use_date`, `is_special`, `custom_due_date` (null), `status` (PENDING / BORROWING / RETURN_PENDING / ISSUED / RETURNED / REJECTED / CANCELLED / EXPIRED), `created_at`, `approved_at`, `reject_reason` |
| `BorrowItem` | `borrow_request` FK, `item` FK, `qty`, `due_date` (null), `initial_photo`, `current_location`, `moved_at` |
| `ReturnRequest` | `borrow_request` FK, `inspected_by` → Staff (null), `status` (RETURN_PENDING / RETURNED / REJECTED), `return_photo`, `custom_fine` (null), `fine_paid`, `fine_reason`, `note`, `created_at`, `returned_at` |
| `ReturnItem` | `return_request` FK, `borrow_item` FK, `qty_returned`, `condition_status` (NORMAL / DAMAGED / LOST), `fine`, `lost_compensation`, `lost_paid` |
| `Queue` | `item` FK, `student` FK, `status` (WAITING / NOTIFIED / CONFIRMED / EXPIRED / CANCELLED), `joined_at`, `notified_at`, `confirmed_at`, `expired_at` |
| `DamageReport` | `student` FK, `item` FK (null), `item_name`, `origin_location`, `location`, `symptom`, `photo`, `status` (PENDING / IN_PROGRESS / RESOLVED), `created_at` |
| `Suggestion` | `student` FK, `name`, `detail`, `status` (SUBMITTED / ACKNOWLEDGED / REJECTED / PURCHASE_PLAN), `created_at` |
| `PurchasePlan` | `suggestion = OneToOneField(Suggestion, null=True)` (ERD เป็น `|o--o|`), `name`, `detail`, `created_by` → Staff, `created_at` |
| `Review` | `borrow_item = OneToOneField(BorrowItem)` (1 รายการรีวิวได้ 1 ครั้ง), `rating`, `comment`, `created_at` · ผู้รีวิวและสิ่งของหาผ่าน `BorrowItem` ตามหัวข้อ "REVIEW แบบ 3NF" |

ทุก `status` ใช้ `TextChoices` ชื่อค่าตรงกับ ERD และ label ภาษาไทย

**ตัวเงินใช้ `DecimalField(max_digits=10, decimal_places=2)`** แทน float ใน ERD (`purchase_price`, `fine_rate_per_day`, `custom_fine`, `fine`, `lost_compensation`) เพราะ float ปัดเศษผิดเวลาคิดเงิน ความหมายเหมือนเดิม

---

## 5. กฎธุรกิจใน ERD → จะเขียนไว้ที่ไหน

| กฎ | ที่ |
|---|---|
| `blocked_by_staff` / `blocked_by_admin` กรอกได้อย่างใดอย่างหนึ่ง | `CheckConstraint` ใน `UbuUser` |
| `Admin.auth_user` ต้องเป็น superuser | `Admin.clean()` |
| `student_id` 11 หลักไม่ซ้ำ, `phone` 10 หลัก | validator + unique ใน `Student` |
| ต้องมี `student_id` + `phone` ก่อนส่งคำขอยืม | `Student.is_profile_complete` (view ของ UC-06 เป็นคนเช็ก) |
| `CartItem` / `BorrowItem` ของ EQUIPMENT ต้อง `qty = 1` | `clean()` ของทั้งสอง model |
| `ReturnItem` ใช้ได้เฉพาะของที่ต้องคืน | `ReturnItem.clean()` |
| `Queue` ใช้ได้เฉพาะของที่ต้องคืน | `Queue.clean()` |
| `qty_available` อยู่ระหว่าง 0 ถึง `qty_total` | `CheckConstraint` ใน `Material` / `DurableMaterial` |
| `rating` 1–5 | `CheckConstraint` ใน `Review` |
| Disjoint / Total ของ ITEM และ USER | `clean()` + service function (หัวข้อ 3) |
| Queue ไม่ยืนยันภายใน 1 วัน → EXPIRED | service `borrow/services.py → expire_queues()` เรียกตอนเปิดหน้าคิว (ไม่ใช่กฎใน model) |

`clean()` ไม่ถูกเรียกอัตโนมัติตอน `save()` → service ทุกตัวต้องเรียก `full_clean()` ก่อนบันทึก

---

## 6. ฟังก์ชันคำนวณกำหนดคืนและค่าปรับ

วางไว้ที่ `borrow/services.py` เป็นฟังก์ชันล้วน (pure function) ทดสอบได้โดยไม่ต้องมีหน้าจอ:

| ฟังก์ชัน | สูตร (จาก ERD หัวข้อ "กำหนดคืนและค่าปรับรายชิ้น") |
|---|---|
| `compute_due_date(borrow_item, release_date)` | MATERIAL → `None` · `is_special` → `custom_due_date` · อื่น ๆ → `release_date + max_borrow_days` |
| `compute_fine(borrow_item, return_date, qty_returned)` | `max(0, return_date − due_date).days × fine_rate_per_day × qty_returned` |
| `ReturnRequest.total_fine` (property) | `custom_fine` ถ้าไม่ใช่ null ไม่อย่างนั้น SUM(`ReturnItem.fine`) |
| `BorrowRequest.total_fine` (property) | SUM `total_fine` ของทุก ReturnRequest |
| `BorrowRequest.earliest_due_date` (property) | MIN(`due_date`) ของรายการที่ยังคืนไม่ครบ |

วันที่ทั้งหมดใช้ `timezone.localdate()` (Asia/Bangkok)

---

## 7. สิ่งที่จะลบหรือเปลี่ยนจากโค้ดเดิม

| ของเดิม | จะทำอะไร |
|---|---|
| `accounts.UserProfile` + signal | ลบ → แทนด้วย `Admin` / `UbuUser` / `Student` / `Staff` |
| `catalog.Category` | ลบ (ERD ไม่มี) · หน้า M2 / M7 จะไม่มีตัวกรองและช่องหมวดหมู่ |
| `catalog.Item` (2 ประเภท) | เขียนใหม่ตามหัวข้อ 3 |
| `catalog.AssetTag` | ลบ → `Equipment` 1 แถว = 1 ชิ้น |
| `catalog/views.py`, `forms.py`, templates 3 หน้า | ถอดออกจาก `urls.py` ชั่วคราวให้โปรเจกต์รันได้ (ไฟล์เดิมดูย้อนหลังได้ใน git) แล้วเขียนใหม่ตอนทำ M2 / M7 |
| `accounts/adapters.py` | เก็บไว้ เพิ่มแค่: ถ้าผู้ใช้ถูก block ให้ปฏิเสธการ login (UC-15) |
| migrations ทั้งหมด + `db.sqlite3` | ลบ แล้วสร้างใหม่ · ล้างฐาน Postgres ด้วย (`docker compose down -v`) เพราะตารางเดิมของ accounts / catalog ถูกแทนทั้งหมด (ข้อมูลทดสอบเดิมหาย) |

---

## 8. ข้อตัดสินใจ (ยืนยันแล้ว 2026-11-13)

| ข้อ | เลือก | ผลต่อการทำงาน |
|---|---|---|
| 1. SSO แยก staff ยังไง | ก. | login ครั้งแรกทุกคนเป็น `Student` · staff สร้างผ่าน Django admin / `seed` ไปก่อน |
| 2. หมวดหมู่ | ก. | ไม่มีตาราง CATEGORY · หน้าจอจริงไม่มีหมวดหมู่ · mockup 3 หน้า (`page-bulk-import`, `page-item-detail`, `page-item-list`) ต้องลบ `category_id` ออกภายหลัง |
| 3. ADMIN | ข. | ตาราง `Admin` แยกจริง ผูกกับ `auth_user` ที่เป็น superuser (หัวข้อ 2) |
| 4. ตัวเงิน | ก. | `DecimalField` · ควรแก้ชนิดใน ERD จาก `float` เป็น `decimal` ด้วย (5 คอลัมน์ในหัวข้อ 4) |

## 9. เอกสารที่ต้องแก้ตามภายหลัง (ไม่ขวางเฟส 1.2)
- ERD: `float` → `decimal` ใน `purchase_price`, `fine_rate_per_day`, `custom_fine`, `fine`, `lost_compensation`
- ERD: หมายเหตุว่า `USER.last_login` / `ADMIN.username`, `last_login` อ่านจากตาราง login ของ Django
- Mockup: ลบหมวดหมู่ออกจาก 3 หน้าในข้อ 2
