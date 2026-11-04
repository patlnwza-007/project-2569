# หน้าที่ 12: แจ้งอุปกรณ์ชำรุด (`page-report-damage.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา / ผู้ใช้งานทั่วไป (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `DAMAGE_REPORT`, `EQUIPMENT`, `DURABLE_MATERIAL`, `USER`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: การค้นหาและระบุสิ่งของที่ชำรุด (Search & OCR)
| ลำดับ | ชื่อช่อง / ช่องกรอกข้อมูล (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **สแกนข้อความ/รหัสจากรูป (OCR)** | `p_report_damage_ocr_input` | `SELECT` | `EQUIPMENT` | `EQUIPMENT.asset_tag` | สแกนหาข้อความรหัสครุภัณฑ์จากภาพถ่าย เพื่อระบุสิ่งของอัตโนมัติ |
| 2 | **ช่องค้นหาชื่อสิ่งของ / เลขครุภัณฑ์ / ห้อง** | `p_report_damage_search_q` | `SELECT` | `EQUIPMENT`, `DURABLE_MATERIAL` | `.name`, `asset_tag`, `location` | กรองรายการเพื่อเลือกสิ่งของที่ต้องการแจ้ง |
| 3 | **ดรอปดาวน์เลือกสิ่งของที่พบชำรุด** | `p_report_damage_select_target` | `SELECT` | `EQUIPMENT`, `DURABLE_MATERIAL` | `EQUIPMENT.id`, `DURABLE_MATERIAL.id` | เลือกรหัสสิ่งของเป้าหมาย |
| 4 | **ตัวเลือก: ไม่เห็นเลขครุภัณฑ์ (ป้ายหลุดหาย)** | `p_report_damage_no_tag`, `p_report_damage_other_item_name` | `Client State` / `INSERT` | `DAMAGE_REPORT` | - | เมื่อติ๊กเลือก ระบบจะแสดงช่องพิมพ์ระบุชื่อสิ่งของ/อุปกรณ์ขึ้นมาให้กรอกได้ทันที โดยไม่ต้องเลือก "อื่นๆ" ซ้ำซ้อน |
| 5 | **การ์ดแสดงข้อมูลที่ตั้งเดิมและผู้ถือครองปัจจุบัน** | `p_report_damage_info_card` | `SELECT` | `EQUIPMENT`, `BORROW_ITEM`, `USER` | `.location`, `current_location`, `user_id` | แสดงที่ตั้งเดิม ที่ตั้งล่าสุดที่แจ้งย้าย และผู้ถือครองปัจจุบันเพื่อความโปร่งใส |

---

### ส่วนที่ 2: ฟอร์มระบุสถานที่และอาการชำรุด
| ลำดับ | ชื่อช่อง / ช่องกรอกข้อมูล (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 6 | **สถานที่พบความชำรุด** <span class="text-red-500">*</span> | `p_report_damage_loc_select` | `INSERT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.location` | ระบุสถานที่พบ เช่น ห้องคลัง หรือห้องเรียน |
| 7 | **อาการชำรุดที่พบ** <span class="text-red-500">*</span> | `p_report_damage_symptom_select` | `INSERT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.symptom` | เช่น เปิดไม่ติด, สายไฟขาด, หน้าจอไม่ติด |
| 8 | **รายละเอียดอาการเพิ่มเติม** | `p_report_damage_symptom_detail` | `INSERT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.symptom` | คำอธิบายอาการความเสียหายอย่างละเอียด (นำไปรวมกับ symptom) |
| 9 | **รูปถ่ายหลักฐานสภาพความเสียหาย** | `p_report_damage_photo_input` | `INSERT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.photo` | แนบภาพถ่ายจุดที่ชำรุด |
| 10 | **รหัสผู้แจ้ง (บันทึกอัตโนมัติ)** | - | `INSERT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.user_id` | รหัสผู้ใช้งานปัจจุบัน (`user_id = S001`) |
| 11 | **รหัสครุภัณฑ์ (บันทึกอัตโนมัติ)** | - | `INSERT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.equipment_id` | รหัสครุภัณฑ์ที่พบชำรุด |
| 12 | **สถานะเริ่มต้น (บันทึกอัตโนมัติ)** | - | `INSERT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.status` | ค่าเริ่มต้นเมื่อส่งคือ `'PENDING'` |
| 13 | **วันเวลาที่ส่งแจ้ง (บันทึกอัตโนมัติ)** | - | `INSERT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.created_at` | วันและเวลาที่บันทึก |

---

### ส่วนที่ 3: ประวัติการแจ้งชำรุด
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 14 | **รายการประวัติแจ้งชำรุดของผู้ใช้** | `p_report_damage_rows` | `SELECT` | `DAMAGE_REPORT` | `id`, `symptom`, `location`, `photo`, `created_at` | กรองเฉพาะรายการที่ส่งโดยผู้ใช้งานปัจจุบัน |
| 15 | **ป้ายสถานะการดำเนินงาน (Badge)** | - | `SELECT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.status` | แสดง 3 สถานะตาม ERD:<br>1. `PENDING` (รอเจ้าหน้าที่ตรวจสอบ)<br>2. `IN_PROGRESS` (กำลังดำเนินการซ่อม)<br>3. `RESOLVED` (ซ่อมเสร็จสิ้น) |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **เชื่อมโยง `user_id` และ `equipment_id`:** บันทึกข้อมูลตรงกับตาราง `DAMAGE_REPORT` ใน ERD
- ✅ **บันทึก `symptom`, `location` และ `photo`:** จัดเก็บรายละเอียดอาการ สถานที่พบ และภาพถ่ายความเสียหายอย่างสมบูรณ์ตรงตาม ERD
- ✅ **สถานะ 3 สถานะตรงกับ ERD 100%:** `PENDING`, `IN_PROGRESS`, `RESOLVED`
