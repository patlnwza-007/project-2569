# Template — Activity Diagram แบบมี Swimlane (`.puml`)

> วิธีใช้: คัดลอกโค้ด PlantUML ด้านล่างไปที่ `<app>/activity_<ชื่อฟังก์ชัน>.puml`
> แทนที่ `{{...}}` ด้วยข้อมูลจริง และลบ/เพิ่ม partition, activity, fork, loop ตามจำนวนจริงของกระบวนการ
> ต้องทำตามกฎใน [`activity_diagram_generate_guide.md`](../guide/activity_diagram_generate_guide.md) ทุกข้อ โดยเฉพาะ **partition หน้าจอต้องเป็น `frontend:<PageCode>` ที่ตรงกับ `module_state_diagram.puml`**, **ฝั่งเซิร์ฟเวอร์ใช้ `backend` เดี่ยว ๆ (ไม่ใช่ชื่อโปรเจกต์)**, **ไม่มี API Gateway/JWT — auth เกิดตอน login เท่านั้น**, และ **ห้ามใช้สีหลายโทน (monochrome เท่านั้น)**
> ก่อนกรอก ต้องรู้ `PageCode` ของทุกหน้าที่ flow นี้ผ่านแล้ว — เปิด `<app>/state/module_state_diagram.puml` ไว้ข้าง ๆ (ดู [`ui_state_diagram_generate_guide.md`](../guide/ui_state_diagram_generate_guide.md) ถ้ายังไม่มี state diagram ให้ทำก่อนไฟล์นี้)
> ดูตัวอย่างที่กรอกครบแล้วได้ที่ [`activity_diagram_example.md`](../example/activity_diagram_example.md)

---

## เตรียมข้อมูลก่อนกรอก template

ไล่ Basic Flow ของ UC นี้ทีละขั้น แล้วกรอกตารางนี้ก่อน — ตารางนี้เองคือโครงของไดอะแกรม (แถวไหนหน้าจอเปลี่ยนคือจุดที่ partition ต้องเปลี่ยนตาม):

| ขั้นที่ | ใครทำ | เกิดที่หน้าไหน (`PageCode` จาก state diagram) | กิจกรรม |
|---|---|---|---|
| 1 | Actor | `{{PageCode1}}` | {{กิจกรรมเริ่มต้น}} |
| 2 | backend | — | {{ตรวจสอบ/ประมวลผล}} |
| 3 | Actor | `{{PageCode2}}` *(ถ้าเปลี่ยนหน้า)* | {{กิจกรรมถัดไป}} |

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

title {{ชื่อฟังก์ชัน}} — Activity Diagram\npartition หน้าจอ = frontend:PageCode (ตรงกับ state diagram) · ฝั่งเซิร์ฟเวอร์ = backend

' ===== หน้าแรกที่ actor เริ่มกระบวนการ — PageCode ต้องมีอยู่จริงใน module_state_diagram.puml =====
' หมายเหตุ: สมมติว่าผู้ใช้ login แล้ว (session) — ไม่ต้องวาด OAuth/SSO ซ้ำใน flow ทั่วไป
|frontend:{{PageCode1}}|
start
:{{กิจกรรมเริ่มต้นของ actor}};

' ===== ฝั่งเซิร์ฟเวอร์ประมวลผล (view + model + logic) — partition เดียวชื่อ backend เสมอ =====
' ถ้า flow เน้นเรื่องสิทธิ์ ใส่ step ตรวจสิทธิ์เป็นกิจกรรมแรกได้ (ไม่ใช่ partition แยก)
|backend|
:ตรวจ session + สิทธิ์ ({{role ที่อนุญาต}});
:{{ประมวลผล/บันทึกข้อมูล}};

' ===== ถ้าขั้นตอนถัดไปอยู่คนละหน้า ต้องสลับ partition ตาม PageCode ใหม่ (ตรงกับ transition ใน state diagram) =====
'|frontend:{{PageCode2}}|
':{{กิจกรรมบนหน้าถัดไป}};

' ===== (ทางเลือก) แยก backend ตาม Django app เฉพาะเมื่อ flow ข้ามหลาย app จริง =====
' การเรียกข้าม app ใน monolith = in-process function call ไม่ใช่ network call (ไม่ต้องเส้นประ)
'|backend:{{app อื่น เช่น catalog}}|
':{{เช่น ลดจำนวนคงเหลือ}};

' ===== ตัวอย่าง loop/retry — ลบออกถ้าฟังก์ชันนี้ไม่มีการวนซ้ำ =====
' ไม่มี Gateway ให้ผ่านทุกรอบ — วนที่ frontend:PageCode เดิม ↔ backend ตรง ๆ
|frontend:{{PageCode1}}|
repeat
  :{{กิจกรรมที่ต้องทำซ้ำ เช่น กรอกฟอร์มใหม่}};
  |backend|
  :{{ตรวจ validation}};
repeat while ({{คำถามเงื่อนไข}}?) is ({{ยังไม่ผ่าน}}) not ({{ผ่านแล้ว}})

' ===== Write operation สำคัญ + side effect แบบ non-blocking (signal/async) =====
|backend|
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
  |<back:white>    </back>| frontend:PageCode — หน้าจอที่ผู้ใช้เห็น (ต้องตรงกับ state diagram) |
  |<back:#F5F5F5>    </back>| backend — เส้นขอบทึบ |
  |<back:#F5F5F5>    </back>| บริการภายนอก (SSO/SMTP/storage) — สื่อด้วยข้อความ "(external)" |
  หมายเหตุ: ทุก view ผ่าน login_required + permission — auth หลักเกิดตอน login ผ่าน UBU Single Sign-On (session)
endlegend

@enduml
```

---

## ตรวจก่อนส่ง

```bash
grep -ohE '\|frontend:[A-Za-z][A-Za-z0-9]*\|' {{app}}_activity_{{ชื่อฟังก์ชัน}}.puml | tr -d '|' | cut -d: -f2 | sort -u | while read p; do grep -qE " as $p$" module_state_diagram.puml || echo "ORPHAN: $p"; done
```

ต้องไม่มี output — ถ้ามี แปลว่า `PageCode` ที่อ้างในไฟล์นี้ยังไม่มีอยู่จริงใน state diagram (แก้ state diagram ก่อนตาม §1.4 ของ guide ห้ามตั้งชื่อหน้าใหม่ในไฟล์นี้เอง) แล้วเดิน [checklist §7 ของ guide](../guide/activity_diagram_generate_guide.md#7-checklist-ก่อนส่งไดอะแกรม) ให้ครบทุกข้อ
