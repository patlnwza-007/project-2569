# Field Mapping: `page-suggestion-review.html` (คำเสนอแนะสิ่งของจากนักศึกษา)

> **หน้าจอ:** เจ้าหน้าที่ตรวจสอบคำเสนอแนะ กดรับทราบ ปฏิเสธ หรือแปลงเป็นแผนจัดซื้อ  
> **ไฟล์ต้นทาง:** `pages/page-suggestion-review.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-28  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **รายการคำเสนอแนะ** | | | |
| ชื่อสิ่งของที่เสนอแนะ | Text | `SUGGESTION.name` | รายการพัสดุที่นักศึกษาต้องการ |
| รายละเอียดและเหตุผลความจำเป็น | Text | `SUGGESTION.detail` | วัตถุประสงค์ที่นักศึกษาเสนอเข้ามา |
| ผู้เสนอแนะ | Text | `USER.name`, `USER.email` | ดึงชื่อผู้เสนอผ่าน `SUGGESTION.user_id -> USER.name` |
| วันเวลาที่เสนอ | Datetime | `SUGGESTION.created_at` | เวลาที่ส่งคำเสนอแนะ |
| สถานะคำเสนอแนะ | Badge | `SUGGESTION.status` | `SUBMITTED`, `ACKNOWLEDGED`, `PURCHASE_PLAN`, `REJECTED` |
| **การพิจารณาของเจ้าหน้าที่ (Actions)** | | | |
| ปุ่ม `[ ✓ รับทราบ ]` | Button | บันทึก `SUGGESTION` | ปรับสถานะเป็น `'ACKNOWLEDGED'` |
| ปุ่ม `[ ✕ ปฏิเสธ ]` | Button | บันทึก `SUGGESTION` | ปรับสถานะเป็น `'REJECTED'` |
| ปุ่ม `[ ➕ เพิ่มในแผนจัดซื้อ ]` | Button | บันทึก `PURCHASE_PLAN` | - ปรับสถานะคำเสนอแนะ: `SUGGESTION.status = 'PURCHASE_PLAN'`<br>- สร้างแถวใหม่ใน `PURCHASE_PLAN`: `suggestion_id = SUGGESTION.id`, `name = SUGGESTION.name`, `detail = SUGGESTION.detail`, `created_by = STAFF.user_id`, `created_at = NOW()` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- `p_suggestion_review_f-status` (ตัวกรองสถานะคำเสนอแนะบนหน้าจอ): Client-side filter

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `SUGGESTION`
- `PURCHASE_PLAN`
- `USER`
- `STUDENT`
- `STAFF`
