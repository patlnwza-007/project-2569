# ตัวอย่าง — Use Case Diagram ที่ทำตามกฎครบทุกข้อ

> ตัวอย่างนี้ใช้ระบบสมมติ **"ระบบยืม-คืนหนังสือห้องสมุด"** เพื่อสาธิตกฎทั้งหมดใน [`usecase_generate_guide.md`](../guide/usecase_generate_guide.md) — ไม่ผูกกับโครงงานใดโครงงานหนึ่งโดยเฉพาะ ใช้เป็นตัวอย่างอ้างอิงได้กับทุกโปรเจกต์

จุดที่ตัวอย่างนี้สาธิตให้เห็น:
- **ไม่มี actor "ระบบ"** — พฤติกรรมอัตโนมัติ (คิดค่าปรับ, แจ้งเตือนใกล้ครบกำหนด) ผูกเข้ากับ use case ของ Member ผ่าน `<<include>>`/`<<extend>>` แทน
- **เส้น actor–use case เป็นเส้นธรรมดา** (`--`) ไม่ใช้ลูกศร
- **ทิศทาง `<<include>>`/`<<extend>>` ถูกต้อง** ตามกฎข้อ 2 ของไกด์
- **จัดกลุ่มด้วย package** และมีทั้งฉบับละเอียด + ฉบับภาพรวม (Top View)
- **ไม่มี note** ในทั้งสองไดอะแกรม

---

## ฉบับละเอียด

```plantuml
@startuml library_usecase
!theme plain
skinparam defaultFontName TH Sarabun New
skinparam defaultFontSize 14
skinparam roundcorner 10

skinparam usecase {
  BackgroundColor #FFFDE7
  BorderColor #795548
}
skinparam actor {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
}
skinparam package {
  BackgroundColor #F5F5F5
  BorderColor #757575
  FontStyle bold
}
skinparam rectangle {
  BackgroundColor #FCFCFC
  BorderColor #9E9E9E
}
skinparam ArrowColor #424242

title <b>ระบบยืม-คืนหนังสือห้องสมุด</b>\n(Use Case Diagram — อ้างอิง Use Case Specification UC-01 ถึง UC-08)

left to right direction

actor "สมาชิกห้องสมุด\n(Member)" as Member
actor "บรรณารักษ์\n(Librarian)" as Librarian

rectangle "ระบบยืม-คืนหนังสือห้องสมุด" {

  ' ===== การยืม-คืน =====
  package "การยืม-คืนหนังสือ" {
    usecase "UC-01\nค้นหาหนังสือ" as UC01
    usecase "UC-02\nยืมหนังสือ" as UC02
    usecase "UC-03\nคืนหนังสือ" as UC03
    usecase "UC-04\nคำนวณค่าปรับ\n(เกินกำหนดคืน)" as UC04
    usecase "UC-05\nต่ออายุการยืม" as UC05
  }

  ' ===== การจัดการของบรรณารักษ์ =====
  package "การจัดการของบรรณารักษ์" {
    usecase "UC-06\nเพิ่ม/แก้ไขข้อมูลหนังสือ" as UC06
    usecase "UC-07\nจัดการบัญชีสมาชิก" as UC07
  }

  ' ===== แจ้งเตือน =====
  package "การแจ้งเตือน" {
    usecase "UC-08\nแจ้งเตือนใกล้ครบกำหนดคืน" as UC08
  }
}

' ===== ความสัมพันธ์ actor–use case (เส้นธรรมดา) =====
Member -- UC01
Member -- UC02
Member -- UC05
Librarian -- UC03
Librarian -- UC06
Librarian -- UC07

' ===== ความสัมพันธ์ use case–use case =====
UC01 ..> UC02 : <<include>>
UC03 ..> UC04 : <<include>>
UC02 ..> UC08 : <<include>>
UC05 ..> UC04 : <<extend>>\nมีค่าปรับค้างอยู่

@enduml
```

**อธิบายจุดที่มักผิด (เทียบกับ diagram ผิดแบบเดิม):**
- UC-04 (คำนวณค่าปรับ) และ UC-08 (แจ้งเตือน) เป็นพฤติกรรมอัตโนมัติที่ **ไม่มี actor ริเริ่มตรง ๆ** — ถ้าทำผิดจะไปสร้าง `actor "System"` แล้วลาก `System --> UC04` และ `System --> UC08` ซึ่งผิดหลัก UML ในตัวอย่างนี้จึงผูก UC-04 เข้ากับ UC-03 (คืนหนังสือ, `<<include>>` เพราะคำนวณทุกครั้งที่คืน) และ UC-05 (`<<extend>>` เพราะเกิดเฉพาะกรณีมีค่าปรับค้าง) ส่วน UC-08 ผูกกับ UC-02 (`<<include>>` เพราะยืมแล้วต้องตั้งการแจ้งเตือนเสมอ)

---

## ฉบับภาพรวม (Top View)

```plantuml
@startuml library_usecase_overview
!theme plain
skinparam defaultFontName TH Sarabun New
skinparam defaultFontSize 14
skinparam roundcorner 10

skinparam usecase {
  BackgroundColor #FFFDE7
  BorderColor #795548
}
skinparam actor {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
}
skinparam rectangle {
  BackgroundColor #FCFCFC
  BorderColor #9E9E9E
}
skinparam ArrowColor #424242

title <b>ระบบยืม-คืนหนังสือห้องสมุด</b>\n(Use Case Diagram — ภาพรวมระดับสูง / Top View)

left to right direction

actor "สมาชิกห้องสมุด\n(Member)" as Member
actor "บรรณารักษ์\n(Librarian)" as Librarian

rectangle "ระบบยืม-คืนหนังสือห้องสมุด" {
  usecase "ยืม-คืนหนังสือ\n(รวมค่าปรับ/แจ้งเตือน)" as UCA
  usecase "จัดการของบรรณารักษ์" as UCB
}

Member -- UCA
Librarian -- UCA
Librarian -- UCB

@enduml
```

ฉบับภาพรวมยุบ UC-01 ถึง UC-08 (ยกเว้น UC-06, UC-07 ที่แยกไปกลุ่มบรรณารักษ์) เหลือ use case ตัวแทนกลุ่มเดียว — ใช้เปิดพรีเซนต์แล้วสลับไปฉบับละเอียดถ้ากรรมการถามลึกกว่านั้น
