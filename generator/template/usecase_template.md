# Template — Use Case Diagram (`.puml`)

> วิธีใช้: คัดลอกโค้ด PlantUML ด้านล่างไปที่ `<module>/usecase.puml` (หรือ `<module>_usecase.puml`)
> แทนที่ `{{...}}` ด้วยข้อมูลจริง และลบ/เพิ่ม actor, package, use case ตามจำนวนจริงของโครงงาน
> ต้องทำตามกฎใน [`usecase_generate_guide.md`](../guide/usecase_generate_guide.md) ทุกข้อ โดยเฉพาะ **ห้ามมี actor "System"** และ **ห้ามใช้ลูกศรเชื่อม actor–use case**
> ดูตัวอย่างที่กรอกครบแล้วได้ที่ [`usecase_example.md`](../example/usecase_example.md)

---

## ฉบับละเอียด — `{{module}}_usecase.puml`

```plantuml
@startuml {{module}}_usecase
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

title <b>{{ชื่อระบบ/แอปพลิเคชัน}}</b>\n(Use Case Diagram — อ้างอิง Use Case Specification UC-01 ถึง UC-{{N}})

left to right direction

' ===== Actor: เฉพาะสิ่งภายนอกขอบเขตระบบเท่านั้น ห้ามมี "ระบบ/System" =====
actor "{{ชื่อ actor 1}}" as {{ActorAlias1}}
actor "{{ชื่อ actor 2}}" as {{ActorAlias2}}

rectangle "{{ชื่อระบบ}}" {

  ' ===== {{ชื่อกลุ่มที่ 1}} =====
  package "{{ชื่อกลุ่มที่ 1}}" {
    usecase "UC-{{01}}\n{{ชื่อ use case}}" as UC{{01}}
    usecase "UC-{{02}}\n{{ชื่อ use case}}" as UC{{02}}
  }

  ' ===== {{ชื่อกลุ่มที่ 2}} =====
  package "{{ชื่อกลุ่มที่ 2}}" {
    usecase "UC-{{03}}\n{{ชื่อ use case}}" as UC{{03}}
  }
}

' ===== ความสัมพันธ์ actor–use case (เส้นธรรมดา ห้ามใช้ลูกศร) =====
{{ActorAlias1}} -- UC{{01}}
{{ActorAlias2}} -- UC{{02}}
{{ActorAlias2}} -- UC{{03}}

' ===== ความสัมพันธ์ use case–use case =====
' <<include>>: BaseUseCase ..> IncludedUseCase (เกิดขึ้นเสมอ)
UC{{01}} ..> UC{{03}} : <<include>>

' <<extend>>: ExtensionUseCase ..> BaseUseCase (เกิดขึ้นตามเงื่อนไข)
UC{{02}} ..> UC{{01}} : <<extend>>

@enduml
```

---

## ฉบับภาพรวม (Top View) — `{{module}}_usecase_overview.puml`

> ยุบแต่ละ package ในฉบับละเอียดให้เหลือ use case ตัวแทนกลุ่มละ 1 ตัว ใช้เปิดพรีเซนต์

```plantuml
@startuml {{module}}_usecase_overview
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

title <b>{{ชื่อระบบ/แอปพลิเคชัน}}</b>\n(Use Case Diagram — ภาพรวมระดับสูง / Top View)

left to right direction

actor "{{ชื่อ actor 1}}" as {{ActorAlias1}}
actor "{{ชื่อ actor 2}}" as {{ActorAlias2}}

rectangle "{{ชื่อระบบ}}" {
  usecase "{{ชื่อกลุ่มที่ 1}}" as UCG1
  usecase "{{ชื่อกลุ่มที่ 2}}" as UCG2
}

{{ActorAlias1}} -- UCG1
{{ActorAlias2}} -- UCG2

UCG1 ..> UCG2 : <<include>>

@enduml
```
