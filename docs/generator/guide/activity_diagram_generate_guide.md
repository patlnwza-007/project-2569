# คู่มือการวาด Activity Diagram แบบมี Swimlane (Activity Diagram Generation Guide)

> ใช้คู่กับ [`activity_diagram_template.md`](../template/activity_diagram_template.md) เป็นจุดเริ่มก๊อปปี้ และดู [`activity_diagram_example.md`](../example/activity_diagram_example.md) เป็นตัวอย่างที่ทำตามกฎครบทุกข้อ
>
> **สถาปัตยกรรมเป้าหมาย: Django MVT monolith** — business logic ทั้งหมดอยู่ในโปรเจกต์เดียว (ไม่มี microservice/API Gateway/JWT) ยืนยันตัวตนด้วย django-allauth ผ่าน UBU Single Sign-On (@ubu.ac.th) (session) กฎด้านล่างสะท้อนความจริงของ monolith ไม่ใช่คลัสเตอร์ service

---

## 0. นิยาม: Activity Diagram ต่างจาก Use Case Diagram อย่างไร (อ่านก่อนเริ่ม)

**Use case diagram** ([`usecase_generate_guide.md`](usecase_generate_guide.md)) ตอบคำถาม "ผู้ใช้ทำอะไรได้บ้าง" ในระดับเป้าหมาย (goal-level) — ห้ามลงรายละเอียดขั้นตอนภายใน

**Activity diagram** (ไฟล์นี้) ตอบคำถามตรงข้าม — "1 use case นั้นทำงานเป็นขั้นตอนอย่างไรจริง ๆ" รวมถึง**ใครทำอะไร ที่ layer/แอปไหน และเรียกระบบภายนอกตัวใดบ้าง** จึงเป็นที่ที่ business rule, decision, loop, และการติดต่อระบบภายนอกที่ถูกห้ามไม่ให้ใส่ใน use case diagram ควรมาอยู่แทน

ใช้ activity diagram แบบมี swimlane เมื่อ:
- ต้องการอธิบาย 1 use case ที่มีขั้นตอนข้ามหลายฝ่าย (ผู้ใช้ ↔ ระบบ ↔ บริการภายนอก)
- ต้องการโชว์กรรมการสอบว่า "ใครทำอะไร ที่ไหน" ในกระบวนการเดียว
- ต้องการเห็น decision/loop ที่ use case diagram บอกไม่ได้ (เช่น ต้องวนกรอกใหม่จนผ่าน validation)

---

## 1. กฎเรื่อง Partition (Swimlane) — ผูกตรงกับ `page_code` ของ State Diagram

**1.1 มี partition แค่ 3 ชนิด — และชนิด "หน้าจอ" ต้องเขียนเป็น `frontend:<page_code>` เสมอ**

Partition ไม่ได้แทน "ใครเป็นคนกด" อีกต่อไป แต่แทน **"ผู้ใช้กำลังยืนอยู่หน้าจอไหน (ฝั่ง frontend) หรือกำลังประมวลผลอยู่ฝั่งไหน (backend/external)"**:

| ชนิด partition | เขียนอย่างไร | คือใคร/อะไร |
|---|---|---|
| **หน้าจอ (frontend)** | `frontend:<PageCode>` | ผู้ใช้ (ไม่ว่า role ไหน) ขณะอยู่บนหน้าจอที่ชื่อ `PageCode` — **`PageCode` ต้องตรงกับชื่อหลัง `as` ใน `module_state_diagram.puml` ของหน้านั้นแบบตัวอักษรต่อตัวอักษร** (ดู [`ui_state_diagram_generate_guide.md`](ui_state_diagram_generate_guide.md) §4) |
| **ฝั่งเซิร์ฟเวอร์ (backend)** | `backend` | โค้ดฝั่ง server ทั้งหมดของโปรเจกต์ (view + model + business logic) — ชื่อคงที่ไม่ต้องระบุชื่อโปรเจกต์ซ้ำทุกไฟล์ |
| **บริการภายนอกจริง** | `<ชื่อบริการ> (external)` | สิ่งที่อยู่นอกโปรเจกต์ Django (UBU Single Sign-On, เซิร์ฟเวอร์อีเมล/SMTP, ที่เก็บไฟล์ภายนอก) — เส้นขอบประ (ดู §5) |

**ทำไมเปลี่ยนจาก partition ชื่อ actor (`นักศึกษา`, `เจ้าหน้าที่`) มาเป็น `frontend:<PageCode>`:** partition ชื่อ actor บอกได้แค่ "ใครกด" แต่บอกไม่ได้ว่า "กดจากหน้าไหน" ทำให้ต้องมานั่งไล่เทียบภายหลังว่า activity diagram อ้างหน้าตรงกับ state diagram หรือเปล่า (เป็นที่มาของงาน audit แยกต่างหาก) — การใช้ `frontend:<PageCode>` ทำให้ **หน้าจอที่ activity diagram อ้างถึง กับหน้าจอใน state diagram เป็นชื่อเดียวกันโดยโครงสร้าง (by construction)** ไม่ต้อง audit ย้อนหลังอีกต่อไป: แค่ grep รายชื่อ partition `frontend:*` มาเทียบกับ `module_state_diagram.puml` ก็พอ (ดู §7 checklist)

**1.2 ทุกครั้งที่ actor เปลี่ยนหน้าจอกลางกระบวนการ ต้องเปลี่ยน partition ตาม `PageCode` ใหม่**

นี่คือกฎที่ทำให้ activity diagram กับ state diagram sync กันเสมอ — partition เปลี่ยนชื่อ = ต้องมี transition คู่กันใน state diagram (และกลับกัน: state diagram มี transition ระหว่าง 2 state ไหน activity diagram ที่เดินตาม flow นั้นต้องเห็น partition สลับ 2 ชื่อนั้นด้วย):

```plantuml
' ถูกต้อง — ผู้ใช้เริ่มที่ตะกร้า แล้วถูกพาไปหน้ากรอกคำขอ (ตรงกับ CartDetail --> CheckoutForm ใน state diagram)
|frontend:CartDetail|
:กดยืนยันส่งคำขอยืม;

|backend|
:ตรวจสต๊อกคงเหลืออีกครั้ง (ORM);

|frontend:CheckoutForm|
:กรอกเหตุผลการยืมและวันที่ใช้งาน;
```

```plantuml
' ผิด — คงชื่อ partition เดิมทั้งที่หน้าจอเปลี่ยนไปแล้วจริง (ตาม state diagram ต้องเป็นคนละหน้า)
|frontend:CartDetail|
:กดยืนยันส่งคำขอยืม;
:กรอกเหตุผลการยืมและวันที่ใช้งาน;   ' ผิด — ขั้นนี้เกิดที่หน้า CheckoutForm ไม่ใช่ CartDetail
```

ถ้า `backend` ทำงานหลายจุดในกระบวนการ ให้ใช้ `backend` เดิมซ้ำทุกครั้ง (PlantUML รวมเป็นคอลัมน์เดียวกันเองตราบใดที่ชื่อตรงกันทุกตัวอักษร) — เช่นเดียวกัน ถ้าผู้ใช้กลับมาหน้าเดิมซ้ำ (เช่น loop) ให้ใช้ `frontend:<PageCode>` เดิมซ้ำ ไม่สร้างชื่อใหม่

**1.3 `backend` แยกเป็น `backend:<app>` ได้เฉพาะเมื่อ flow ข้ามหลาย Django app จริง**

ค่าเริ่มต้นใช้ `backend` เปล่า ๆ พอ (หน่วยของ "ฝั่งเซิร์ฟเวอร์" ใน monolith คือทั้งโปรเจกต์ ไม่ใช่แยกตาม View/Model/Form/Service ซึ่งเป็นโครงสร้างภายในของ process เดียว) — แยกเป็น `backend:borrow`, `backend:catalog` ได้เฉพาะเมื่อกระบวนการเดียวพาดผ่านหลาย app จริงและต้องการความชัด แต่ต้องเข้าใจว่าการเรียกข้าม app ใน monolith เป็น **in-process function call** (import แล้วเรียกตรง ๆ) **ไม่ใช่ network/HTTP call** ต่างจาก microservice ที่เรียกข้าม service ผ่านเครือข่าย

**1.4 `PageCode` ที่ยังไม่มีในหน้าจอทางการ ห้ามคิดขึ้นเอง**

ถ้า flow ของ UC ที่กำลังเขียนต้องพาผู้ใช้ไปหน้าที่ยังไม่เคยนิยามใน `module_state_diagram.puml` (ของ module ตัวเองหรือ module อื่น) ให้ไป**เพิ่ม state นั้นใน state diagram ก่อน** แล้วค่อยกลับมาอ้างเป็น `frontend:<PageCode>` ในนี้ — ห้ามตั้งชื่อหน้าใหม่ลอย ๆ ใน activity diagram เพราะจะกลายเป็นหน้าที่ไม่มีอยู่จริง (orphan reference)

---

## 2. กฎเรื่องการรับ Request และการยืนยันตัวตน (แทนที่ API Gateway เดิม)

**ใน monolith ไม่มี API Gateway** — request จากเบราว์เซอร์วิ่งเข้า Django โดยตรง (ผ่าน WSGI/ASGI) ไม่ต้องวาด partition "Gateway" คั่นทุกครั้งเหมือนสถาปัตยกรรม microservice

**2.1 การยืนยันตัวตนเกิดครั้งเดียวตอนล็อกอิน ไม่ใช่ทุก request** — django-allauth ยืนยันตัวตนผ่าน UBU Single Sign-On ตอนล็อกอิน แล้วเซ็ต **session cookie** หลังจากนั้นทุก request แนบ session เอง Django middleware ผูก `request.user` ให้อัตโนมัติ ดังนั้น:
- **flow ล็อกอินเท่านั้น** ที่ต้องวาดขั้นตอนติดต่อ UBU Single Sign-On (partition ภายนอก `UBU Single Sign-On (@ubu.ac.th) (external)`) โดยเริ่มที่ `frontend:Welcome` หรือ `frontend:Login` ตามหน้าจริงใน state diagram
- **flow ทั่วไป** (ยืม/คืน/อนุมัติ) **ไม่ต้อง**วาดขั้นตอน SSO ซ้ำ — สมมติว่า login แล้ว เริ่มที่ `frontend:<PageCode>` ของหน้าแรกที่ actor ใช้ใน UC นั้นได้เลย

**2.2 การตรวจสิทธิ์ (authorization) เป็น step แรกใน `backend` ไม่ใช่ partition แยก** — เมื่อ request เข้าถึง view, Django ตรวจ `login_required` + permission/group ก่อนรัน logic แสดงเป็นกิจกรรมแรกใน partition `backend` ได้ถ้าต้องการเน้น เช่น:

```plantuml
|frontend:PendingRequests|
:กดอนุมัติคำขอ;

|backend|
:ตรวจ session + สิทธิ์ (staff เท่านั้น);
:เปลี่ยนสถานะคำขอเป็น APPROVED;
```

> ถ้า flow ไม่ได้เน้นเรื่องสิทธิ์ จะข้ามการวาด step "ตรวจสิทธิ์" ก็ได้ — เขียนเป็นหมายเหตุทั่วไปครั้งเดียวว่า "ทุก view ผ่าน login_required + permission" แทนการวาดซ้ำทุกไดอะแกรม (ดู §7 checklist)

**2.3 การเรียกบริการภายนอกจริง** (UBU Single Sign-On, SMTP, storage) วาดเป็น partition แยกเส้นขอบประ เพราะอยู่นอกขอบเขต Django — ต่างจากการเรียกข้าม app ภายใน (§1.3) ที่เป็น in-process call ไม่ต้องแยกเส้นประ

---

## 3. กฎเรื่อง Cross-cutting Concern (Audit Log / Notification)

**3.1 side effect ที่ไม่ต้องให้ผู้ใช้รอ ใช้ `fork` / `fork again` / `end fork`** — เช่น เขียน audit log หรือส่งแจ้งเตือน ที่ main flow ไม่ต้องรอให้เสร็จก่อนตอบผู้ใช้ ใน Django มักทำผ่าน **signal** (`post_save`) หรือ **async task** (Celery/django-q):

```plantuml
:บันทึกข้อมูล (write);

fork
  :ดำเนินการต่อ (main flow);
fork again
  :เขียน audit log (who/what/when) ผ่าน signal;
end fork
```

**3.2 Notification ใช้ pattern เดียวกัน** — ถ้า 1 write ต้องทั้งแจ้งเตือนและเขียน audit พร้อมกัน ใส่เป็นแตกกิ่งคู่ขนานใน fork เดียวกันได้ · การส่งอีเมลจริงวิ่งออกไปที่ SMTP (partition ภายนอก เส้นขอบประ)

**3.3 อย่าใช้ fork ถ้า side effect นั้น block การทำงานจริง** — ถ้าต้องรอผลก่อนไปต่อ (เช่น ต้องรอ `catalog` ยืนยันว่าลดจำนวนคงเหลือสำเร็จก่อนจึงอนุมัติได้) ให้วาดเป็นลำดับปกติ ไม่ใช่ fork เพราะ fork สื่อว่า "ทำพร้อมกันโดยไม่ต้องรอกัน" เท่านั้น

---

## 4. Loop / Retry Pattern

ใช้ `repeat` / `repeat while` แทนการวาดลูกศรย้อนกลับเอง เพื่อสื่อว่าต้องวนจนกว่าเงื่อนไขจะผ่าน ไม่ใช่ทำครั้งเดียวจบ — **ไม่มี Gateway ให้ผ่านทุกรอบเหมือน microservice** วนที่ `frontend:<PageCode>` ↔ `backend` ตรง ๆ (loop ที่วนอยู่หน้าเดิมใช้ `frontend:<PageCode>` เดิมซ้ำทุกรอบ ไม่เปลี่ยนชื่อ):

```plantuml
|frontend:RequestForm|
repeat
  :กรอกแบบฟอร์มคำขอยืม;
  |backend|
  :ตรวจ validation (ข้อมูลครบ/เบอร์ติดต่อมี);
repeat while (ข้อมูลผ่านครบหรือไม่?) is (ไม่ผ่าน — กรอกใหม่) not (ผ่าน)

|backend|
:บันทึกคำขอ (สถานะ PENDING);
```

`is (...)` คือ label บนเส้นที่วนกลับไปทำซ้ำ ส่วน `not (...)` คือ label บนเส้นที่ออกจาก loop — ระวังอย่าสลับสองอันนี้กัน

---

## 5. Style มาตรฐาน — Monochrome เท่านั้น

**กฎสำคัญ: ห้ามให้แต่ละ partition มีสีพื้นหลังต่างกันแบบสีรุ้ง** เพราะยิ่งฝ่ายเยอะยิ่งดูรก และสีจะสื่อความหมายซ้ำซ้อนกับ label ที่มีอยู่แล้ว — ใช้โทนเดียว (ขาว/เทา) ทั้งไดอะแกรม แล้วแยกบทบาทด้วย **เส้นขอบ** แทน:

| ชนิด partition | พื้นหลัง | เส้นขอบ |
|---|---|---|
| `frontend:<PageCode>` | ขาว (`white`) | ทึบ (`#424242`) |
| `backend` | เทาอ่อน (`#F5F5F5`) | ทึบ (`#424242`) |
| บริการภายนอก (UBU Single Sign-On (@ubu.ac.th), SMTP, storage) | เทาอ่อน (`#F5F5F5`) | **เส้นประ** (`#616161`) — สื่อว่าอยู่นอกขอบเขต Django |

```plantuml
skinparam activity {
  BackgroundColor #F5F5F5
  BorderColor #424242
  FontName "TH Sarabun New"
  FontSize 13
  DiamondBackgroundColor #FAFAFA
  DiamondBorderColor #616161
}
skinparam partition {
  BackgroundColor #FAFAFA
  BorderColor #424242
}
```

ถ้า PlantUML เวอร์ชันที่ใช้ไม่รองรับการทำเส้นประบน partition โดยตรง ให้ระบุชื่อ partition ต่อท้ายด้วย `(external)` แทนสี เช่น `|UBU Single Sign-On (@ubu.ac.th) (external)|` — สื่อความหมายด้วยข้อความ ไม่ใช่สี

**ห้ามใช้สีตระกูลต่างกัน (ส้ม/ฟ้า/เขียว/ม่วง) แยกแต่ละ partition เด็ดขาด** — ทุกอย่างอยู่ในโทนเทา-ขาวเดียวกัน แยกด้วยเส้นขอบ + label เท่านั้น

---

## 6. Audit `frontend:<PageCode>` เทียบกับ State Diagram (แทนที่งาน "(page: X)" แบบเดิม)

เพราะ partition หน้าจอเขียนเป็น `frontend:<PageCode>` โดยตรงตาม §1 การตรวจว่า activity diagram อ้างหน้าตรงกับ state diagram หรือไม่ ทำได้ทันทีด้วย 2 คำสั่ง โดยไม่ต้องมานั่งอ่านทีละบรรทัดหาคำว่า "หน้า" แบบวิธีเดิมอีกต่อไป:

```bash
# 1) orphan check — frontend:X ใน activity ที่ไม่มี X อยู่จริงใน state diagram (ต้องไม่มี output)
grep -ohE '\|frontend:[A-Za-z][A-Za-z0-9]*\|' activity/*.puml | tr -d '|' | cut -d: -f2 | sort -u | while read p; do grep -qE " as $p$" module_state_diagram.puml || echo "ORPHAN: $p"; done
```

```bash
# 2) reverse check — state ที่มีอยู่จริงแต่ไม่มี activity ไฟล์ไหนอ้างถึงเลย (ไม่ใช่ error เสมอไป — ดูหมายเหตุ)
grep -oE ' as [A-Za-z][A-Za-z0-9]*$' module_state_diagram.puml | sed 's/ as //' | sort -u | while read p; do grep -qrE "\|frontend:$p\|" activity/ || echo "ไม่มี activity อ้างถึง: $p"; done
```

ผลของคำสั่งที่ 2 ไม่ถือเป็น error เสมอไป — หน้าที่เป็นแค่การแสดงข้อมูลอาจไม่มีขั้นตอนใน activity diagram ที่ต้องพูดถึงมัน แต่ถ้าเป็นหน้าที่ควรมี flow (`Form`, `Confirm`) แล้วไม่มีใครอ้าง ให้กลับไปตรวจว่า activity diagram ของ UC นั้นยังตกหล่นอยู่หรือเปล่า

---

## 7. Checklist ก่อนส่งไดอะแกรม

- [ ] ทุก partition เป็น `frontend:<PageCode>` / `backend` / บริการภายนอกจริง — ไม่มี partition ชื่อ actor เฉย ๆ (`นักศึกษา`, `เจ้าหน้าที่`) และไม่ใช่ 1 view/1 URL (ข้อ 1.1)
- [ ] ทุก `<PageCode>` ใน `frontend:<PageCode>` ตรงกับชื่อหลัง `as` ใน `module_state_diagram.puml` แบบตัวอักษรต่อตัวอักษร — ไม่มีหน้าที่คิดขึ้นเองลอย ๆ (ข้อ 1.4)
- [ ] ทุกจุดที่ partition เปลี่ยนจาก `frontend:A` เป็น `frontend:B` กลางกระบวนการ ต้องมี transition `A --> B` คู่กันใน state diagram (ข้อ 1.2)
- [ ] ค่าเริ่มต้นใช้ `backend` เปล่า ๆ พอ · แยกเป็น `backend:<app>` เฉพาะเมื่อ flow ข้ามหลาย Django app จริง และเข้าใจว่าเป็น in-process call (ข้อ 1.3)
- [ ] หน้าเดิม/backend เดิมที่ทำงานซ้ำ ใช้ชื่อ partition เดิมทุกครั้ง ไม่สร้างซ้ำ
- [ ] **ไม่มี partition "API Gateway" และไม่มีขั้นตอน "ตรวจ JWT" ทุก request** — auth เกิดตอน login ผ่าน UBU SSO (session) เท่านั้น (ข้อ 2)
- [ ] flow ล็อกอินเท่านั้นที่วาดขั้นตอน UBU Single Sign-On (external) เริ่มที่ `frontend:Welcome`/`frontend:Login` · flow อื่นเริ่มที่ `frontend:<PageCode>` ของหน้าแรกใน UC นั้นได้เลย
- [ ] บริการภายนอกจริง (SSO/SMTP/storage) เป็น partition เส้นขอบประ · การเรียกข้าม app ภายในไม่ใช่เส้นประ
- [ ] Write operation สำคัญที่ไม่ต้องรอ มีเส้นไป Audit Log/Notification แบบ `fork`/`end fork` (ผ่าน signal/async)
- [ ] Loop ใช้ `repeat`/`repeat while` ไม่ใช่ลูกศรย้อนกลับเอง และ label `is`/`not` ไม่สลับกัน
- [ ] **ทั้งไดอะแกรมใช้โทนเดียว (ขาว/เทา)** — แยก `frontend`/`backend` ด้วยเส้นขอบทึบ/ประ + ข้อความเท่านั้น
- [ ] รันคำสั่ง audit ใน §6 แล้วไม่มี output ผิดปกติ (ไม่มี `frontend:*` ที่อ้างหน้าซึ่งไม่มีจริงใน state diagram)
