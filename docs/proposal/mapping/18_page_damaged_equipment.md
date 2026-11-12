# Field Mapping: `page-damaged-equipment.html` (ครุภัณฑ์เสียหายและเรื่องแจ้งซ่อม)

> **หน้าจอ:** จัดการครุภัณฑ์เสียหายและเรื่องแจ้งซ่อม แบ่งเป็น 2 แท็บ รองรับการส่งซ่อม/ปลดระวางแบบกลุ่ม (Batch Action)  
> **ไฟล์ต้นทาง:** `pages/page-damaged-equipment.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-35  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **แท็บที่ 1: ครุภัณฑ์เสียหายในคลัง (In-Warehouse Items)** | | | |
| Checkbox เลือกหลายรายการ | Checkbox (Multi) | ระบุแถว `EQUIPMENT` | รองรับการติ๊กเลือกหลายชิ้นเพื่ออัปเดตแบบกลุ่ม (Batch Action) |
| รูปภาพสิ่งของ | Image | `ITEM.image` | รูปถ่ายสิ่งของ |
| ชื่อสิ่งของ | Text | `ITEM.name` | ชื่อครุภัณฑ์ |
| รหัสประจำชิ้น | Text (Badge) | `EQUIPMENT.asset_tag` | รหัส Asset Tag ชิ้นที่เสียหาย |
| สถานที่ตั้งวางในคลัง | Text | `ITEM.location` | ที่ตั้งสิ่งของ |
| สถานะความเสียหาย | Badge | `EQUIPMENT.status` | `DAMAGED` (รอส่งซ่อม), `MAINTENANCE` (กำลังซ่อม), `RETIRED` (ปลดระวาง) |
| หมายเหตุสภาพความเสียหาย | Text | `EQUIPMENT.note` | รายละเอียดอาการเสียที่ตรวจพบ |
| ปุ่มดำเนินการเดี่ยวและแบบกลุ่ม | Buttons | บันทึก `EQUIPMENT.status` | - `[ 🔧 ส่งซ่อม ]` -> ปรับเป็น `MAINTENANCE`<br>- `[ ✅ ซ่อมเสร็จแล้ว ]` -> ปรับเป็น `AVAILABLE` (กลับมาพร้อมให้ยืม)<br>- `[ 📦 ปลดระวาง ]` -> ปรับเป็น `RETIRED` (ไม่ต้องระบุเหตุผล) |
| **แท็บที่ 2: รายการแจ้งซ่อมจากนักศึกษา (Student Damage Reports)** | | | |
| เลขที่ใบแจ้งชำรุด | Text | `DAMAGE_REPORT.id` | รหัสใบแจ้งซ่อมที่รับมาจาก UC-38 |
| วันเวลาที่แจ้ง | Datetime | `DAMAGE_REPORT.created_at` | เวลาที่นักศึกษาส่งเรื่อง |
| ผู้แจ้งเรื่อง | Text | `USER.name`, `STUDENT.student_id` | ดึงชื่อและรหัสนักศึกษาผ่าน `DAMAGE_REPORT.user_id` |
| ชื่ออุปกรณ์ที่แจ้งซ่อม | Text | `DAMAGE_REPORT.item_name` | ชื่อสิ่งของที่พบเสีย |
| รหัสครุภัณฑ์ (ถ้ามี) | Text (Badge) | `EQUIPMENT.asset_tag` | รหัสครุภัณฑ์ในระบบ (nullable) |
| สถานที่พบความชำรุด | Text | `DAMAGE_REPORT.location` | ตึก/ห้อง ที่พบอุปกรณ์เสีย |
| อาการชำรุด | Text | `DAMAGE_REPORT.symptom` | รายละเอียดอาการที่นักศึกษาระบุ |
| รูปถ่ายความเสียหาย | Image / Modal | `DAMAGE_REPORT.photo` | รูปถ่ายหลักฐาน |
| สถานะเรื่องแจ้งซ่อม | Badge | `DAMAGE_REPORT.status` | `PENDING` (รอตรวจสอบ), `IN_PROGRESS` (กำลังประสานงานช่าง), `RESOLVED` (ปิดงานซ่อมแล้ว) |
| ปุ่มรับเรื่อง `[ รับเรื่อง ]` | Button | บันทึก `DAMAGE_REPORT` | ปรับสถานะเป็น `'IN_PROGRESS'` |
| ปุ่มปิดงานซ่อม `[ ปิดงานซ่อม ]` | Button | บันทึก `DAMAGE_REPORT` | ปรับสถานะเป็น `'RESOLVED'` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- `p_damaged_check_all` (Checkbox เลือกทั้งหมดหัวตาราง): สถานะการเลือกบนหน้าจอ

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `EQUIPMENT`
- `ITEM`
- `DAMAGE_REPORT`
- `USER`
- `STUDENT`
