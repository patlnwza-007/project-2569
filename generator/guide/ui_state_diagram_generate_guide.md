# คู่มือการวาด UI State Diagram (UI State Diagram Generation Guide)

> ใช้คู่กับ [`ui_state_diagram_template.md`](../template/ui_state_diagram_template.md) เป็นจุดเริ่มก๊อปปี้ และดู [`ui_state_diagram_example.md`](../example/ui_state_diagram_example.md) เป็นตัวอย่างที่ทำตามกฎครบทุกข้อ
>
> **แหล่งข้อมูลนำเข้า (input) มี 2 ไฟล์เท่านั้น:** `<app>/proposal/usecase_description.md` (มี UC อะไร ใครทำ เงื่อนไข/ข้อผิดพลาดอะไร) และ `<app>/activity/*.puml` (แต่ละ UC เดินเป็นขั้นตอนอย่างไร ขั้นไหนอยู่ฝั่ง actor) — **ห้ามคิดหน้าจอขึ้นมาเองโดยไม่มี 2 ไฟล์นี้รองรับ**
>
> **สถาปัตยกรรมเป้าหมาย: Django MVT monolith** — 1 state = 1 หน้าจอ = 1 URL (`path`) ที่ server render จริง ไม่ใช่ client-side route ของ SPA ผลลัพธ์ของไฟล์นี้เป็น input บังคับของ [`UI_django_frontend.md`](UI_django_frontend.md) §0 และ [`mockup_generate_guide.md`](mockup_generate_guide.md) §4.1 ต่อไป

---

## 0. นิยาม: UI State Diagram ต่างจาก Use Case / Activity Diagram อย่างไร (อ่านก่อนเริ่ม)

ไดอะแกรม 3 ตัวตอบคำถามคนละข้อ ห้ามเอาเนื้อหาข้ามกัน:

| ไดอะแกรม | ตอบคำถาม | หน่วยของกล่อง |
|---|---|---|
| Use case diagram ([guide](usecase_generate_guide.md)) | "ผู้ใช้ทำอะไรได้บ้าง" (goal-level) | 1 กล่อง = 1 เป้าหมายของผู้ใช้ |
| Activity diagram ([guide](activity_diagram_generate_guide.md)) | "1 UC ทำงานเป็นขั้นตอนอย่างไร ใครทำที่ไหน" | 1 กล่อง = 1 ขั้นตอน (มี swimlane) |
| **UI state diagram (ไฟล์นี้)** | **"ผู้ใช้เดินจากหน้าจอไหนไปหน้าจอไหน ด้วยปุ่มอะไร"** | **1 กล่อง = 1 หน้าจอจริง** |

**กฎข้อเดียวที่สำคัญที่สุด: คำว่า "state" ที่นี่หมายถึง "หน้าจอ (page/screen)" ไม่ใช่ "สถานะของข้อมูล"**

นี่คือความสับสนที่พบบ่อยที่สุด — สถานะข้อมูลอย่าง `รออนุมัติ / อนุมัติแล้ว / กำลังยืม / คืนสำเร็จ` **ไม่ใช่ state ในไดอะแกรมนี้** เพราะผู้ใช้ไม่ได้ "ไปที่หน้ารออนุมัติ" — ผู้ใช้อยู่ที่ *หน้าเดียวกัน* แล้วเห็นป้ายสถานะเปลี่ยนไป สถานะข้อมูลต้องไปอยู่ที่ 2 ที่นี้เท่านั้น:
- **บน label ของ transition** — ในรูป `→ <สถานะใหม่>` (สื่อว่ากดปุ่มนี้แล้วข้อมูลเปลี่ยนสถานะเป็นอะไร)
- **ใน `note` ของ state** — บรรทัด `แสดง:` (สื่อว่าหน้านี้แสดงป้ายสถานะอะไรได้บ้าง)

```plantuml
' ผิด — เอาสถานะข้อมูลมาเป็นหน้าจอ ทั้งที่ผู้ใช้ไม่ได้เปลี่ยนหน้า
state "รออนุมัติ" as Pending
state "อนุมัติแล้ว" as Approved
Pending --> Approved : เจ้าหน้าที่อนุมัติ
```

```plantuml
' ถูกต้อง — หน้าจอเป็น state, สถานะข้อมูลอยู่บน label + note
state "สถานะคำขอของฉัน\n(UC-10)" as MyRequestList
note right of MyRequestList
  แสดง: รายการคำขอ + ป้ายสถานะ (รออนุมัติ / อนุมัติแล้ว / ปฏิเสธ)
end note
MyRequestList --> PickupConfirm : เลือกคำขอที่ "อนุมัติแล้ว"
PickupConfirm --> MyRequestList : กด "ยืนยันรับของ"\n→ สถานะเปลี่ยนเป็น "กำลังยืม"
```

---

## 1. ลำดับการอ่าน input (ทำตามลำดับนี้ ห้ามข้าม)

1. **`<app>/proposal/usecase_description.md`** — ทำรายการ UC ทั้งหมดของ app นี้ก่อน พร้อมจดไว้ 4 ช่องต่อ UC: **Actor หลัก** (ใช้แบ่งโซน §8), **Basic Flow** (ใช้หา suffix ของ page_code §4 + บรรทัด `แสดง/ฟิลด์:` §7), **Alternative Flow** (ใช้หา transition ขาล้มเหลว §6 + บรรทัด `ว่าง/ผิดพลาด:` §7), **Business Rules** (ใช้หา guard §6 + บรรทัด `กฎ:` §7)
2. **`<app>/activity/*.puml` ทุกไฟล์ของ app นั้น** — ใช้หาขอบเขตหน้าจอตามอัลกอริทึม §3 (สิ่งที่ usecase_description บอกไม่ได้คือ "ขั้นตอนไหนอยู่ฝั่ง actor" ซึ่งเป็นตัวตัดสินว่าต้องมีหน้าจอกี่หน้า)
3. **`fn req/<app>.md`** (ถ้ามี) — ใช้ยืนยัน role ที่เห็นแต่ละหน้า ไม่ได้ใช้กำหนดจำนวน state

> **ห้ามเริ่มวาดจาก activity diagram ก่อน usecase_description** — activity diagram บอกขั้นตอนแต่ไม่บอกว่า UC ไหนเป็นของ actor ไหน ถ้าเริ่มผิดลำดับจะได้โซนที่ role ปนกัน

---

## 2. โครงสร้างไฟล์ output — แยกไฟล์ต่อ module + 1 ไฟล์ overview

```
<app>/state/module_state_diagram.puml      ← 1 ไฟล์ต่อ 1 Django app (ระดับ "หน้าจอ")
architecture/overview_state_diagram.puml   ← 1 ไฟล์ต่อระบบ (ระดับ "app") — ดู §8
```

| ระดับ | ไฟล์ | 1 state = | ตัวอย่าง page_code |
|---|---|---|---|
| **Module** | `<app>/state/module_state_diagram.puml` | 1 หน้าจอ = 1 URL | `ItemList`, `CartDetail`, `CheckoutForm` |
| **Overview** | `architecture/overview_state_diagram.puml` | 1 Django app = 1 การ์ด/เมนูใน Dashboard | `CatalogApp`, `BorrowApp`, `Dashboard` |

**ทำไมแยกไฟล์ต่อ app ไม่รวมเป็นไฟล์เดียว:** ไดอะแกรมรวมทุก role/ทุก app ในไฟล์เดียวจะมีหน้าจอหลายสิบหน้า อ่านไม่ออกและ layout engine จัดไม่ลงหน้ากระดาษ · ที่สำคัญกว่านั้นคือ [`UI_django_frontend.md`](UI_django_frontend.md) และ [`mockup_generate_guide.md`](mockup_generate_guide.md) นับจำนวนหน้าจอ/ไฟล์ mockup **ต่อ app** จากไฟล์ `module_state_diagram` ของ app นั้นโดยตรง (1 state = 1 `path()` = 1 view = 1 template = 1 ไฟล์ใน `pages/`) ถ้ารวมเป็นไฟล์เดียวจะเช็ค 1:1 ไม่ได้

**ถ้า app เดียวมีหลาย role ใช้งาน** (เช่น `borrow` มีทั้งนักศึกษาและเจ้าหน้าที่) ให้แบ่งเป็น composite state ตาม role **ในไฟล์เดียวกันของ app นั้น** ตาม §8.2 ไม่ต้องแยกไฟล์เพิ่ม

---

## 3. วิธีหา state จาก Activity Diagram — Screen Boundary Algorithm

นี่คือขั้นที่แปลง "ขั้นตอน" เป็น "หน้าจอ" ใช้กฎเดียว: **ขอบเขตหน้าจอเกิดขึ้นทุกครั้งที่ control กลับมาที่ partition ของ actor มนุษย์**

เพราะขั้นตอนใน partition `|ระบบ ...|` หรือ `|... (external)|` ไม่มี UI ให้ผู้ใช้เห็น — มันคือสิ่งที่เกิดขึ้น *ระหว่าง* กดปุ่มกับเห็นหน้าถัดไป จึงเป็น **label บน transition** ไม่ใช่ state

| สิ่งที่เจอใน activity diagram | แปลงเป็นอะไรใน state diagram |
|---|---|
| ขั้นตอนติดกันหลายขั้นใน partition actor เดียวกัน โดยไม่มี partition ระบบคั่น | **1 state เดียว** (ผู้ใช้ทำหลายอย่างจบในหน้าเดียว) |
| `start` ของ flow | ปุ่ม/เมนูที่เข้ามาที่ state นี้ (transition ขาเข้า) |
| ขั้นตอนใน partition `\|ระบบ ...\|` | **ไม่ใช่ state** — เป็นการประมวลผลบน transition |
| ขั้นตอนใน partition `\|... (external)\|` (SSO/SMTP/Payment) | **ไม่ใช่ state** — เป็น label บน transition หรือ note |
| `if (...) then (...) else (...)` ที่ปลายทางทั้งสองข้าง actor เห็นหน้าต่างกัน | **2 transition** ออกจาก state เดียวกัน พร้อม guard บน label (§6.3) |
| `if` ที่ทั้งสองข้าง actor ยังอยู่หน้าเดิม (แค่ขึ้น error ในหน้า) | **1 self-transition** `A --> A` (§6.4) — ไม่สร้าง state ใหม่ |
| `repeat` / `repeat while` | **self-transition** `A --> A : <เงื่อนไขที่ยังไม่ผ่าน>` |
| `stop` ใน alternative flow (ปฏิเสธ/ยกเลิก) | transition กลับไป state ก่อนหน้า หรือ self-transition — **ห้ามสร้าง state ชื่อ "Error"** |
| `fork` / `end fork` (audit log, ส่งอีเมล, in-app notification) | **ไม่ใช่ state และไม่ใช่ transition** — เขียนเป็นบรรทัด `แจ้งเตือน:` ใน note (§7) |
| `note` ที่บอก pre-condition | guard บน transition ขาเข้า (§6.3) |

### 3.1 กฎยุบ/แตกหน้า — ห้ามคิดว่า 1 UC = 1 state

**ยุบหลาย UC เป็น 1 state เมื่อ** (ทำให้ตรงกับหน้าจริงมากกว่า):
- UC นั้นเป็น `<<extend>>` ของอีก UC หนึ่ง เช่น "ค้นหาและกรอง" ที่ extend "ดูรายการ" → **ไม่แยกหน้า** เพราะช่องค้นหาอยู่บนหน้ารายการเดียวกัน ให้เขียนรวมใน page_title (§5.3) และใส่ช่องค้นหาไว้บรรทัด `ฟิลด์:` ของ note
- UC หลายตัวใช้ข้อมูลชุดเดียวกันและ actor เดียวกัน จนหน้าจริงทำเป็นแท็บในหน้าเดียว (เช่น "ดูโปรไฟล์" + "แก้ไขโปรไฟล์" = `ProfileDetail` หน้าเดียว)
- UC เป็นการกระทำในตาราง (approve/ลบ/ออกจากคิว) ที่ทำเสร็จแล้วผู้ใช้ยังอยู่หน้าเดิม → เป็น **self-transition** บนหน้ารายการ ไม่ใช่หน้าใหม่

**แตก 1 UC เป็นหลาย state เมื่อ:**
- activity diagram แสดงว่า actor ต้องกรอกข้อมูลเพิ่มในขั้นที่ 2 หลังระบบตอบกลับ (เช่น UC "ส่งคำขอยืม" = `CartDetail` → `RequestForm` เพราะกดจากตะกร้าแล้วต้องไปหน้ากรอกเหตุผลก่อน)
- UC มีทั้งหน้ารายการและหน้ารายละเอียด (list → detail เป็น 2 URL คนละหน้า)

**UC ที่ไม่มี state เลย (ถูกต้องและต้องระบุ):**
- UC ที่เป็น background job / auto-expire / scheduled task — ไม่มีใครกดปุ่ม จึงไม่มีหน้าจอ
- UC ที่เป็น API ให้ app อื่นเรียก
> ทั้งสองกรณีต้องเขียน `note` ระดับไฟล์กำกับไว้ว่า UC นั้นไม่มีหน้าจอเพราะอะไร ไม่ใช่เงียบหายไป — มิฉะนั้นตาราง traceability (§10) จะดูเหมือนทำไม่ครบ

---

## 4. `page_code` — ชื่ออ้างอิงของหน้าจอ (PlantUML alias)

`page_code` คือชื่อหลังคำว่า `as` ในไดอะแกรม และเป็น **ชื่อจริงที่ไหลต่อไปทั้งระบบ** (URL name, view class, template, ไฟล์ mockup) จึงต้องตั้งด้วยกฎ ไม่ใช่ตั้งตามใจ

```plantuml
state "รายการวัสดุและครุภัณฑ์\n(UC-01, extend UC-02)" as ItemList
'      └─ page_title (§5) ────────────────────┘      └ page_code ┘
```

### 4.1 รูปแบบบังคับ

| ข้อ | กฎ |
|---|---|
| ตัวอักษร | **ASCII PascalCase เท่านั้น** — ห้ามภาษาไทย, ห้าม space, ห้าม `-` `_`, ห้ามตัวเลข |
| ความยาว | 2-3 คำ / ≤ 24 ตัวอักษร (ต้องยังอ่านรู้เรื่องหลังแปลงเป็น kebab-case) |
| ความไม่ซ้ำ | unique **ทั้งไฟล์** (PlantUML จะรวมเป็น state เดียวเงียบ ๆ ถ้าซ้ำ — เป็นบั๊กที่หายาก) |
| ห้ามเด็ดขาด | ใส่เลข UC ใน page_code (`UC06Form`), ใช้คำกริยาลอย ๆ (`Submit`, `Approve`), ใช้ชื่อสถานะข้อมูล (`Pending`, `Approved`), ใช้ชื่อ generic (`Page1`, `MainPage`) |

### 4.2 อัลกอริทึมการตั้ง page_code (4 ขั้น)

**ขั้น 1 — หาคำนาม (สิ่งที่หน้าจอนี้แสดง) จาก Post-condition ของ UC ไม่ใช่จากชื่อ UC**

ชื่อ UC เป็นกริยาเสมอ ("ดูรายการ...", "ส่งคำขอ...") ถ้าแปลตรงจะได้ page_code ที่เป็นกริยา ซึ่งผิดกฎ §4.1 — ให้อ่าน **Post-condition** แทน เพราะ post-condition บอกว่า "สุดท้ายผู้ใช้เห็น/ได้อะไร" ซึ่งคือตัวหน้าจอ

| UC (กริยา) | Post-condition | คำนามที่ได้ |
|---|---|---|
| ดูรายการวัสดุและครุภัณฑ์ | "นักศึกษาเห็นภาพรวมของสิ่งของทั้งหมด" | `Item` |
| ส่งคำขอยืมสิ่งของ | "มีคำขอยืมสถานะรออนุมัติถูกสร้างขึ้น" | `Request` |
| จัดการสิทธิ์การยืมของนักศึกษา | "สถานะสิทธิ์ของนักศึกษาถูกอัปเดต" | `StudentPermission` |

**ขั้น 2 — เลือก suffix จาก Basic Flow** (ดูว่าขั้นแรกของ actor คือ "เปิดดู" หรือ "กรอก" หรือ "ยืนยัน")

| suffix | ใช้เมื่อ Basic Flow คือ | ตัวอย่าง |
|---|---|---|
| `List` | เปิดดูหลายรายการ + ค้นหา/กรอง/แบ่งหน้า | `ItemList`, `StudentList` |
| `Detail` | เปิดดู 1 รายการเจาะลึก | `ItemDetail`, `UserDetail` |
| `Form` | กรอกข้อมูลเพื่อสร้าง/แก้ไข แล้วกดบันทึก | `RequestForm`, `ItemForm` |
| `Confirm` | ยืนยันการกระทำที่ไม่ต้องกรอกข้อมูลใหม่ | `PickupConfirm`, `ReturnConfirm` |
| `Dashboard` | การ์ดสรุป + กราฟ + ทางลัด (ไม่มีตารางหลัก) | `StaffDashboard` |
| `Settings` | จัดการค่าตั้งต้น/ข้อมูลพื้นฐาน (มักมีแท็บ) | `InventorySettings` |
| `Import` / `Export` | อัปโหลดไฟล์เข้า / เลือกเงื่อนไขแล้วดาวน์โหลด | `BulkImport`, `ReportExport` |
| `Map` | แสดงผังเชิงพื้นที่/ตำแหน่ง | `PositionMap` |

**ขั้น 3 — เติม prefix role เฉพาะเมื่อชนกันจริง** (อย่าเติมทุกอันโดยไม่จำเป็น เพราะทำให้ชื่อยาวเกินเปล่า ๆ)

ถ้าคำนาม+suffix ซ้ำกันระหว่าง 2 role ในไฟล์เดียวกัน ให้เติม prefix `Stu` / `Staff` / `Admin`:
- นักศึกษาดูประวัติของตัวเอง + เจ้าหน้าที่ดูประวัติทุกคน → `StuHistoryList` และ `StaffHistoryList`
- ถ้ามี role เดียวใช้หน้านั้น → ไม่ต้องมี prefix (`PositionMap` พอ ไม่ต้อง `StuPositionMap`)

**ขั้น 4 — ทดสอบด้วยการแปลง** ถ้าแปลงเป็น kebab-case แล้วอ่านไม่รู้เรื่อง ให้กลับไปขั้น 1

### 4.3 ตาราง derive — page_code ไหลต่อไปเป็นอะไร (ต้องใส่ในไฟล์ .md ที่แนบกับไดอะแกรม)

| ปลายทาง | กฎแปลงจาก `page_code` | ตัวอย่างจาก `ItemList` |
|---|---|---|
| URL name (`urls.py`) | snake_case + prefix app namespace | `catalog:item_list` |
| URL path | kebab-case | `/catalog/item-list/` |
| View class | page_code + `View` | `ItemListView` |
| Template | `<app>/<snake_case>.html` | `catalog/item_list.html` |
| ไฟล์ mockup | `pages/page-<kebab-case>.html` | `pages/page-item-list.html` |

> การแปลงต้องเป็น **deterministic 1:1** — เห็น page_code แล้วต้องเดา URL/ไฟล์ได้ถูกทันทีโดยไม่ต้องเปิดตาราง นี่คือเหตุผลที่ §4.1 ห้ามใช้ตัวเลขและอักขระพิเศษ

---

## 5. `page_title` — ข้อความในกล่อง state

### 5.1 รูปแบบบังคับ

```
"<ชื่อหน้าภาษาไทย>\n(<UC ref>)"
```

- **บรรทัดที่ 1** = ชื่อหน้าภาษาไทย · **บรรทัดที่ 2** = UC ref ในวงเล็บ — คั่นด้วย `\n` เสมอ (ไม่ใช่ space) เพื่อให้กล่องไม่กว้างจนล้นหน้ากระดาษ
- ยาวรวม ≤ 2-3 บรรทัด บรรทัดละ ≤ ~30 ตัวอักษรไทย ถ้ายาวกว่านั้นให้ย้ายรายละเอียดไป `note` (§7)

### 5.2 ชื่อหน้าภาษาไทยต้องเป็น "คำนามวลี" ไม่ใช่ประโยคกริยา

หน้าจอคือ *สิ่ง* ไม่ใช่ *การกระทำ* — และชื่อนี้ต้องเอาไปใช้เป็น `<h1>` ของหน้าจริงและชื่อเมนู sidebar ได้ตรง ๆ ตาม [`UI_django_frontend.md`](UI_django_frontend.md) §4.3

| ❌ ประโยคกริยา (ผิด) | ✅ คำนามวลี (ถูก) |
|---|---|
| "ดูรายการวัสดุและครุภัณฑ์" | "รายการวัสดุและครุภัณฑ์" |
| "จัดการสิทธิ์การยืมของนักศึกษา" | "สิทธิ์การยืมของนักศึกษา" |

**ข้อยกเว้น 2 กรณีที่ใช้กริยาได้** เพราะหน้านั้นคือการกระทำจริง ๆ: หน้า `Form` ที่เป็นการส่งคำขอ ("ยืนยันส่งคำขอยืม") และหน้า `Confirm` ("ยืนยันรับของ")

### 5.3 รูปแบบ UC ref

| กรณี | เขียน | ความหมาย |
|---|---|---|
| 1 UC = 1 หน้า | `(UC-06)` | ปกติ |
| หน้าเดียวรองรับ `<<extend>>` | `(UC-01, extend UC-02)` | ความสามารถของ UC-02 เป็นฟิลด์ในหน้านี้ ไม่แยกหน้า |
| หน้าเดียวรองรับหลาย UC ที่ยุบรวม | `(UC-02, UC-03, UC-04)` | ตาม §3.1 |
| หน้าที่ `<<include>>` UC อื่น | `(UC-06, include UC-05)` | ต้องมี transition มาจากหน้าของ UC-05 (§6.5) |

**ห้ามใส่รหัส FR ใน page_title** — FR อยู่ในตาราง traceability (§10) เท่านั้น มิฉะนั้นกล่องจะรกและซ้ำซ้อนกับ usecase_description

---

## 6. `transition` — เส้นเชื่อมระหว่างหน้าจอ

### 6.1 กฎแม่บท: 1 transition = 1 ปุ่มหรือลิงก์ที่กดได้จริงบนหน้าต้นทาง

ถ้าวาดเส้นแล้วตอบไม่ได้ว่า "ผู้ใช้กดอะไรบนหน้า A เพื่อไป B" → เส้นนั้นผิด ต้องลบหรือแก้ · กลับกัน ถ้าหน้าจริงมีปุ่มแล้วไม่มีเส้น → mockup กับ Django URLconf จะขาดหน้าไป เพราะทั้งสองนับจากไดอะแกรมนี้

### 6.2 โครงของ label (3 ส่วน — ส่วนที่ 2, 3 ใส่เมื่อจำเป็น)

```
A --> B : <ข้อความบนปุ่มจริง>\n(<guard/เงื่อนไข>)\n→ <ผลลัพธ์หรือสถานะข้อมูลใหม่>
```

```plantuml
ItemDetail --> CartDetail : กด "เพิ่มลงตะกร้า"\n(จำนวนคงเหลือ > 0)
RequestForm --> MyRequestList : กด "ยืนยันส่งคำขอ"\n→ สร้างคำขอสถานะ "รออนุมัติ"
```

- **ส่วนที่ 1 (บังคับ)** — ข้อความบนปุ่มจริง ใส่ `" "` ครอบข้อความปุ่ม เพื่อให้แยกออกจากคำอธิบาย · คำนี้ต้องตรงกับปุ่มใน mockup และ Django template แบบคำต่อคำ
- **ส่วนที่ 2 (ถ้ามี)** — guard จาก Pre-condition/Business Rules (§6.3)
- **ส่วนที่ 3 (ถ้ามี)** — ผลลัพธ์ที่มองไม่เห็นจากชื่อปุ่ม โดยเฉพาะ **สถานะข้อมูลใหม่** ตาม §0

### 6.3 Guard — เอามาจาก Pre-condition และ Business Rules เท่านั้น

ห้ามคิด guard ขึ้นเอง ทุก guard ต้อง trace กลับไปยังบรรทัดใน `usecase_description.md` ได้:

| ที่มาใน usecase_description | เขียนเป็น guard |
|---|---|
| Pre-condition "สิ่งของต้องมีจำนวนคงเหลือ > 0" | `(จำนวนคงเหลือ > 0)` |
| Business Rule "วันที่ใช้งานบังคับกรอกเฉพาะเมื่อมีครุภัณฑ์" | `(ตะกร้ามีครุภัณฑ์ ≥ 1 ชิ้น)` |
| Pre-condition "คำขอต้องอยู่สถานะรออนุมัติ" | `(เฉพาะสถานะ "รออนุมัติ")` |

### 6.4 Self-transition — action ที่ทำเสร็จแล้วยังอยู่หน้าเดิม

ใช้ `A --> A` เมื่อผู้ใช้กดปุ่มแล้ว **ไม่เปลี่ยน URL** (ใน Django MVT คือ redirect กลับหน้าเดิม หรือ htmx swap บางส่วน) — พบใน 3 กรณี:

```plantuml
ItemList --> ItemList : กด "ค้นหา"/เลือกตัวกรอง (UC-02)         ' 1) extend UC ที่ไม่แยกหน้า
MyRequestList --> MyRequestList : กด "ยกเลิกคำขอ" (UC-07)\n(เฉพาะสถานะ "รออนุมัติ")  ' 2) action ในตาราง
RequestForm --> RequestForm : ข้อมูลไม่ครบ → แสดง validation error  ' 3) repeat/validation loop
```

**ข้อดีที่ต้องรักษาไว้:** self-transition ทำให้ทีมหน้าบ้านรู้ว่า "ปุ่มนี้ไม่ต้องสร้าง URL ใหม่" ซึ่งเป็นข้อมูลที่หายไปถ้าเขียนแค่ใน note

### 6.5 กฎความถูกต้องเชิงโครงสร้าง — ตรวจทุกครั้งก่อนส่ง

**(ก) ห้ามมี unreachable state — ทุก state ต้องมี transition ขาเข้า**

ทุก state ต้องเข้าถึงได้จาก `[*]` หรือจาก state อื่น · state ที่ประกาศไว้แต่ไม่มีเส้นเข้าเลย = **ฟังก์ชันที่ผู้ใช้เปิดไม่ได้** ซึ่งเป็นบั๊กที่ตรวจด้วยตาแล้วมองข้ามง่ายที่สุด เพราะกล่องยัง *ปรากฏ* ในภาพปกติ

วิธีตรวจ: ไล่ page_code ทุกตัวในไฟล์ แล้วค้นหาชื่อนั้นในฝั่ง **ขวา** ของ `-->` ถ้าไม่เจอเลยแม้แต่ครั้งเดียว = unreachable

```bash
grep -oE ' as [A-Za-z][A-Za-z0-9]*$' module_state_diagram.puml | sed 's/ as //' | sort -u | while read p; do grep -qE -- "--> +$p( |$)" module_state_diagram.puml || echo "UNREACHABLE: $p"; done
```

> `$` ท้าย pattern ทำให้จับเฉพาะ **leaf state** (บรรทัดที่จบด้วยชื่อ) และข้ามชื่อโซน composite ที่ลงท้ายด้วย `{` โดยอัตโนมัติ — ถูกต้องแล้ว เพราะโซนไม่ต้องมี transition ของตัวเอง
> ใช้ `grep -oE` ไม่ใช่ `-oP` เพราะ Git Bash บน Windows ไม่รองรับ `-P` ในบาง locale (`grep: -P supports only unibyte and UTF-8 locales`)

**(ข) ห้ามมี dead-end — ทุก state ต้องมี transition ขาออก**

ทุกหน้าต้องออกไปที่อื่นได้ อย่างน้อยต้องมีเส้น "กลับ" · หน้าที่เข้าไปแล้วออกไม่ได้ = ผู้ใช้ติดอยู่ในหน้านั้น (ยอมรับได้เฉพาะ state ที่ชี้ไป `[*]` เช่นหน้าออกจากระบบ)

**(ค) `<<include>>` ต้องมีเส้นรองรับ** — ถ้า usecase_description บอกว่า UC-06 `<<include>>` UC-05 แปลว่าเข้าหน้าของ UC-06 ได้จากหน้าของ UC-05 เท่านั้น ต้องมี `CartDetail --> RequestForm` และ **ห้าม**มีเส้นตรงจากที่อื่นเข้า `RequestForm`

**(ง) `<<extend>>` ต้อง *ไม่* มี state ใหม่** — ถ้าเห็น state ที่ page_title มีคำว่า extend เป็น state เดี่ยว ๆ แปลว่าแตกหน้าเกิน ให้ยุบตาม §3.1

### 6.6 สิ่งที่ห้ามวาดเป็น transition

| สิ่งที่ห้ามวาด | เพราะ | เขียนที่ไหนแทน |
|---|---|---|
| Background job / auto-expire (เช่น คำขอหมดอายุเอง) | ไม่มีผู้ใช้กดปุ่ม จึงไม่ใช่การนำทาง | `note` ระดับโซน/ไฟล์ |
| การส่งอีเมล / in-app notification (`fork` ใน activity) | ไม่เปลี่ยนหน้าจอของผู้ใช้ที่กด | บรรทัด `แจ้งเตือน:` ใน note ของ state |
| ขั้นตอนภายในระบบ (ตรวจ session, เขียน DB, ลด stock) | เป็นสิ่งที่เกิดบนเส้น ไม่ใช่ปลายทาง | ส่วนที่ 3 ของ label (§6.2) |
| Modal / toast / dialog ยืนยัน | เป็น component ในหน้าเดิม ไม่ใช่ URL ใหม่ | `note` หรือ self-transition |
| การเปลี่ยน role ของผู้ใช้ | เกิดตอน login ครั้งถัดไป ไม่ใช่การกดปุ่มข้ามโซน | `note` ระดับไฟล์ |

---

## 7. `note` ประจำ state — คำนำบรรทัดมาตรฐาน

ทุก state ควรมี `note` กำกับ โดยแต่ละบรรทัดต้องขึ้นต้นด้วยคำนำที่กำหนดไว้เท่านั้น (ใส่เฉพาะบรรทัดที่มีข้อมูลจริง ไม่ต้องใส่ครบทุกบรรทัด) — **แต่ละบรรทัดต้อง map จาก usecase_description แบบตรงตัว ไม่ใช่เขียนเพิ่มเอง**

| บรรทัด | เอามาจาก | ใช้ทำอะไรต่อ |
|---|---|---|
| `แสดง:` / `ฟิลด์:` | **Basic Flow** ขั้นที่ระบบแสดงผล + ฟิลด์ที่ actor กรอก | องค์ประกอบบนหน้าจอใน mockup + ฟิลด์ใน Django form |
| `ปุ่ม:` | **Basic Flow** ปุ่ม/action ที่กดได้บนหน้านั้น (แยกจาก `แสดง:` เพราะเน้น action ไม่ใช่ข้อมูล read-only) | ปุ่มจริงใน mockup + guard ว่าปุ่มไหนแสดงเมื่อไร |
| `ว่าง:` / `ผิดพลาด:` | **Alternative/Exception Flow** | empty state + error message ที่ mockup ต้อง trigger ได้จริง |
| `กฎ:` | **Business Rules** ที่กระทบ UI | guard ที่ต้องบังคับใน view/template |
| `แจ้งเตือน:` | `fork` ใน activity diagram (§6.6) | toast / badge กระดิ่ง |
| `หมายเหตุ:` | ข้อมูลเสริม/ความสัมพันธ์กับ UC อื่นที่ไม่เข้าพวกข้างบน (catch-all) | บริบทประกอบสำหรับคนอ่าน ไม่ผูกกับ mockup โดยตรง |

**ห้ามตั้งคำนำใหม่นอกเหนือจาก 6 แบบนี้** (เช่น `ต่อยอด:`, `ยืนยันซ้ำ:`, `ฟิลด์แก้ไขได้:`) — ถ้าเนื้อหาไม่เข้าพวกไหนเป๊ะ ให้เลือกอันที่ใกล้เคียงที่สุดแล้วเขียนรายละเอียดต่อในวงเล็บ/ประโยคเดียวกัน (เช่น `ฟิลด์: เบอร์โทรศัพท์ (แก้ไขได้)` แทนที่จะสร้างคำนำใหม่ `ฟิลด์แก้ไขได้:`) เพื่อให้ทุกไฟล์ในระบบใช้คำศัพท์ชุดเดียวกัน ค้นหา/เทียบกันได้ตรง ๆ

```plantuml
note right of CartDetail
  แสดง: รายการสินค้าในตะกร้า + ราคารวม
  ฟิลด์: ช่องแก้ไขจำนวนต่อรายการ, ปุ่มลบรายการ
  ว่าง: "ยังไม่มีสินค้าในตะกร้า"
  ผิดพลาด: จำนวนที่กรอกเกินสต๊อกจริง → ไม่อนุญาตให้เพิ่ม
end note
```

> **กฎกันการแต่งเรื่อง:** ถ้าจะเขียนบรรทัด `ผิดพลาด:` หรือ `กฎ:` ที่หา**ไม่เจอ**ใน usecase_description → **ห้ามเขียนลงไปเอง** ให้กลับไปถามเจ้าของเอกสารว่าจะเพิ่มกฎนั้นใน usecase_description ก่อน แล้วค่อยวาดตาม (ไดอะแกรมเป็นภาพสะท้อนของเอกสาร ไม่ใช่ที่คิดข้อกำหนดใหม่ — ดู §11)

---

## 8. โซนและ Entry Point

### 8.1 `overview_state_diagram.puml` — ระดับ app

ไฟล์นี้ตอบคำถาม "ผู้ใช้เข้าถึงแต่ละ app ได้อย่างไร" ไม่ใช่ "ในแต่ละ app มีหน้าอะไร":

```plantuml
state "หน้าเข้าสู่ระบบ\n(UC-16)" as Login
state "Dashboard กลาง" as Dashboard
state "จัดการคลังสินค้า\n(catalog)" as CatalogApp

[*] --> Login
Login --> Dashboard : ยืนยันตัวตนสำเร็จ\n(บทบาทจาก SSO / Role Override)
Dashboard --> CatalogApp : กดเมนู "คลังสินค้า"
CatalogApp --> Dashboard : กด "← กลับหน้าหลัก"
Dashboard --> [*] : ออกจากระบบ
```

- **1 state = 1 Django app** ตั้ง page_code เป็น `<AppName>App` (`CatalogApp`, `BorrowApp`) + มี `Dashboard` และ `Login` เป็น state พิเศษ
- label ขาเข้าต้องเป็นข้อความบนการ์ด/เมนูจริงใน Dashboard — [`UI_django_frontend.md`](UI_django_frontend.md) §4.2 นับ **1 การ์ด = 1 app = 1 เมนู** จากที่นี่
- label ขาออกต้องเป็นคำเดียวกับปุ่ม "กลับหน้าหลัก" ที่ [`mockup_generate_guide.md`](mockup_generate_guide.md) §4.1 บังคับให้มีทุก mockup
- ห้ามใส่หน้าจอย่อยของ app ในไฟล์นี้ (นั่นเป็นหน้าที่ของ `module_state_diagram`)

### 8.2 `module_state_diagram.puml` — แบ่งโซนตาม role เมื่อ app เดียวมีหลาย role

ใช้ composite state คลุม แล้วประกาศ transition ข้ามโซน (ถ้ามี) ไว้**นอก**บล็อก:

```plantuml
state "นักศึกษา (Student)" as StudentZone {
  state "..." as StuHome
  [*] --> StuHome
}
state "เจ้าหน้าที่ (Staff)" as StaffZone {
  state "..." as StaffDashboard
  [*] --> StaffDashboard
}
```

- `[*] --> <หน้าแรกของ role>` **หนึ่งอันต่อหนึ่งโซน** — คือหน้าที่ผู้ใช้เห็นทันทีหลังเข้ามาที่ app นี้
- **โซนต่างกันไม่ต้องมีเส้นเชื่อมกัน** — ผู้ใช้คนหนึ่งมี role เดียวต่อ session การข้าม role เกิดตอน login ใหม่เท่านั้น (§6.6)

---

## 9. Style มาตรฐาน — Monochrome + ภาษาไทย

ใช้กฎเดียวกับ [`activity_diagram_generate_guide.md`](activity_diagram_generate_guide.md) §5: **โทนเทา-ขาวทั้งไดอะแกรม ห้ามใช้สีแยกแต่ละโซน/แต่ละ role** เพราะสีจะสื่อความหมายซ้ำกับชื่อโซนที่มีอยู่แล้ว และพอ role เยอะจะกลายเป็นสีรุ้งอ่านไม่ออก

```plantuml
!pragma layout smetana
skinparam defaultFontName "TH Sarabun New"
skinparam defaultFontSize 14
!theme plain
skinparam state {
  BackgroundColor #F5F5F5
  BorderColor #424242
  FontName "TH Sarabun New"
  FontSize 13
  ArrowFontName "TH Sarabun New"
}
skinparam note {
  BackgroundColor #FFFDE7
  BorderColor #9E9E9E
}
```

- บันทึกไฟล์เป็น **UTF-8 ไม่มี BOM** เสมอ
- render ผ่าน CLI: `java -Dfile.encoding=UTF-8 -jar plantuml.jar -charset UTF-8 module_state_diagram.puml`
- บังคับ `!pragma layout smetana` — Graphviz บน Windows อ่าน UTF-8 ไม่ตรง ทำให้สระ/วรรณยุกต์ไทยเพี้ยน
- ฟอนต์: Windows ใช้ `TH Sarabun New` · Linux/PlantUML server เปลี่ยนเป็น `Noto Sans Thai`
- ถ้ากล่องเยอะจนภาพกว้างเกิน ให้ย้ายรายละเอียดจาก page_title ไป note (§5.1) ก่อน — **ห้ามแก้ด้วยการลบ state**

---

## 10. ตาราง Traceability (บังคับ — แนบเป็น .md คู่กับ .puml)

ตารางนี้คือหลักฐานว่าไม่มี UC หลุด และเป็นตัวที่ [`mockup_generate_guide.md`](mockup_generate_guide.md) §4.2 กับ [`UI_django_frontend.md`](UI_django_frontend.md) §0 เอาไปใช้ต่อโดยตรง:

| UC | ชื่อ Use Case | ไฟล์ activity ที่ใช้ map | `page_code` | URL name | Template | ไฟล์ mockup |
|---|---|---|---|---|---|---|
| UC-01 | ดูรายการสินค้า | `activity/activity_uc01_list.puml` | `ItemList` | `catalog:item_list` | `catalog/item_list.html` | `pages/page-item-list.html` |
| UC-02 | ค้นหาและกรอง | `activity/activity_uc02_search.puml` | `ItemList` *(extend)* | (เดียวกัน) | (เดียวกัน) | (เดียวกัน) |
| UC-99 | *(auto-expire job)* | `activity/activity_uc99_expire.puml` | **— ไม่มีหน้าจอ** | — | — | — |

- **UC ที่ยุบรวมกันจะมี page_code ซ้ำได้** (แถว UC-02 ข้างบน) — ไม่ใช่ข้อผิดพลาด แต่ต้องกำกับ *(extend)* / *(รวมหน้า)* ให้ชัด
- **UC ที่ไม่มีหน้าจอต้องมีแถวและเขียนเหตุผล** — ห้ามลบแถวทิ้ง (§3.1)
- จำนวน page_code ที่ไม่ซ้ำ = จำนวนหน้าจอ = จำนวน `path()` = จำนวนไฟล์ใน `pages/` ต้องตรงกันทั้ง 3 ที่

---

## 11. เมื่อพบว่า usecase_description / activity diagram **ขัดกันเชิงตรรกะ** — ห้ามแก้เอง

> **ขอบเขตของข้อนี้:** §11 คุมเฉพาะความขัดแย้ง **เชิงตรรกะ/ข้อกำหนด** (logic & requirement) — ส่วนการแก้ **ชื่อหน้าที่อ้างผิด/อ้างซ้ำ** ใน activity diagram ให้ทำได้เลยโดยไม่ต้องถาม ตาม §12 (เป็นการแก้เชิงชื่อเรียก ไม่ใช่เชิงตรรกะ)

ระหว่างวาดจะเจอบ่อยว่าเอกสารต้นทางขัดกันเอง เช่น alternative flow บอกให้ส่งต่อไป UC อื่นแต่ไม่มีทางไปถึง, pre-condition ขัดกับ business rule, หรือ activity diagram มีขั้นตอนที่ไม่มีใน basic flow

**ลำดับที่ถูกต้อง:**
1. **หยุด** อย่าวาดสิ่งที่เอกสารไม่ได้บอก และอย่า "เติมให้สมเหตุสมผล" เอง
2. บันทึกจุดขัดแย้งเป็นรายการ พร้อมอ้าง `ไฟล์:บรรทัด` ทั้งสองฝั่งที่ขัดกัน
3. **ถามเจ้าของเอกสารก่อนแก้** ว่าจะแก้ที่ `usecase_description.md` / `activity_*.puml` หรือจะวาด state diagram ตามเอกสารเดิมไปก่อน
4. เมื่อได้คำตอบแล้วจึงแก้เอกสารต้นทาง **ก่อน** แล้ววาด state diagram ตามเอกสารที่แก้แล้ว

**เหตุผล:** state diagram เป็นเอกสารปลายน้ำ ถ้า "แก้เงียบ ๆ" ที่ปลายน้ำ เอกสารต้นน้ำจะยังผิดอยู่และไปโผล่เป็นความขัดแย้งอีกครั้งตอนทำ mockup/โค้ดจริง — และกรรมการสอบจะเจอว่าเอกสาร 2 ฉบับพูดไม่ตรงกัน

---

## 12. ขั้นตอนสุดท้าย — Audit `page_code` ใน Activity Diagram (แก้ได้ทันที ไม่ต้องถาม)

**ทำขั้นนี้หลังจาก state diagram เสร็จและผ่าน §6.5 แล้วเท่านั้น** เพราะต้องมี "รายชื่อ page_code ที่เป็นทางการ" ก่อนจึงจะรู้ว่า activity diagram อ้างถูกหรือผิด

**หลักการ: `module_state_diagram.puml` เป็นแหล่งความจริงเดียว (single source of truth) ของชื่อหน้าจอ** — activity diagram ต้องอ้าง page_code ผ่าน **partition `frontend:<PageCode>`** ตามกฎใน [`activity_diagram_generate_guide.md`](activity_diagram_generate_guide.md) §1 (ไม่ใช่ partition ชื่อ actor + comment อธิบายหน้าแบบลอย ๆ) การผูก page_code เข้ากับ partition โดยตรงแบบนี้ทำให้ **หน้าจอที่ activity diagram อ้างถึง กับหน้าจอใน state diagram เป็นชื่อเดียวกันโดยโครงสร้าง** — งาน "audit" ในหัวข้อนี้จึงเหลือแค่การเทียบชื่อ ไม่ต้องตีความประโยคภาษาไทยอีกต่อไป

> **สำหรับ activity diagram ที่เขียนก่อนกฎนี้มีผล** (partition ยังเป็นชื่อ actor เช่น `นักศึกษา`/`เจ้าหน้าที่` และอธิบายหน้าด้วยประโยคลอย ๆ) ต้องแปลง partition เป็น `frontend:<PageCode>` ก่อน (ดูตัวอย่างการแปลงใน activity_diagram_generate_guide.md §1.2) แล้วจึงมาทำ audit ตามหัวข้อนี้ต่อ

### 12.1 อะไรแก้ได้ทันที vs อะไรต้องถาม

| ประเภทที่พบ | ตัวอย่าง | ทำอย่างไร |
|---|---|---|
| **(ก) อ้างผิดหน้า** | activity ใช้ `\|frontend:ItemOverview\|` ตอนจบ แต่ตาม state diagram ปลายทางจริงของ flow นี้คือ `CartDetail` | **แก้ activity ได้ทันที ไม่ต้องถาม** — เปลี่ยน partition ให้ตรง page_code จริง |
| **(ข) อ้างหน้าที่ไม่มีจริง** | activity ใช้ `\|frontend:OrderSummary\|` แต่ state diagram ไม่มีหน้านี้ (ยุบรวมไปกับ `CustOrderList` แล้ว) | **แก้ activity ได้ทันที** — เปลี่ยน partition ไปหน้าที่ยุบรวมแล้ว |
| **(ค) สร้างหน้าซ้ำ** | activity หลายไฟล์ใช้ partition คนละชื่อสำหรับหน้าเดียวกัน (`frontend:CartDetail` / `frontend:CartReview` / `frontend:CartSummary`) | **แก้ activity ได้ทันที** — รวมให้เหลือ `frontend:<PageCode>` เดียว |
| **(ง) partition ยังไม่เปลี่ยนตามหน้าจริง** | flow พาไปหน้าอื่นจริง (ตาม basic flow) แต่ partition ในไฟล์ activity ไม่ได้สลับตาม — ยังค้างชื่อเดิม | **แก้ activity ได้ทันที** — เพิ่มบรรทัด `\|frontend:<PageCode>\|` ตรงจุดที่หน้าจอเปลี่ยนจริง ตาม activity guide §1.2 |
| **(จ) ขั้นตอน/เงื่อนไขไม่ตรงกัน** | activity มี decision ที่ usecase_description ไม่มี หรือ business rule ขัดกัน (เช่น ลำดับ step สลับกับที่ระบุใน Basic Flow) | **ห้ามแก้เอง — ถามก่อนตาม §11** |

> เส้นแบ่งคือ: **ถ้าแก้แล้วพฤติกรรมของระบบไม่เปลี่ยน (เปลี่ยนแค่ partition/ชื่อที่ใช้เรียกหน้า) → แก้ได้เลย** · ถ้าแก้แล้วขั้นตอน/เงื่อนไข/ลำดับ/ผลลัพธ์เปลี่ยน → เข้า §11 ต้องถามก่อน (ดูตัวอย่างจริง: การสลับลำดับ "ตรวจข้อมูลติดต่อ" ให้เกิดหลังกรอกฟอร์มแทนที่จะเกิดก่อน เป็นกรณี (จ) เพราะเปลี่ยนลำดับขั้นตอนจริง)

### 12.2 รูปแบบ partition ที่ต้องมี (อ้างอิง activity_diagram_generate_guide.md §1)

ทุก partition ที่เป็นหน้าจอต้องเขียนเป็น `\|frontend:<PageCode>\|` ตรงตัวอักษรกับชื่อหลัง `as` ใน state diagram เสมอ — **นี่คือกลไกหลักที่ทำให้ page_code ถูกอ้างอิงตรงกันทั้งสองไฟล์** (ไม่ใช่แค่ comment/annotation แบบเดิม):

```plantuml
' ถูกต้อง — partition คือ page_code ตรง ๆ สลับตามหน้าจอที่เปลี่ยนจริง
|frontend:CartDetail|
:กดยืนยันส่งคำขอยืม;

|backend|
:ตรวจสต๊อกคงเหลือ;

|frontend:CheckoutForm|
:กรอกเหตุผลการยืมและวันที่ใช้งาน;
```

```plantuml
' ผิด — partition เป็นชื่อ actor ลอย ๆ ต้องอนุมานเอาเองว่าอยู่หน้าไหน
|นักศึกษา|
:กดยืนยันส่งคำขอยืม;
:กรอกเหตุผลการยืมและวันที่ใช้งาน;
```

### 12.3 ขั้นตอนการ audit (4 ขั้น)

**ขั้น 1 — ดึงรายชื่อ page_code ที่เป็นทางการจาก state diagram**

```bash
grep -oE ' as [A-Za-z][A-Za-z0-9]*$' module_state_diagram.puml | sed 's/ as //' | sort -u
```

**ขั้น 2 — ตรวจว่าทุก `frontend:X` ใน activity มี `X` อยู่จริงใน state diagram (orphan reference, ต้องไม่มี output)**

```bash
grep -ohE '\|frontend:[A-Za-z][A-Za-z0-9]*\|' ../activity/*.puml | tr -d '|' | cut -d: -f2 | sort -u | while read p; do grep -qE " as $p$" module_state_diagram.puml || echo "ORPHAN ใน activity (ไม่มีใน state diagram): $p"; done
```

ถ้ามี output แปลว่า activity อ้างหน้าที่ไม่มีจริง (กรณี ก/ข ใน §12.1) — แก้ partition ให้ชี้ไปหน้าที่มีอยู่จริง

**ขั้น 3 — ตรวจย้อนกลับ: หน้าที่มีอยู่จริงแต่ไม่มี activity ไฟล์ไหนอ้างถึงเลย**

```bash
grep -oE ' as [A-Za-z][A-Za-z0-9]*$' module_state_diagram.puml | sed 's/ as //' | sort -u | while read p; do grep -qrE "\|frontend:$p\|" ../activity/ || echo "ไม่มี activity อ้างถึง: $p"; done
```

ผลลัพธ์ของขั้นนี้ **ไม่ถือเป็น error เสมอไป** — หน้าที่เป็นแค่การแสดงข้อมูล (เช่น `PositionMap`) อาจไม่มีขั้นตอนใน activity diagram ที่ต้องพูดถึงมัน แต่ถ้าเป็นหน้าที่ควรมี flow (`Form`, `Confirm`) แล้วไม่มีใครอ้าง แปลว่าน่าจะสร้าง state เกินมา → กลับไปทวนตาม §3.1

**ขั้น 4 — ตรวจ transition ระดับคู่ (deeper check): ทุกจุดที่ partition สลับกลางไฟล์ activity ต้องมี edge คู่กันใน state diagram**

ดึงลำดับ `frontend:X` ที่ปรากฏในแต่ละไฟล์ activity ตามลำดับ (ไม่ใช่แค่เทียบว่ามีอยู่จริง) แล้วเทียบกับ arrow ใน state diagram — ต้องระวัง **if/elseif/else ในไฟล์ activity อ่านเป็นลำดับต่อเนื่องผิด ๆ ได้** (กิ่งที่แยกจากกันจะถูกเข้าใจผิดว่าเป็น path เดียวต่อกัน) จึงต้องตรวจด้วยตาซ้ำทุกจุดที่ได้ output ก่อนสรุปว่า "หายจริง" หรือเป็นแค่ false positive จาก branching:

```bash
for f in ../activity/*.puml; do
  grep -oE '\|frontend:[A-Za-z][A-Za-z0-9]*\|' "$f" | tr -d '|' | cut -d: -f2 | uniq | awk 'NR>1{print prev" --> "$0} {prev=$0}'
done | sort -u
```

นำผลลัพธ์แต่ละคู่มาเทียบกับ `A --> B` ใน state diagram — คู่ไหน **MISSING** จริง (ไม่ใช่ artifact จาก if/else) ให้เพิ่ม transition ใน state diagram (ถ้าเป็นการเพิ่ม path ที่ไม่ขัดกับ usecase_description) หรือแก้ activity ให้ตรงกับ transition ที่มีอยู่แล้ว (ถ้า activity เขียนผิดลำดับ)

### 12.4 บันทึกผลการ audit

ใส่ตารางนี้ต่อท้ายไฟล์ `module_state_diagram.md` (ตาราง traceability §10) เพื่อให้เห็นว่าแก้อะไรไปบ้าง — สำคัญเพราะเป็นการแก้ไฟล์ต้นทางโดยไม่ได้ถาม จึงต้องมีร่องรอยให้ตรวจย้อนหลังได้:

| # | ไฟล์ activity | เดิม partition/ลำดับ | แก้เป็น | ประเภท (§12.1) |
|---|---|---|---|---|
| 1 | `activity/activity_uc06_submit.puml` | `\|นักศึกษา\|` ตลอดไฟล์ | `\|frontend:CartDetail\|` → `\|frontend:CheckoutForm\|` ตามหน้าที่เปลี่ยนจริง | (ง) partition ไม่เปลี่ยนตามหน้าจริง |
| 2 | `activity/activity_uc04_cart.puml` | `\|frontend:CartReview\|` | `\|frontend:CartDetail\|` | (ค) สร้างหน้าซ้ำ |

---

## 13. Checklist ก่อนส่งไดอะแกรม

**นิยาม state**
- [ ] ทุก state เป็น **หน้าจอจริง (1 URL)** ไม่มี state ที่เป็นสถานะข้อมูล (`Pending`/`Approved`) หรือ modal/toast (§0, §6.6)
- [ ] ทุก state trace กลับไปยัง UC ใน`usecase_description.md` ได้ และทุกขั้นตอนฝั่ง actor ใน `activity/*.puml` มีหน้าจอรองรับ (§3)
- [ ] UC ที่เป็น `<<extend>>` **ไม่มี** state ของตัวเอง — ยุบเข้าหน้าฐานแล้ว (§3.1, §6.5ง)
- [ ] UC ที่ไม่มีหน้าจอ (background job/API) มี `note` อธิบายเหตุผล ไม่ได้หายไปเงียบ ๆ (§3.1)

**page_code (§4)**
- [ ] ASCII PascalCase, unique ทั้งไฟล์, ≤ 24 ตัวอักษร — ไม่มีเลข UC / คำกริยาลอย / ชื่อสถานะข้อมูล / `Page1`
- [ ] มี suffix จากตาราง §4.2 ขั้น 2 และเป็นคำนามที่มาจาก Post-condition ไม่ใช่ชื่อ UC
- [ ] prefix role (`Stu`/`Staff`/`Admin`) ใส่**เฉพาะ**คู่ที่ชนกันจริง
- [ ] แปลงเป็น URL name / template / ไฟล์ mockup ได้ตรงตาราง §4.3 แบบ 1:1

**page_title (§5)**
- [ ] รูปแบบ `"<ชื่อไทย>\n(UC-xx)"` ทุก state — คำนามวลี (ยกเว้นหน้า Form/Confirm) ไม่มีรหัส FR
- [ ] หน้าที่รองรับหลาย UC เขียน ref ครบตาม §5.3 (`extend` / `include` / รายการ UC)

**transition (§6)**
- [ ] ทุกเส้นตอบได้ว่า "กดปุ่มอะไรบนหน้าต้นทาง" และ label ใส่ `" "` ครอบข้อความปุ่มจริง
- [ ] **ไม่มี unreachable state** — รัน `grep` ใน §6.5(ก) แล้วไม่มี output
- [ ] **ไม่มี dead-end** — ทุก state มีขาออก (อย่างน้อยเส้น "กลับ") ยกเว้น state ที่ชี้ `[*]`
- [ ] `<<include>>` มีเส้นจากหน้าของ UC ที่ถูก include และไม่มีทางเข้าอื่น (§6.5ค)
- [ ] guard ทุกตัว trace กลับไป Pre-condition/Business Rules ได้ ไม่ใช่คิดเอง (§6.3)
- [ ] action ที่ไม่เปลี่ยน URL เป็น self-transition ไม่ใช่ state ใหม่ (§6.4)
- [ ] background job / notification / ขั้นตอนภายในระบบ **ไม่ได้**ถูกวาดเป็นเส้น (§6.6)

**note, โซน, style**
- [ ] `note` ใช้เฉพาะคำนำ 6 แบบ (`แสดง:`, `ฟิลด์:`, `ปุ่ม:`, `ว่าง:`, `ผิดพลาด:`, `กฎ:`, `แจ้งเตือน:`, `หมายเหตุ:`) และทุกบรรทัด map จาก usecase_description จริง (§7) — ไม่สร้างคำนำใหม่นอกเหนือจากนี้
- [ ] แต่ละโซน role มี `[*] -->` เข้าหน้าแรกของ role นั้น 1 อัน และไม่มีเส้นข้ามโซน (§8.2)
- [ ] `overview_state_diagram.puml` มี 1 state ต่อ 1 app + `Dashboard` + `Login` และไม่มีหน้าจอย่อยปน (§8.1)
- [ ] **โทนเทา-ขาวล้วน** ไม่มีสีแยก role/โซน · UTF-8 ไม่มี BOM · มี `!pragma layout smetana` (§9)

**Audit `page_code` ใน activity diagram (§12 — ขั้นตอนสุดท้าย)**
- [ ] ทำ audit **หลัง** state diagram ผ่าน §6.5 แล้ว (ไม่ใช่ทำพร้อมกัน)
- [ ] ทุก partition หน้าจอใน `activity/*.puml` เขียนเป็น `\|frontend:<PageCode>\|` ตรงตัวอักษรกับ state diagram (ไม่ใช่ partition ชื่อ actor + comment อธิบายหน้าลอย ๆ) ตาม §12.2
- [ ] partition สลับตามจริงทุกจุดที่หน้าจอเปลี่ยน (ตาม activity guide §1.2) — ไม่ค้างชื่อเดิมทั้งที่ basic flow ระบุว่าไปหน้าอื่นแล้ว
- [ ] กรณี (ก)-(ง) — อ้างผิดหน้า / อ้างหน้าที่ไม่มีจริง / สร้างหน้าซ้ำ / partition ไม่เปลี่ยนตามหน้าจริง — **แก้ activity ให้ตรงแล้ว** (ไม่ต้องถาม)
- [ ] กรณี (จ) ขั้นตอน/เงื่อนไข/ลำดับไม่ตรงกัน — **ไม่ได้แก้เอง** จดไว้ถามตาม §11
- [ ] คำสั่งตรวจ orphan reference (§12.3 ขั้น 2) และตรวจย้อนกลับ (ขั้น 3) ไม่มี output ผิดปกติ
- [ ] ตรวจ transition ระดับคู่ (§12.3 ขั้น 4) แล้ว — คู่ที่ MISSING จริง (ไม่ใช่ artifact จาก if/else) ถูกแก้ไขหรือเพิ่มแล้ว
- [ ] มีตารางบันทึกผล audit (§12.4) ต่อท้าย `module_state_diagram.md` ทุกจุดที่แก้

**เอกสารประกอบ**
- [ ] มีตาราง traceability §10 ครบทุก UC และจำนวน page_code ที่ไม่ซ้ำ = จำนวน `path()` = จำนวนไฟล์ `pages/`
- [ ] จุดที่เอกสารต้นทางขัดกัน**เชิงตรรกะ**ถูก **ถามก่อน** ไม่ได้แก้เองเงียบ ๆ (§11) — ต่างจากการแก้ชื่อหน้าที่ทำได้เลย (§12)
