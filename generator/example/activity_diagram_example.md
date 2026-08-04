# ตัวอย่าง — Activity Diagram ที่ทำตามกฎครบทุกข้อ (Monolith)

> ตัวอย่างนี้ใช้ระบบสมมติ **"ระบบสั่งซื้อสินค้าออนไลน์"** (Django MVT monolith) เพื่อสาธิตกฎทั้งหมดใน [`activity_diagram_generate_guide.md`](../guide/activity_diagram_generate_guide.md) — เป็น**ระบบเดียวกับ** [`ui_state_diagram_example.md`](ui_state_diagram_example.md) โดยตั้งใจ เพื่อให้เห็นว่า partition ในไฟล์นี้ (`frontend:CartDetail`, `frontend:CheckoutForm`, `frontend:CustOrderList`) ต้องตรงกับชื่อ state ในไดอะแกรมนั้นทุกตัวอักษร

จุดที่ตัวอย่างนี้สาธิตให้เห็น:
- **partition หน้าจอเป็น `frontend:<PageCode>` เสมอ** — ไม่ใช่ชื่อ actor (`Customer`) ลอย ๆ แบบเดิม และทุก `PageCode` (`CartDetail`, `CheckoutForm`, `CustOrderList`) มีอยู่จริงใน `module_state_diagram_order.puml` ของ [`ui_state_diagram_example.md`](ui_state_diagram_example.md)
- **partition เปลี่ยนตามหน้าจอที่เปลี่ยนจริง** — ลูกค้าเริ่มที่ `frontend:CartDetail` แล้วถูกพาไปหน้า `frontend:CheckoutForm` ตรงกับ transition `CartDetail --> CheckoutForm` ในไดอะแกรม state · เมื่อสต๊อกไม่พอ กระบวนการพากลับไป `frontend:CartDetail` ตรงกับ transition ขาล้มเหลว `CheckoutForm --> CartDetail`
- **`backend` เดี่ยว ๆ แทนชื่อโปรเจกต์** — ไม่มี partition ชื่อ "ระบบร้านค้าออนไลน์" อีกต่อไป ใช้ `backend` คงที่ตลอดไฟล์
- **บริการภายนอกจริงเป็น partition เส้นขอบประ** — `Payment Gateway (external)` และ `เซิร์ฟเวอร์อีเมล (external)` อยู่นอกโปรเจกต์ Django
- **Loop ด้วย `repeat`/`repeat while` วนที่ `frontend:CheckoutForm` เดิม** — ชำระเงินไม่สำเร็จ วนกลับให้ลูกค้าลองใหม่บนหน้าเดิม ไม่เปลี่ยนชื่อ partition
- **Audit log + อีเมลแบบ non-blocking ด้วย `fork`/`end fork`** — ผ่าน Django signal / async task ไม่บล็อกการตอบลูกค้า
- **Monochrome ล้วน** — แยก `frontend`/`backend`/external ด้วยข้อความ ไม่ใช่สี

---

## เตรียมข้อมูลก่อนกรอก template

| ขั้นที่ | ใครทำ | เกิดที่หน้าไหน (`PageCode`) | กิจกรรม |
|---|---|---|---|
| 1 | ลูกค้า | `CartDetail` | กดสั่งซื้อสินค้าในตะกร้า |
| 2 | backend | — | ตรวจสิทธิ์ + สร้างคำสั่งซื้อ (pending) |
| 3 | ลูกค้า | `CheckoutForm` | กรอกที่อยู่/วิธีชำระเงิน แล้วกดยืนยัน |
| 4 | backend | — | ตรวจสต๊อก + เรียกชำระเงิน |
| 5a | ลูกค้า | `CartDetail` *(สต๊อกไม่พอ — ย้อนกลับ)* | เห็นข้อความยกเลิกคำสั่งซื้อ |
| 5b | ลูกค้า/Payment Gateway | `CheckoutForm` *(loop จนกว่าจะสำเร็จ)* | ชำระเงิน |
| 6 | backend | — | ยืนยันคำสั่งซื้อ + ตัดสต๊อก (write) |
| 7 | ลูกค้า | `CustOrderList` | เห็นคำสั่งซื้อในประวัติพร้อมสถานะ "ยืนยันแล้ว" |

---

```plantuml
@startuml order_activity_checkout
' ══════════════════════════════════════════════════════════════════
' รองรับภาษาไทย — อ่านก่อน render:
' 1. บันทึกไฟล์นี้เป็น UTF-8 (ไม่ต้องมี BOM) เสมอ
' 2. ถ้า render ผ่าน CLI (plantuml.jar) ต้องระบุ flag encoding ด้วย:
'      java -Dfile.encoding=UTF-8 -jar plantuml.jar -charset UTF-8 order_activity_checkout.puml
' 3. บังคับใช้ Smetana (pure-Java layout engine) แทน Graphviz/dot
'    เพราะ Graphviz บางระบบ (โดยเฉพาะ Windows) อ่าน UTF-8 ไม่ตรง ทำให้ตัวอักษรไทยเพี้ยน/หาย
!pragma layout smetana
' 4. ฟอนต์ที่มีสระ/วรรณยุกต์ไทยครบและ render ผ่าน Java ได้เสถียร
'    - Windows: "TH Sarabun New" (ฟอนต์มาตรฐานราชการ) หรือ "Tahoma" (มากับเครื่องอยู่แล้ว)
'    - Linux / PlantUML online server: เปลี่ยนเป็น "Noto Sans Thai" หรือ "Loma"
skinparam defaultFontName "TH Sarabun New"
skinparam defaultFontSize 14
' ══════════════════════════════════════════════════════════════════

!theme plain
skinparam titleFontName "TH Sarabun New"
skinparam titleFontSize 20
skinparam noteFontName "TH Sarabun New"
skinparam ArrowFontName "TH Sarabun New"
skinparam ArrowFontSize 12
skinparam swimlaneTitleFontName "TH Sarabun New"
skinparam swimlaneTitleFontSize 14

' ===== Monochrome เท่านั้น — ไม่มี partition ไหนสีต่างจากที่อื่น =====
skinparam activity {
  BackgroundColor #F5F5F5
  BorderColor #424242
  FontName "TH Sarabun New"
  FontSize 13
  DiamondBackgroundColor #FAFAFA
  DiamondBorderColor #616161
}

title สั่งซื้อสินค้าออนไลน์ (Checkout) — Activity Diagram\npartition หน้าจอ = frontend:PageCode (ตรงกับ module_state_diagram_order.puml) · ฝั่งเซิร์ฟเวอร์ = backend

|frontend:CartDetail|
start
' สมมติ login แล้ว (session) — ไม่ต้องวาด OAuth/SSO ซ้ำใน flow นี้
:กดสั่งซื้อสินค้าในตะกร้า;

|backend|
:ตรวจ session + สิทธิ์ (ลูกค้าที่ล็อกอิน);
:สร้างคำสั่งซื้อ (สถานะ pending);

|frontend:CheckoutForm|
:กรอกที่อยู่จัดส่งและเลือกวิธีชำระเงิน;
:กดยืนยันชำระเงิน;

|backend|
:ตรวจสอบสต๊อกสินค้าอีกครั้ง (ORM);
if (สต๊อกเพียงพอหรือไม่?) then (ไม่พอ)
  :ยกเลิกคำสั่งซื้อ (pending);
  |frontend:CartDetail|
  :เห็นข้อความแจ้งยกเลิก กลับสู่ตะกร้า;
  stop
else (พอ)
endif
:เรียกชำระเงิน;

|frontend:CheckoutForm|
repeat
  |Payment Gateway (external)|
  :ประมวลผลการชำระเงิน;
repeat while (ชำระเงินสำเร็จหรือไม่?) is (ไม่สำเร็จ — ลูกค้าลองใหม่บนหน้าเดิม) not (สำเร็จ)

|backend|
:ยืนยันคำสั่งซื้อ + ตัดสต๊อก (write);

fork
  |frontend:CustOrderList|
  :เห็นคำสั่งซื้อสถานะ "ยืนยันแล้ว" ในประวัติ (main flow);
fork again
  :เขียน audit log (ยืนยันคำสั่งซื้อ) ผ่าน signal;
fork again
  |เซิร์ฟเวอร์อีเมล (external)|
  :ส่งอีเมลใบเสร็จให้ลูกค้า;
end fork

stop

legend right
  |<back:white>    </back>| frontend:PageCode — หน้าจอที่ผู้ใช้เห็น (ตรงกับ module_state_diagram_order.puml) |
  |<back:#F5F5F5>    </back>| backend (Django monolith) — เส้นขอบทึบ |
  |<back:#F5F5F5>    </back>| บริการภายนอก (Payment Gateway, อีเมล) — สื่อด้วยข้อความ "(external)" ไม่ใช่สี |
  หมายเหตุ: สร้างคำสั่งซื้อ + ตรวจสต๊อก + ตัดสต๊อก เป็น in-process logic ใน backend เดียวกัน ไม่ใช่การเรียกข้าม service
endlegend

@enduml
```

---

## ตรวจก่อนส่ง

ต้องไม่มี output ทั้งคู่ — ยืนยันว่าทุก `frontend:PageCode` ในไฟล์นี้มีอยู่จริงใน state diagram และไม่มีหน้าไหนถูกคิดขึ้นเองลอย ๆ:

```bash
grep -ohE '\|frontend:[A-Za-z][A-Za-z0-9]*\|' order_activity_checkout.puml | tr -d '|' | cut -d: -f2 | sort -u | while read p; do grep -qE " as $p$" module_state_diagram_order.puml || echo "ORPHAN: $p"; done
```

ผลตรวจ: `CartDetail`, `CheckoutForm`, `CustOrderList` — ทั้ง 3 ชื่อมีอยู่จริงใน [`ui_state_diagram_example.md`](ui_state_diagram_example.md) → ไม่มี output → ผ่าน
