# Field Mapping: `page-pending-requests.html` (คำขอรออนุมัติ / ตรวจปล่อยของหน้าเคาน์เตอร์)

> **หน้าจอ:** ตรวจนับสิ่งของจริงหน้าเคาน์เตอร์ ติ๊กตัดของขาด ปรับวันคืนพิเศษ และกดปล่อยของในคลิกเดียว  
> **ไฟล์ต้นทาง:** `pages/page-pending-requests.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-17  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **ข้อมูลคำขอยืม** | | | |
| เลขที่คำขอ | Text | `BORROW_REQUEST.id` | รหัสคำขอที่รอตรวจ |
| วันที่ส่งคำขอ | Datetime | `BORROW_REQUEST.created_at` | เวลาที่ส่งคำขอเข้ามา |
| ป้ายขอยืมกรณีพิเศษ | Badge | `BORROW_REQUEST.is_special` | แสดงหากผู้ยืมระบุ `is_special = true` |
| กำหนดส่งคืนกรณีพิเศษที่ขอ | Date | `BORROW_REQUEST.custom_due_date` | วันที่นักศึกษาขอส่งคืน |
| **ข้อมูลผู้ยืม** | | | |
| ชื่อ-นามสกุลผู้ยืม | Text | `USER.name` | ดึงชื่อผู้ยืมผ่าน `BORROW_REQUEST.user_id` |
| รหัสนักศึกษา | Text | `STUDENT.student_id` | รหัส 11 หลัก |
| เบอร์โทรศัพท์ติดต่อ | Text | `STUDENT.phone` | เบอร์โทรศัพท์ 10 หลัก |
| อีเมลมหาวิทยาลัย | Text | `USER.email` | อีเมล @ubu.ac.th |
| **รายการสิ่งของที่ต้องตรวจนับ (รายชิ้น)** | | | |
| Checkbox ตรวจของจริงบนโต๊ะ | Checkbox | Logic การปล่อยของ | ค่าเริ่มต้นติ๊กถูกทุกชิ้น ชิ้นที่ของขาด/ไม่รับให้ติ๊กออก |
| ชื่อและประเภทสิ่งของ | Text / Badge | `ITEM.name`, `ITEM.item_type`, `ITEM.unit` | ข้อมูลสิ่งของ |
| รหัสประจำชิ้น (ครุภัณฑ์) | Text (Badge) | `EQUIPMENT.asset_tag` | รหัส Asset Tag ชิ้นที่ปล่อย |
| จำนวนที่ขอ | Text | `BORROW_ITEM.qty` | จำนวนของแต่ละรายการ |
| รูปถ่ายสภาพก่อนยืม (ถ้ามี) | Image / Modal | `BORROW_ITEM.initial_photo` | รูปถ่ายที่นักศึกษาแนบมา |
| ตำแหน่งจัดเก็บในคลัง | Text | `ITEM.location` | ที่ตั้งสิ่งของ เช่น ชั้นวาง A1 |
| ตรวจเช็กสต็อกคงเหลือ | Text | `MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_available`, `EQUIPMENT.status` | เช็กความพร้อมใช้งานก่อนปล่อย |
| ช่องปรับวันที่อนุญาตคืน (กรณีพิเศษ) | Input (Date) | `BORROW_REQUEST.custom_due_date` | เจ้าหน้าที่ปรับเปลี่ยนวันคืนที่อนุญาตได้ก่อนกดปล่อย |
| **การดำเนินการของเจ้าหน้าที่ (Actions)** | | | |
| ปุ่ม `[ ✓ ตรวจของครบแล้ว — ปล่อยของ ]` | Button | บันทึกอนุมัติปล่อยของ | - อนุมัติคำขอ: `BORROW_REQUEST.status = 'BORROWING'` (หรือ `'ISSUED'` หากมีเฉพาะวัสดุสิ้นเปลือง)<br>- บันทึกผู้อนุมัติ: `BORROW_REQUEST.approved_by = STAFF.user_id`<br>- บันทึกเวลาปล่อยของ: `BORROW_REQUEST.approved_at = NOW()`<br>- กำหนดวันคืนรายชิ้น: `BORROW_ITEM.due_date` = วันปล่อย + `max_borrow_days` (หรือ `custom_due_date`)<br>- ตัดสต็อก: `MATERIAL.qty_available -= qty`, `DURABLE_MATERIAL.qty_available -= qty`, `EQUIPMENT.status = 'BORROWED'` |
| ปุ่ม `[ ✕ ปฏิเสธคำขอ ]` | Button / Modal | บันทึกปฏิเสธ | - เปลี่ยนสถานะ: `BORROW_REQUEST.status = 'REJECTED'`<br>- บันทึกเหตุผล: `BORROW_REQUEST.reject_reason` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- Checkbox รายชิ้นที่ติ๊กออก (ชิ้นที่ของขาดหรือไม่รับ): ระบบจะลบแถว `BORROW_ITEM` นั้นออกจากคำขอ โดยไม่แตะต้องสต็อก

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `BORROW_REQUEST`
- `BORROW_ITEM`
- `USER`
- `STUDENT`
- `STAFF`
- `ITEM`
- `MATERIAL`
- `DURABLE_MATERIAL`
- `EQUIPMENT`
