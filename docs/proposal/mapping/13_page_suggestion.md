# Field Mapping: `page-suggestion.html` (เสนอแนะสิ่งของใหม่)

> **หน้าจอ:** ฟอร์มเสนอแนะสิ่งของที่ต้องการให้จัดหา และดูประวัติข้อเสนอแนะ  
> **ไฟล์ต้นทาง:** `pages/page-suggestion.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student)  
> **Use Case:** UC-12  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **ฟอร์มส่งข้อเสนอแนะใหม่** | | | |
| ชื่อสิ่งของที่ต้องการเสนอ | Input (Text) | `SUGGESTION.name` | เช่น Arduino UNO, ปากกาดิจิทัล |
| รายละเอียด / เหตุผลความจำเป็น | Input (Textarea) | `SUGGESTION.detail` | วัตถุประสงค์การใช้งานและเหตุผลที่ต้องการ |
| ผู้เสนอแนะ | FK (Hidden) | `SUGGESTION.user_id` | บันทึกรหัสผู้ใช้งานปัจจุบัน (`STUDENT.user_id`) |
| สถานะข้อเสนอแนะเริ่มต้น | Status (Auto) | `SUGGESTION.status` | เริ่มต้นบันทึกเป็น `'SUBMITTED'` (ส่งคำเสนอแนะแล้ว) |
| วันเวลาที่ส่งคำเสนอแนะ | Datetime (Auto) | `SUGGESTION.created_at` | บันทึกเวลาส่งคำเสนอแนะ (`NOW()`) |
| **ประวัติข้อเสนอแนะของฉัน (History List)** | | | |
| ชื่อสิ่งของที่เคยเสนอ | Text | `SUGGESTION.name` | ข้อมูลรายการที่เคยเสนอ |
| รายละเอียดที่เคยเสนอ | Text | `SUGGESTION.detail` | รายละเอียดที่เคยกรอก |
| สถานะการพิจารณา | Badge | `SUGGESTION.status` | `SUBMITTED`, `ACKNOWLEDGED`, `PURCHASE_PLAN`, `REJECTED` |
| วันที่เสนอแนะ | Datetime | `SUGGESTION.created_at` | แสดงวันเวลาที่ส่งข้อมูล |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- ไม่มีฟิลด์นอกเหนือจากที่ระบุ

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `SUGGESTION`
- `STUDENT`
