# คู่มือการวาด Activity Diagram แบบมี Swimlane (Activity Diagram Generation Guide)

> ใช้คู่กับ [`activity_diagram_template.md`](../template/activity_diagram_template.md) เป็นจุดเริ่มก๊อปปี้ และดู [`activity_diagram_example.md`](../example/activity_diagram_example.md) เป็นตัวอย่างที่ทำตามกฎครบทุกข้อ
>
> **สถาปัตยกรรมเป้าหมาย: Django MVT monolith** — business logic ทั้งหมดอยู่ในโปรเจกต์เดียว (ไม่มี microservice/API Gateway/JWT) ยืนยันตัวตนด้วย django-allauth ผ่าน Google OAuth (session) กฎด้านล่างสะท้อนความจริงของ monolith ไม่ใช่คลัสเตอร์ service

---

## 0. นิยาม: Activity Diagram ต่างจาก Use Case Diagram อย่างไร (อ่านก่อนเริ่ม)

**Use case diagram** ([`usecase_generate_guide.md`](usecase_generate_guide.md)) ตอบคำถาม "ผู้ใช้ทำอะไรได้บ้าง" ในระดับเป้าหมาย (goal-level) — ห้ามลงรายละเอียดขั้นตอนภายใน

**Activity diagram** (ไฟล์นี้) ตอบคำถามตรงข้าม — "1 use case นั้นทำงานเป็นขั้นตอนอย่างไรจริง ๆ" รวมถึง**ใครทำอะไร ที่ layer/แอปไหน และเรียกระบบภายนอกตัวใดบ้าง** จึงเป็นที่ที่ business rule, decision, loop, และการติดต่อระบบภายนอกที่ถูกห้ามไม่ให้ใส่ใน use case diagram ควรมาอยู่แทน

ใช้ activity diagram แบบมี swimlane เมื่อ:
- ต้องการอธิบาย 1 use case ที่มีขั้นตอนข้ามหลายฝ่าย (ผู้ใช้ ↔ ระบบ ↔ บริการภายนอก)
- ต้องการโชว์กรรมการสอบว่า "ใครทำอะไร ที่ไหน" ในกระบวนการเดียว
- ต้องการเห็น decision/loop ที่ use case diagram บอกไม่ได้ (เช่น ต้องวนกรอกใหม่จนผ่าน validation)

---

## 1. กฎเรื่อง Partition (Swimlane) — สำหรับ Monolith

**1.1 หนึ่ง partition แทนหนึ่ง "ผู้รับผิดชอบขั้นตอน" — ไม่ใช่หนึ่ง view/หนึ่ง URL**

Partition คือ "ใครเป็นเจ้าของ logic ตรงนี้" ในบริบท monolith มี 3 ชนิดเท่านั้น:
- **Actor ภายนอกที่เป็นมนุษย์** (นักศึกษา, เจ้าหน้าที่, ผู้ดูแลระบบ) — ผู้ริเริ่มการกระทำ
- **ระบบ (Django application)** — โค้ดฝั่ง server ที่ประมวลผล (view + model + business logic) ทั้งหมดของโปรเจกต์
- **บริการภายนอกจริง** ที่อยู่นอกโปรเจกต์ Django (เช่น Google OAuth, เซิร์ฟเวอร์อีเมล/SMTP, ที่เก็บไฟล์ภายนอก) — เส้นขอบประ (ดู §5)

ถ้าระบบทำงานหลายจุดในกระบวนการ ให้ใช้ชื่อ partition เดิมซ้ำทุกครั้ง — PlantUML รวมเป็นคอลัมน์เดียวกันเองตราบใดที่ชื่อ (และสี) ตรงกันทุกตัวอักษร

```plantuml
' ถูกต้อง — ระบบทำงานกี่ครั้งก็ใช้ partition เดิม
|ระบบ UBORROWU|
:สร้างคำขอยืม (สถานะ PENDING);
...
|ระบบ UBORROWU|
:อัปเดตสถานะเป็น ACTIVE;
```

```plantuml
' ผิด — ห้ามแยก partition ตาม view/URL ของระบบเดียวกัน
|POST /borrow/create|
:สร้างคำขอ;
|POST /borrow/approve|
:อนุมัติ;
```

**1.2 หน่วยของ "ระบบ" ใน monolith คือทั้งโปรเจกต์ Django — layer ภายในไม่ใช่ partition แยก** (View/Model/Form/Service ไม่ใช่ partition แยกกัน เพราะเป็นโครงสร้างภายในของ process เดียว) ค่าเริ่มต้นจึงใช้ partition ระบบตัวเดียว เช่น `|ระบบ UBORROWU|`

> **ข้อยกเว้น — แยก partition ตาม Django app ได้เมื่อ flow ข้ามหลาย app จริง:** ถ้ากระบวนการเดียวพาดผ่านหลาย app (เช่น `borrow` เรียกใช้ `catalog` เพื่อลดจำนวนคงเหลือ แล้วเรียก `notifications`) จะแยกเป็น `|borrow|`, `|catalog|` เพื่อความชัดได้ — แต่ต้องเข้าใจว่าการเรียกข้าม app ใน monolith เป็น **in-process function call** (import แล้วเรียกตรง ๆ) **ไม่ใช่ network/HTTP call** ต่างจาก microservice ที่เรียกข้าม service ผ่านเครือข่าย ถ้า flow อยู่ app เดียวไม่ต้องแยก — ใช้ partition ระบบตัวเดียวพอ

**1.3 Actor ที่เป็นมนุษย์ก็นับเป็น partition** — ใช้หลักเดียวกับ actor ใน use case diagram (ดูข้อ 1.1 ของ [`usecase_generate_guide.md`](usecase_generate_guide.md)): ต้องเป็นสิ่งภายนอกที่ริเริ่มการกระทำจริง ไม่สร้าง partition ชื่อ "System" ลอย ๆ (ใช้ชื่อระบบจริงเช่น "ระบบ UBORROWU" แทน)

---

## 2. กฎเรื่องการรับ Request และการยืนยันตัวตน (แทนที่ API Gateway เดิม)

**ใน monolith ไม่มี API Gateway** — request จากเบราว์เซอร์วิ่งเข้า Django โดยตรง (ผ่าน WSGI/ASGI) ไม่ต้องวาด partition "Gateway" คั่นทุกครั้งเหมือนสถาปัตยกรรม microservice

**2.1 การยืนยันตัวตนเกิดครั้งเดียวตอนล็อกอิน ไม่ใช่ทุก request** — django-allauth ทำ OAuth กับ Google ตอนล็อกอิน แล้วเซ็ต **session cookie** หลังจากนั้นทุก request แนบ session เอง Django middleware ผูก `request.user` ให้อัตโนมัติ ดังนั้น:
- **flow ล็อกอิน** เท่านั้นที่ต้องวาดขั้นตอนติดต่อ Google OAuth (partition ภายนอก "Google OAuth (allauth)") + ตรวจ Whitelist
- **flow ทั่วไป** (ยืม/คืน/อนุมัติ) **ไม่ต้อง**วาดขั้นตอน OAuth ซ้ำ — สมมติว่า login แล้ว ให้เริ่มที่ actor กระทำได้เลย

**2.2 การตรวจสิทธิ์ (authorization) เป็น step แรกในฝั่งระบบ ไม่ใช่ partition แยก** — เมื่อ request เข้าถึง view, Django ตรวจ `login_required` + permission/group ก่อนรัน logic แสดงเป็นกิจกรรมแรกใน partition ระบบได้ถ้าต้องการเน้น เช่น:

```plantuml
|เจ้าหน้าที่|
:กดอนุมัติคำขอ;

|ระบบ UBORROWU|
:ตรวจ session + สิทธิ์ (staff เท่านั้น);
:เปลี่ยนสถานะคำขอเป็น APPROVED;
```

> ถ้า flow ไม่ได้เน้นเรื่องสิทธิ์ จะข้ามการวาด step "ตรวจสิทธิ์" ก็ได้ — เขียนเป็นหมายเหตุทั่วไปครั้งเดียวว่า "ทุก view ผ่าน login_required + permission" แทนการวาดซ้ำทุกไดอะแกรม (ดู §7 checklist)

**2.3 การเรียกบริการภายนอกจริง** (Google OAuth, SMTP, storage) วาดเป็น partition แยกเส้นขอบประ เพราะอยู่นอกขอบเขต Django — ต่างจากการเรียกข้าม app ภายใน (§1.2) ที่เป็น in-process call ไม่ต้องแยกเส้นประ

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

ใช้ `repeat` / `repeat while` แทนการวาดลูกศรย้อนกลับเอง เพื่อสื่อว่าต้องวนจนกว่าเงื่อนไขจะผ่าน ไม่ใช่ทำครั้งเดียวจบ — **ไม่มี Gateway ให้ผ่านทุกรอบเหมือน microservice** วนที่ actor ↔ ระบบ ตรง ๆ:

```plantuml
|นักศึกษา|
repeat
  :กรอกแบบฟอร์มคำขอยืม;
  |ระบบ UBORROWU|
  :ตรวจ validation (ข้อมูลครบ/เบอร์ติดต่อมี);
repeat while (ข้อมูลผ่านครบหรือไม่?) is (ไม่ผ่าน — กรอกใหม่) not (ผ่าน)

|ระบบ UBORROWU|
:บันทึกคำขอ (สถานะ PENDING);
```

`is (...)` คือ label บนเส้นที่วนกลับไปทำซ้ำ ส่วน `not (...)` คือ label บนเส้นที่ออกจาก loop — ระวังอย่าสลับสองอันนี้กัน

---

## 5. Style มาตรฐาน — Monochrome เท่านั้น

**กฎสำคัญ: ห้ามให้แต่ละ partition มีสีพื้นหลังต่างกันแบบสีรุ้ง** เพราะยิ่งฝ่ายเยอะยิ่งดูรก และสีจะสื่อความหมายซ้ำซ้อนกับ label ที่มีอยู่แล้ว — ใช้โทนเดียว (ขาว/เทา) ทั้งไดอะแกรม แล้วแยกบทบาทด้วย **เส้นขอบ** แทน:

| บทบาท | พื้นหลัง | เส้นขอบ |
|---|---|---|
| Actor ภายนอก (human) | ขาว (`white`) | ทึบ (`#424242`) |
| ระบบ (Django application) | เทาอ่อน (`#F5F5F5`) | ทึบ (`#424242`) |
| บริการภายนอก (Google OAuth, SMTP, storage) | เทาอ่อน (`#F5F5F5`) | **เส้นประ** (`#616161`) — สื่อว่าอยู่นอกขอบเขต Django |

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

ถ้า PlantUML เวอร์ชันที่ใช้ไม่รองรับการทำเส้นประบน partition โดยตรง ให้ระบุชื่อ partition ต่อท้ายด้วย `(external)` แทนสี เช่น `|Google OAuth (external)|` — สื่อความหมายด้วยข้อความ ไม่ใช่สี

**ห้ามใช้สีตระกูลต่างกัน (ส้ม/ฟ้า/เขียว/ม่วง) แยกแต่ละ partition เด็ดขาด** — ทุกอย่างอยู่ในโทนเทา-ขาวเดียวกัน แยกด้วยเส้นขอบ + label เท่านั้น

---

## 6. Checklist ก่อนส่งไดอะแกรม

- [ ] ทุก partition เป็น actor มนุษย์ / ระบบ Django / บริการภายนอกจริง — ไม่ใช่ 1 view/1 URL (ข้อ 1.1)
- [ ] ค่าเริ่มต้นใช้ partition ระบบตัวเดียว (`ระบบ <ชื่อ>`) · แยกตาม Django app เฉพาะเมื่อ flow ข้ามหลาย app จริง และเข้าใจว่าเป็น in-process call (ข้อ 1.2)
- [ ] ระบบเดียวกัน/app เดียวกันที่ทำงานซ้ำ ใช้ชื่อ partition เดิมทุกครั้ง ไม่สร้างซ้ำ
- [ ] **ไม่มี partition "API Gateway" และไม่มีขั้นตอน "ตรวจ JWT" ทุก request** — auth เกิดตอน login ผ่าน allauth/Google (session) เท่านั้น (ข้อ 2)
- [ ] flow ล็อกอินเท่านั้นที่วาดขั้นตอน Google OAuth (external) + Whitelist · flow อื่นเริ่มที่ actor ได้เลย
- [ ] บริการภายนอกจริง (OAuth/SMTP/storage) เป็น partition เส้นขอบประ · การเรียกข้าม app ภายในไม่ใช่เส้นประ
- [ ] Write operation สำคัญที่ไม่ต้องรอ มีเส้นไป Audit Log/Notification แบบ `fork`/`end fork` (ผ่าน signal/async)
- [ ] Loop ใช้ `repeat`/`repeat while` ไม่ใช่ลูกศรย้อนกลับเอง และ label `is`/`not` ไม่สลับกัน
- [ ] **ทั้งไดอะแกรมใช้โทนเดียว (ขาว/เทา)** — แยกบทบาทด้วยเส้นขอบทึบ/ประ + ข้อความเท่านั้น
- [ ] ไม่มี partition ชื่อ "ระบบ"/"System" ลอย ๆ (ใช้ชื่อระบบจริง)
