# Field Mapping: `page-report-damage.html` (แจ้งอุปกรณ์ชำรุด)

> **หน้าจอ:** ฟอร์มแจ้งซ่อม/แจ้งอุปกรณ์ชำรุดทั่วไป โดยไม่ต้องมีประวัติการยืม  
> **ไฟล์ต้นทาง:** `pages/page-report-damage.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student)  
> **Use Case:** UC-38  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **ตัวเลือกประเภทที่จะแจ้ง** | | | |
| ตัวเลือกประเภท (อุปกรณ์ในระบบ vs อุปกรณ์สถานที่) | Radio Button | จัดการบันทึก `DAMAGE_REPORT` | เลือกว่าเป็นครุภัณฑ์ในระบบยืม-คืน หรืออุปกรณ์ประจำห้อง/สถานที่ |
| **กรณีครุภัณฑ์ในระบบ** | | | |
| ค้นหา/เลือกครุภัณฑ์ในระบบ | Select / Search | `ITEM.id`, `ITEM.name`, `EQUIPMENT.asset_tag` | ดึงรายการครุภัณฑ์จากฐานข้อมูลมาให้เลือก |
| สถานที่จัดเก็บเดิมในคลัง | Text (Auto) | `DAMAGE_REPORT.origin_location` | ดึงตำแหน่งเดิมจาก `ITEM.location` มาบันทึก |
| **กรณีอุปกรณ์ประจำห้อง/สถานที่ทั่วไป** | | | |
| ชื่ออุปกรณ์ที่พบชำรุด | Input (Text) | `DAMAGE_REPORT.item_name` | เช่น โปรเจกเตอร์ติดผนัง, ปลั๊กไฟ, แอร์ |
| **ข้อมูลความเสียหายและการส่งเรื่อง** | | | |
| สถานที่พบความชำรุด (ตึก/ห้อง) | Input (Text) / Select | `DAMAGE_REPORT.location` | เช่น ตึก EN ห้อง 304 |
| รายละเอียดอาการชำรุด | Input (Textarea) | `DAMAGE_REPORT.symptom` | ระบุลักษณะอาการเสีย |
| รูปถ่ายหลักฐานความเสียหาย | Input (File) | `DAMAGE_REPORT.photo` | รูปภาพสภาพชำรุด |
| ผู้แจ้งเรื่อง | FK (Hidden) | `DAMAGE_REPORT.user_id` | บันทึกรหัสนักศึกษาผู้แจ้ง (`STUDENT.user_id`) |
| สถานะเรื่องแจ้งซ่อม | Status (Auto) | `DAMAGE_REPORT.status` | บันทึกสถานะเริ่มต้นเป็น `'PENDING'` (รอตรวจสอบ) |
| วันเวลาที่แจ้ง | Datetime (Auto) | `DAMAGE_REPORT.created_at` | บันทึกเวลาที่ส่งเรื่อง (`NOW()`) |
| **ประวัติการแจ้งซ่อมของตนเอง (History List)** | | | |
| รายการเรื่องที่เคยแจ้ง | List Item | `DAMAGE_REPORT.id`, `DAMAGE_REPORT.item_name`, `DAMAGE_REPORT.symptom`, `DAMAGE_REPORT.status`, `DAMAGE_REPORT.created_at` | แสดงรายการที่ตนเองเคยแจ้งพร้อมสถานะติดตาม |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
1. **`p_report_damage_ocr_input` (ช่องอัปโหลดสแกน OCR Asset Tag):** เครื่องมือช่วยอ่านข้อความจากรูปบนฝั่งเบราว์เซอร์ (Client-side Helper) ไม่มีการเก็บใน ERD

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `DAMAGE_REPORT`
- `ITEM`
- `EQUIPMENT`
- `STUDENT`
