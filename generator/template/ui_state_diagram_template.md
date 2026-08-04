# Template — UI State Diagram (`.puml`)

> วิธีใช้: ทำ **3 ส่วน** ต่อ 1 Django app เสมอ
> 1. คัดลอกบล็อก A ไปที่ `<app>/state/module_state_diagram.puml` (ระดับหน้าจอ)
> 2. คัดลอกบล็อก B ไปที่ `architecture/overview_state_diagram.puml` (ระดับ app — ทำครั้งเดียวต่อระบบ ไม่ใช่ต่อ app)
> 3. คัดลอกบล็อก C ไปที่ `<app>/state/module_state_diagram.md` (ตาราง traceability — **บังคับ**)
>
> แทนที่ `{{...}}` ด้วยข้อมูลจริง แล้วลบ/เพิ่ม state, transition, note ตามจำนวนจริงของ app นั้น
> ต้องทำตามกฎใน [`ui_state_diagram_generate_guide.md`](../guide/ui_state_diagram_generate_guide.md) ทุกข้อ โดยเฉพาะ **1 state = 1 หน้าจอจริง (ไม่ใช่สถานะข้อมูล)**, **page_code = ASCII PascalCase ที่ derive เป็น URL/template/ไฟล์ mockup ได้ 1:1**, **ไม่มี unreachable state / dead-end**, และ **monochrome เท่านั้น**
> ดูตัวอย่างที่กรอกครบแล้วได้ที่ [`ui_state_diagram_example.md`](../example/ui_state_diagram_example.md)

---

## เตรียมข้อมูลก่อนกรอก template (ทำตารางนี้ในกระดาษทดก่อน)

อ่าน `<app>/proposal/usecase_description.md` แล้ว `<app>/activity/*.puml` ตามลำดับ (guide §1) จากนั้นกรอก:

| UC | Post-condition → คำนาม | Basic Flow → suffix | `page_code` ที่ได้ | Actor |
|---|---|---|---|---|
| UC-{{nn}} | {{คำนาม เช่น Item}} | {{List/Detail/Form/Confirm/...}} | `{{ItemList}}` | {{Actor}} |
| ... | ... | ... | ... | ... |

> ถ้าขั้นนี้ได้ page_code ที่เป็นคำกริยา (`Submit`, `Approve`) หรือมีเลข UC ปนอยู่ → ยังผิดกฎ guide §4.1 ให้กลับไปอ่าน Post-condition ใหม่

---

## บล็อก A — `<app>/state/module_state_diagram.puml`

```plantuml
@startuml module_state_diagram_{{app}}
' ══════════════════════════════════════════════════════════════════
' {{ชื่อระบบ}} — UI State Transition Diagram (ระดับหน้าจอ) ของ app `{{app}}`
' อ้างอิง: {{app}}/proposal/usecase_description.md,
'          {{app}}/activity/*.puml
'
' รองรับภาษาไทย — อ่านก่อน render:
' 1. บันทึกไฟล์นี้เป็น UTF-8 (ไม่ต้องมี BOM) เสมอ
' 2. ถ้า render ผ่าน CLI (plantuml.jar) ต้องระบุ flag encoding ด้วย:
'      java -Dfile.encoding=UTF-8 -jar plantuml.jar -charset UTF-8 module_state_diagram_{{app}}.puml
' 3. บังคับใช้ Smetana (pure-Java layout engine) แทน Graphviz/dot
'    เพราะ Graphviz บางระบบ (โดยเฉพาะ Windows) อ่าน UTF-8 ไม่ตรง ทำให้ตัวอักษรไทยเพี้ยน/หาย
' 4. ฟอนต์: Windows = "TH Sarabun New" · Linux/PlantUML server = "Noto Sans Thai"
'
' กฎที่ไดอะแกรมนี้ต้องรักษา (ดู ui_state_diagram_generate_guide.md):
'   - 1 state = 1 หน้าจอ = 1 URL — สถานะข้อมูล (รออนุมัติ/อนุมัติแล้ว) อยู่บน label + note เท่านั้น
'   - ทุก state มีขาเข้าและขาออก (ไม่มี unreachable / dead-end)
'   - UC ที่เป็น <<extend>> ไม่มี state ของตัวเอง — เป็นฟิลด์ในหน้าฐาน
'   - monochrome ล้วน แยกโซนด้วยชื่อ ไม่ใช่สี
' ══════════════════════════════════════════════════════════════════
!pragma layout smetana
skinparam defaultFontName "TH Sarabun New"
skinparam defaultFontSize 14

!theme plain
skinparam titleFontName "TH Sarabun New"
skinparam titleFontSize 20
skinparam noteFontName "TH Sarabun New"
skinparam noteFontSize 11
skinparam ArrowFontName "TH Sarabun New"
skinparam ArrowFontSize 11

' ===== Monochrome เท่านั้น — ห้ามให้แต่ละโซน/role มีสีต่างกัน =====
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

title {{ชื่อระบบ}} — UI State Diagram: app `{{app}}`\n1 state = 1 หน้าจอ = 1 URL · เส้น = ปุ่ม/ลิงก์ที่กดได้จริง

' ═════════ โซน {{Role 1}} ═════════
' ใช้ composite state เฉพาะเมื่อ app นี้มีหลาย role ใช้งาน (guide §8.2)
' ถ้ามี role เดียว ลบบล็อก state "..." { } ออก เหลือแต่ state ข้างในกับ [*] -->
state "{{Role 1}}" as {{Role1}}Zone {

  ' ---------- หน้าแรกของ role นี้ ----------
  state "{{ชื่อหน้าภาษาไทย เป็นคำนามวลี}}\n(UC-{{nn}})" as {{PageCode1}}
  note right of {{PageCode1}}
    แสดง: {{สิ่งที่หน้านี้แสดง — จาก Basic Flow ขั้นที่ระบบแสดงผล}}
    ว่าง: "{{ข้อความเมื่อไม่มีข้อมูล — จาก Alternative Flow}}"
  end note

  ' ---------- หน้ารายการ (suffix List) ----------
  state "{{ชื่อหน้า}}\n(UC-{{nn}}, extend UC-{{mm}})" as {{PageCode2}}
  note right of {{PageCode2}}
    แสดง: {{คอลัมน์/การ์ดที่แสดงต่อรายการ}} (pagination)
    ฟิลด์: {{ช่องค้นหา + ตัวกรอง — UC ที่ extend เข้ามา ไม่แยกหน้า}}
    ว่าง: "{{ยังไม่มีรายการ}}" / "{{ไม่พบรายการที่ค้นหา}}"
  end note

  ' ---------- หน้ารายละเอียด (suffix Detail) ----------
  state "{{ชื่อหน้า}}\n(UC-{{nn}})" as {{PageCode3}}
  note right of {{PageCode3}}
    แสดง: {{ฟิลด์ที่แสดงของ 1 รายการ}}
    ปุ่ม: {{ปุ่มหลักบนหน้า + เงื่อนไขที่ปุ่มจะโชว์}}
    ผิดพลาด: {{กรณีข้อมูลถูกลบ/ไม่พบ — จาก Alternative Flow}}
  end note

  ' ---------- หน้าฟอร์ม (suffix Form) — ชื่อเป็นกริยาได้ตาม guide §5.2 ----------
  state "{{ยืนยัน/กรอก ...}}\n(UC-{{nn}}, include UC-{{mm}})" as {{PageCode4}}
  note right of {{PageCode4}}
    ฟิลด์: {{ฟิลด์ที่ actor กรอก + ระบุว่าอันไหนบังคับ}}
    ผิดพลาด: {{validation error — จาก Alternative Flow}}
    กฎ: {{Business Rule ที่กระทบ UI เช่น ฟิลด์นี้บังคับเฉพาะเมื่อ...}}
  end note

  ' ---------- จุดเริ่มของ role นี้ (1 อันต่อ 1 โซน) ----------
  [*] --> {{PageCode1}}

  ' ---------- transition: label = ข้อความบนปุ่มจริง + guard + ผลลัพธ์ (guide §6.2) ----------
  {{PageCode1}} --> {{PageCode2}} : กด "{{ชื่อเมนู}}"
  {{PageCode2}} --> {{PageCode1}} : กด "กลับ"
  {{PageCode2}} --> {{PageCode3}} : เลือก{{รายการ}} (UC-{{nn}})
  {{PageCode3}} --> {{PageCode2}} : กด "กลับ"
  {{PageCode3}} --> {{PageCode4}} : กด "{{ปุ่มหลัก}}"\n({{guard จาก Pre-condition/Business Rule}})
  {{PageCode4}} --> {{PageCode1}} : กด "{{ปุ่มยืนยัน}}"\n→ {{สถานะข้อมูลใหม่}}
  {{PageCode4}} --> {{PageCode3}} : กด "ยกเลิก"

  ' ---------- self-transition: action ที่ทำเสร็จแล้วยังอยู่หน้าเดิม (guide §6.4) ----------
  {{PageCode2}} --> {{PageCode2}} : กด "ค้นหา"/เลือกตัวกรอง (UC-{{mm}})
  {{PageCode4}} --> {{PageCode4}} : {{ข้อมูลไม่ครบ}} → แสดง validation error
}

' ═════════ โซน {{Role 2}} — ลบทั้งบล็อกถ้า app นี้มี role เดียว ═════════
' โซนต่างกันไม่ต้องมีเส้นเชื่อมกัน — 1 session = 1 role (guide §8.2)
state "{{Role 2}}" as {{Role2}}Zone {
  state "{{ชื่อหน้า}}\n(UC-{{nn}})" as {{PageCode5}}
  note right of {{PageCode5}}
    แสดง: {{...}}
  end note

  [*] --> {{PageCode5}}
}

' ═════════ note ระดับไฟล์ — UC ที่ไม่มีหน้าจอ + พฤติกรรมอัตโนมัติ (guide §3.1, §6.6) ═════════
note bottom of {{Role1}}Zone
  ครอบคลุม UC-{{nn}} ถึง UC-{{mm}} ({{จำนวน}} use case ของ role นี้)
  UC ที่ไม่มีหน้าจอ: UC-{{xx}} ({{เหตุผล เช่น background job / API ให้ app อื่นเรียก}})
  ไม่นับเป็น state/transition: {{การแจ้งเตือน in-app + อีเมล / auto-expire job}}
end note

@enduml
```

---

## บล็อก B — `architecture/overview_state_diagram.puml` (1 ไฟล์ต่อระบบ)

```plantuml
@startuml overview_state_diagram
' ══════════════════════════════════════════════════════════════════
' {{ชื่อระบบ}} — UI State Diagram ระดับ app (ผู้ใช้เข้าถึงแต่ละ Django app ได้อย่างไร)
' 1 state = 1 Django app · ห้ามใส่หน้าจอย่อยของ app ในไฟล์นี้ (นั่นคือหน้าที่ของ module_state_diagram)
' UI_django_frontend.md §4.2 นับ "1 การ์ดใน Dashboard = 1 app = 1 เมนู" จากไฟล์นี้โดยตรง
' ══════════════════════════════════════════════════════════════════
!pragma layout smetana
skinparam defaultFontName "TH Sarabun New"
skinparam defaultFontSize 14

!theme plain
skinparam titleFontName "TH Sarabun New"
skinparam titleFontSize 20
skinparam noteFontName "TH Sarabun New"
skinparam noteFontSize 11
skinparam ArrowFontName "TH Sarabun New"
skinparam ArrowFontSize 11

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

title {{ชื่อระบบ}} — Overview State Diagram (ระดับ Django app)\n1 state = 1 app = 1 การ์ดทางลัดใน Dashboard กลาง

state "หน้าเข้าสู่ระบบ\n(UC-{{nn}})" as Login
note right of Login
  แสดง: ปุ่ม "เข้าสู่ระบบด้วย {{ผู้ให้บริการ SSO}}" เท่านั้น (ไม่มีฟอร์มของระบบเอง)
  ผิดพลาด: ยืนยันตัวตนไม่สำเร็จ / บัญชีถูกระงับสิทธิ์ → ปฏิเสธการเข้าสู่ระบบ
end note

state "Dashboard กลาง" as Dashboard
note right of Dashboard
  แสดง: คำทักทาย + role badge, KPI card, การ์ดทางลาด 1 ใบต่อ 1 app
  กฎ: การ์ด/เมนูแสดงเฉพาะ app ที่ role ปัจจุบันมีสิทธิ์
end note

' 1 state ต่อ 1 Django app — page_code = <AppName>App
state "{{ชื่อ app ภาษาไทย}}\n({{app1}})" as {{App1}}App
state "{{ชื่อ app ภาษาไทย}}\n({{app2}})" as {{App2}}App

[*] --> Login
Login --> Login : ยืนยันตัวตนไม่สำเร็จ /\nบัญชีถูกระงับสิทธิ์
Login --> Dashboard : ยืนยันตัวตนสำเร็จ\n(บทบาทจาก {{SSO}} หรือ Role Override)

' label ขาเข้า = ข้อความบนการ์ด/เมนูจริงใน Dashboard
Dashboard --> {{App1}}App : กดเมนู "{{ชื่อเมนู 1}}"
Dashboard --> {{App2}}App : กดเมนู "{{ชื่อเมนู 2}}"\n({{role ที่เห็นเมนูนี้}})

' label ขาออก = คำเดียวกับปุ่ม "กลับหน้าหลัก" ที่บังคับใน mockup_generate_guide.md §4.1
{{App1}}App --> Dashboard : กด "← กลับหน้าหลัก"
{{App2}}App --> Dashboard : กด "← กลับหน้าหลัก"

Dashboard --> [*] : ออกจากระบบ

note bottom of Dashboard
  แต่ละ app มีหน้าจอย่อยของตัวเองใน `<app>/state/module_state_diagram.puml`
  การเปลี่ยน role ไม่ใช่ transition ที่นี่ — มีผลตอนเข้าสู่ระบบครั้งถัดไปเท่านั้น
end note

@enduml
```

---

## บล็อก C — `<app>/state/module_state_diagram.md` (ตาราง Traceability — บังคับ)

```markdown
# `{{app}}` — UI State Diagram: ตาราง Traceability

> ไดอะแกรม: [`module_state_diagram.puml`](module_state_diagram.puml)
> ที่มา: `{{app}}/proposal/usecase_description.md` + `{{app}}/activity/*.puml`

## สรุปจำนวน

| ตัวชี้วัด | จำนวน | ต้องตรงกับ |
|---|---|---|
| UC ทั้งหมดของ app นี้ | {{n}} | `usecase_description.md` |
| UC ที่มีหน้าจอ | {{n}} | — |
| UC ที่ไม่มีหน้าจอ (background job / API) | {{n}} | note ท้ายไดอะแกรม |
| **`page_code` ที่ไม่ซ้ำ = จำนวนหน้าจอ** | **{{n}}** | จำนวน `path()` ใน `urls.py` = จำนวนไฟล์ใน `mockup/pages/` |

## ตาราง UC → หน้าจอ → ไฟล์

| UC | ชื่อ Use Case | Actor | ไฟล์ activity ที่ใช้ map | `page_code` | URL name | Template | ไฟล์ mockup |
|---|---|---|---|---|---|---|---|
| UC-{{nn}} | {{ชื่อ UC}} | {{Actor}} | `activity/{{ไฟล์}}.puml` | `{{PageCode}}` | `{{app}}:{{page_code_snake}}` | `{{app}}/{{page_code_snake}}.html` | `pages/page-{{page-code-kebab}}.html` |
| UC-{{mm}} | {{ชื่อ UC ที่ extend}} | {{Actor}} | `activity/{{ไฟล์}}.puml` | `{{PageCode}}` *(extend — ไม่แยกหน้า)* | (เดียวกัน) | (เดียวกัน) | (เดียวกัน) |
| UC-{{xx}} | {{ชื่อ UC}} | — | `activity/{{ไฟล์}}.puml` | **— ไม่มีหน้าจอ** ({{เหตุผล}}) | — | — | — |

## ผลการ Audit `page_code` ใน activity diagram (guide §12 — แก้ได้เลย ไม่ต้องถาม)

> การแก้ **ชื่อหน้าที่อ้างผิด/อ้างซ้ำ** ใน `activity/*.puml` ทำได้ทันที (ไม่เปลี่ยนพฤติกรรมระบบ) แต่ต้องบันทึกร่องรอยไว้ที่นี่ทุกจุด

| # | ไฟล์ activity | เดิม partition | แก้เป็น | ประเภท (§12.1) |
|---|---|---|---|---|
| 1 | `activity/{{ไฟล์}}.puml` | `\|{{ชื่อ actor เดิม}}\|` ตลอดไฟล์ | `\|frontend:{{PageCode}}\|` ตามหน้าที่เปลี่ยนจริง | {{(ง) partition ไม่เปลี่ยนตามหน้าจริง}} |
| 2 | `activity/{{ไฟล์}}.puml` | `\|frontend:{{PageCode ซ้ำ}}\|` | `\|frontend:{{PageCode}}\|` | {{(ค) สร้างหน้าซ้ำ}} |

## จุดที่เอกสารต้นทางยังต้องยืนยันก่อนแก้ (guide §11 — เชิงตรรกะเท่านั้น)

> ขั้นตอน/เงื่อนไข/ผลลัพธ์ที่ขัดกัน **ห้ามแก้เอง** — บันทึกไว้ที่นี่แล้วถามเจ้าของเอกสารก่อน

| # | จุดที่ขัดกัน | ไฟล์:บรรทัด (ฝั่ง A) | ไฟล์:บรรทัด (ฝั่ง B) | สถานะ |
|---|---|---|---|:---:|
| 1 | {{อธิบายสั้น ๆ}} | `{{file}}:{{line}}` | `{{file}}:{{line}}` | ☐ รอยืนยัน |
```

---

## ตรวจก่อนส่ง

รัน 2 คำสั่งนี้กับไฟล์ที่กรอกเสร็จ — ทั้งคู่ต้องไม่มี output (guide §6.5):

```bash
grep -oE ' as [A-Za-z][A-Za-z0-9]*$' module_state_diagram.puml | sed 's/ as //' | sort -u | while read p; do grep -qE -- "--> +$p( |$)" module_state_diagram.puml || echo "UNREACHABLE: $p"; done
```

```bash
grep -oE ' as [A-Za-z][A-Za-z0-9]*$' module_state_diagram.puml | sed 's/ as //' | sort -u | while read p; do grep -qE "(^|[^-])$p +-->" module_state_diagram.puml || echo "DEAD-END: $p"; done
```

> ทั้งสองคำสั่งจับเฉพาะ leaf state (ข้ามชื่อโซน composite ที่ลงท้ายด้วย `{`) และใช้ `-oE` ไม่ใช่ `-oP` เพื่อให้รันได้บน Git Bash/Windows

## ขั้นตอนสุดท้าย — audit `page_code` ใน activity diagram (guide §12)

ทำ **หลัง** 2 คำสั่งข้างบนผ่านแล้วเท่านั้น ทุก partition หน้าจอใน activity ต้องเขียนเป็น `|frontend:<PageCode>|` ตรงตัวอักษรกับ state diagram (ดู [`activity_diagram_generate_guide.md`](../guide/activity_diagram_generate_guide.md) §1) — ไม่ใช่ partition ชื่อ actor + comment อธิบายหน้าลอย ๆ:

```bash
# 1) รายชื่อ page_code ที่เป็นทางการ
grep -oE ' as [A-Za-z][A-Za-z0-9]*$' module_state_diagram.puml | sed 's/ as //' | sort -u
```

```bash
# 2) orphan check — frontend:X ใน activity ที่ไม่มี X อยู่จริงใน state diagram (ต้องไม่มี output)
grep -ohE '\|frontend:[A-Za-z][A-Za-z0-9]*\|' ../activity/*.puml | tr -d '|' | cut -d: -f2 | sort -u | while read p; do grep -qE " as $p$" module_state_diagram.puml || echo "ORPHAN: $p"; done
```

```bash
# 3) reverse check — หน้าที่มีอยู่จริงแต่ไม่มี activity อ้างถึง (ไม่ใช่ error เสมอไป — ดู guide §12.3)
grep -oE ' as [A-Za-z][A-Za-z0-9]*$' module_state_diagram.puml | sed 's/ as //' | sort -u | while read p; do grep -qrE "\|frontend:$p\|" ../activity/ || echo "ไม่มี activity อ้างถึง: $p"; done
```

```bash
# 4) transition ระดับคู่ — ดึงลำดับ frontend:X ต่อไฟล์ แล้วเทียบกับ arrow ใน state diagram
# ระวัง if/elseif/else ในไฟล์ activity อ่านเป็นลำดับต่อเนื่องผิด ๆ ได้ (ตรวจด้วยตาซ้ำก่อนสรุปว่า MISSING จริง)
for f in ../activity/*.puml; do
  grep -oE '\|frontend:[A-Za-z][A-Za-z0-9]*\|' "$f" | tr -d '|' | cut -d: -f2 | uniq | awk 'NR>1{print prev" --> "$0} {prev=$0}'
done | sort -u
```

จุดที่เป็น **(ก) อ้างผิดหน้า / (ข) อ้างหน้าที่ไม่มีจริง / (ค) สร้างหน้าซ้ำ / (ง) partition ไม่เปลี่ยนตามหน้าจริง** → แก้ partition ใน `activity/*.puml` ให้ตรงได้เลย **ไม่ต้องถาม** แล้วบันทึกในตาราง "ผลการ Audit" ของบล็อก C · จุดที่เป็น **(จ) ขั้นตอน/เงื่อนไข/ลำดับไม่ตรงกัน** → ห้ามแก้เอง ให้จดไว้ถามตาม guide §11

แล้วเดิน [checklist §13 ของ guide](../guide/ui_state_diagram_generate_guide.md#13-checklist-ก่อนส่งไดอะแกรม) ให้ครบทุกข้อ
