# Template — Activity Diagram แบบมี Swimlane (`.puml`)

> วิธีใช้: คัดลอกโค้ด PlantUML ด้านล่างไปที่ `<app>/activity_<ชื่อฟังก์ชัน>.puml`
> แทนที่ `{{...}}` ด้วยข้อมูลจริง และลบ/เพิ่ม partition, activity, fork, loop ตามจำนวนจริงของกระบวนการ
> ต้องทำตามกฎใน [`activity_diagram_generate_guide.md`](../guide/activity_diagram_generate_guide.md) ทุกข้อ โดยเฉพาะ **partition = actor/ระบบ Django/บริการภายนอก (ไม่ใช่ 1 view)**, **ไม่มี API Gateway/JWT — auth เกิดตอน login เท่านั้น**, และ **ห้ามใช้สีหลายโทน (monochrome เท่านั้น)**
> ดูตัวอย่างที่กรอกครบแล้วได้ที่ [`activity_diagram_example.md`](../example/activity_diagram_example.md)

---

```plantuml
@startuml {{app}}_activity_{{ชื่อฟังก์ชัน}}
' ══════════════════════════════════════════════════════════════════
' รองรับภาษาไทย — อ่านก่อน render:
' 1. บันทึกไฟล์นี้เป็น UTF-8 (ไม่ต้องมี BOM) เสมอ
' 2. ถ้า render ผ่าน CLI (plantuml.jar) ต้องระบุ flag encoding ด้วย:
'      java -Dfile.encoding=UTF-8 -jar plantuml.jar -charset UTF-8 {{app}}_activity_{{ชื่อฟังก์ชัน}}.puml
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

' ===== Monochrome เท่านั้น — ห้ามให้แต่ละ partition มีสีต่างกัน =====
skinparam activity {
  BackgroundColor #F5F5F5
  BorderColor #424242
  FontName "TH Sarabun New"
  FontSize 13
  DiamondBackgroundColor #FAFAFA
  DiamondBorderColor #616161
}

title {{ชื่อฟังก์ชัน}} — Activity Diagram\nMonolith: partition = actor / ระบบ Django / บริการภายนอก (ไม่ใช่ 1 view)

' ===== Actor ภายนอก (human) ที่ริเริ่มกระบวนการ =====
' หมายเหตุ: สมมติว่าผู้ใช้ login แล้ว (session) — ไม่ต้องวาด OAuth ซ้ำใน flow ทั่วไป
|{{Actor 1}}|
start
:{{กิจกรรมเริ่มต้นของ actor}};

' ===== ระบบ Django ประมวลผล (view + model + logic) =====
' ถ้า flow เน้นเรื่องสิทธิ์ ใส่ step ตรวจสิทธิ์เป็นกิจกรรมแรกได้ (ไม่ใช่ partition แยก)
|ระบบ {{ชื่อระบบ}}|
:ตรวจ session + สิทธิ์ ({{role ที่อนุญาต}});
:{{ประมวลผล/บันทึกข้อมูล}};

' ===== (ทางเลือก) แยก partition ตาม Django app เฉพาะเมื่อ flow ข้ามหลาย app จริง =====
' การเรียกข้าม app ใน monolith = in-process function call ไม่ใช่ network call (ไม่ต้องเส้นประ)
'|{{app อื่น เช่น catalog}}|
':{{เช่น ลดจำนวนคงเหลือ}};

' ===== ตัวอย่าง loop/retry — ลบออกถ้าฟังก์ชันนี้ไม่มีการวนซ้ำ =====
' ไม่มี Gateway ให้ผ่านทุกรอบ — วนที่ actor ↔ ระบบ ตรง ๆ
|{{Actor 1}}|
repeat
  :{{กิจกรรมที่ต้องทำซ้ำ เช่น กรอกฟอร์มใหม่}};
  |ระบบ {{ชื่อระบบ}}|
  :{{ตรวจ validation}};
repeat while ({{คำถามเงื่อนไข}}?) is ({{ยังไม่ผ่าน}}) not ({{ผ่านแล้ว}})

' ===== Write operation สำคัญ + side effect แบบ non-blocking (signal/async) =====
|ระบบ {{ชื่อระบบ}}|
:{{บันทึกข้อมูลสำคัญ (write)}};

fork
  :{{ดำเนินการต่อ / ตอบผู้ใช้}};
fork again
  :เขียน audit log ({{ชื่อ action}}) ผ่าน signal;
fork again
  |เซิร์ฟเวอร์อีเมล (external)|
  :ส่งอีเมลแจ้งเตือน (ถ้ามี);
end fork

stop

legend right
  |<back:white>    </back>| Actor ภายนอก (human) |
  |<back:#F5F5F5>    </back>| ระบบ Django — เส้นขอบทึบ |
  |<back:#F5F5F5>    </back>| บริการภายนอก (OAuth/SMTP/storage) — สื่อด้วยข้อความ "(external)" |
  หมายเหตุ: ทุก view ผ่าน login_required + permission — auth หลักเกิดตอน login ผ่าน allauth/Google (session)
endlegend

@enduml
```
