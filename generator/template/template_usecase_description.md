# Template — Use Case Description

> วิธีใช้: คัดลอกไฟล์นี้ไปที่ `<ชื่อโฟลเดอร์ module>/usecase_description.md` (เช่น `m9/usecase_description.md`)
> แทนที่ `{{...}}` ด้วยข้อมูลจริง โดย 1 use case ในนี้ต้องตรงกับ 1 use case ใน `<module>/usecase.puml`
> จัดกลุ่มตาม Epic เดียวกับที่แบ่งไว้ใน `fn req/<module>.md` และ `usecase.puml`

---

## {{M_CODE}} · {{MODULE_NAME_TH}} — Use Case Description

### {{E1}} · {{ชื่อ Epic}}

#### UC-{{01}} · {{ชื่อ Use Case}}

| หัวข้อ | รายละเอียด |
|-------|-----------|
| **รหัสอ้างอิง** | {{FN-XXX-001}} |
| **Actor หลัก** | {{ชื่อ actor ที่ลงมือทำ}} |
| **Actor รอง** | {{module/ระบบภายนอกที่ถูกเรียก ถ้ามี — ใส่ "-" ถ้าไม่มี}} |
| **คำอธิบายโดยย่อ** | {{อธิบาย 1-2 ประโยคว่า use case นี้ทำอะไร เพื่ออะไร}} |
| **เงื่อนไขก่อนเริ่มทำงาน (Pre-condition)** | {{สิ่งที่ต้องเป็นจริงก่อน use case นี้เริ่มได้ เช่น ต้อง login แล้ว, ข้อมูลอ้างอิงต้องมีอยู่ก่อน}} |
| **ลำดับเหตุการณ์หลัก (Basic Flow)** | 1. {{ขั้นตอนที่ 1}}<br>2. {{ขั้นตอนที่ 2}}<br>3. {{ขั้นตอนที่ 3}} |
| **ลำดับเหตุการณ์ทางเลือก (Alternative/Exception Flow)** | {{กรณีที่ไม่เป็นไปตามทางหลัก เช่น ข้อมูลไม่ครบ, validation ไม่ผ่าน, ระบบภายนอกไม่ตอบสนอง}} |
| **เงื่อนไขหลังทำงานสำเร็จ (Post-condition)** | {{สถานะของระบบ/ข้อมูลหลังทำสำเร็จ เช่น สถานะเปลี่ยนเป็น X, มี event ถูกส่งออก}} |
| **ความสัมพันธ์กับ Use Case อื่น** | {{<<include>> ของ UC ใด / <<extend>> จาก UC ใด — อ้างอิงจาก usecase.puml}} |
| **URL/View + สิ่งที่ต้องพึ่งพา** | {{URL name + view ของ use case นี้ (เช่น `borrow:request_create` → `RequestCreateView`) + ถ้าเรียกใช้ app อื่นภายในโปรเจกต์ ระบุเป็น in-process call (เช่น อ่าน/แก้ model ของ `catalog`) + ถ้าเรียกบริการภายนอกจริง ระบุ (Google OAuth, ส่งอีเมล SMTP, สร้าง QR) — ใส่ "-" ถ้าไม่มี dependency}} |

---

> ทำซ้ำ 1 บล็อกด้านบนต่อ 1 use case จนครบทุกตัวใน `usecase.puml` — เรียงตาม Epic เดิม อย่าข้าม use case ใดแม้จะดูเล็กน้อย เพราะต้องสอดคล้อง 1:1 กับ diagram
>
> **หมายเหตุ:** อย่าใส่การตรวจสอบสิทธิ์ (`login_required`/permission ผ่าน django-allauth) ซ้ำในทุกแถว "URL/View + สิ่งที่ต้องพึ่งพา" — ให้เขียนเป็นหมายเหตุทั่วไปครั้งเดียวไว้บนสุดของเอกสารแทน เพราะเป็น cross-cutting concern ที่ทุก use case มีเหมือนกัน (auth หลักเกิดตอน login ผ่าน Google OAuth + Whitelist)
