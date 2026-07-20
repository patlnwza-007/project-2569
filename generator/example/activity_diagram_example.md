# ตัวอย่าง — Activity Diagram ที่ทำตามกฎครบทุกข้อ (Monolith)

> ตัวอย่างนี้ใช้ระบบสมมติ **"ระบบสั่งซื้อสินค้าออนไลน์"** (Django MVT monolith) เพื่อสาธิตกฎทั้งหมดใน [`activity_diagram_generate_guide.md`](../guide/activity_diagram_generate_guide.md) — ไม่ผูกกับโครงงานใดโครงงานหนึ่งโดยเฉพาะ ใช้เป็นตัวอย่างอ้างอิงได้กับทุกโปรเจกต์

จุดที่ตัวอย่างนี้สาธิตให้เห็น:
- **partition ระบบตัวเดียว** — `ระบบร้านค้าออนไลน์` ทำทั้งสร้างคำสั่งซื้อ + ตรวจสต๊อก + ยืนยันคำสั่งซื้อ (logic ทั้งหมดอยู่ใน process เดียว ไม่แยกตาม endpoint และไม่แยกเป็น service ย่อย)
- **ไม่มี API Gateway / ไม่มีตรวจ JWT ทุก request** — สมมติผู้ใช้ล็อกอินแล้ว (session ผ่าน allauth) flow เริ่มที่ actor ได้เลย · การตรวจสิทธิ์เป็น step แรกในฝั่งระบบ ไม่ใช่ partition แยก
- **บริการภายนอกจริงเป็น partition เส้นขอบประ** — `Payment Gateway` และ `เซิร์ฟเวอร์อีเมล` อยู่นอกโปรเจกต์ Django จึงกำกับ `(external)`
- **Loop ด้วย `repeat`/`repeat while`** — ชำระเงินไม่สำเร็จ วนกลับให้ลูกค้าลองใหม่ (ไม่มี Gateway ให้ผ่านทุกรอบ)
- **Audit log + อีเมลแบบ non-blocking ด้วย `fork`/`end fork`** — ผ่าน Django signal / async task ไม่บล็อกการตอบลูกค้า
- **Monochrome ล้วน** — แยกบทบาทด้วยข้อความ `(external)` แทนสี

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

title สั่งซื้อสินค้าออนไลน์ (Checkout) — Activity Diagram\nMonolith: ระบบตัวเดียวทำ logic ทั้งหมด · บริการภายนอกกำกับ (external)

|Customer|
start
' สมมติ login แล้ว (session ผ่าน allauth) — ไม่ต้องวาด OAuth ซ้ำใน flow นี้
:กดสั่งซื้อสินค้าในตะกร้า;

|ระบบร้านค้าออนไลน์|
:ตรวจ session + สิทธิ์ (ลูกค้าที่ล็อกอิน);
:สร้างคำสั่งซื้อ (สถานะ pending);
:ตรวจสอบสต๊อกสินค้า (ORM);
if (สต๊อกเพียงพอหรือไม่?) then (ไม่พอ)
  :ยกเลิกคำสั่งซื้อ;
  stop
else (พอ)
endif
:เรียกชำระเงิน;

|Customer|
repeat
  |Payment Gateway (external)|
  :ประมวลผลการชำระเงิน;
repeat while (ชำระเงินสำเร็จหรือไม่?) is (ไม่สำเร็จ — ลูกค้าลองใหม่) not (สำเร็จ)

|ระบบร้านค้าออนไลน์|
:ยืนยันคำสั่งซื้อ + ตัดสต๊อก (write);

fork
  :แสดงหน้ายืนยันให้ลูกค้า (main flow);
fork again
  :เขียน audit log (ยืนยันคำสั่งซื้อ) ผ่าน signal;
fork again
  |เซิร์ฟเวอร์อีเมล (external)|
  :ส่งอีเมลใบเสร็จให้ลูกค้า;
end fork

stop

legend right
  |<back:white>    </back>| Actor ภายนอก (Customer) |
  |<back:#F5F5F5>    </back>| ระบบร้านค้าออนไลน์ (Django monolith) — เส้นขอบทึบ |
  |<back:#F5F5F5>    </back>| บริการภายนอก (Payment Gateway, อีเมล) — สื่อด้วยข้อความ "(external)" ไม่ใช่สี |
  หมายเหตุ: สร้างคำสั่งซื้อ + ตรวจสต๊อก + ตัดสต๊อก เป็น in-process logic ใน process เดียว ไม่ใช่การเรียกข้าม service
endlegend

@enduml
```
