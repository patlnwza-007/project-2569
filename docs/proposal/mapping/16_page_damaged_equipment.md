# หน้าที่ 16: ครุภัณฑ์เสียหายและการจัดการแจ้งซ่อม (`page-damaged-equipment.html`)
**บทบาทผู้ใช้งาน:** เจ้าหน้าที่พัสดุ (`staff`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `DAMAGE_REPORT`, `EQUIPMENT`, `DURABLE_MATERIAL`, `USER`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### แท็บที่ 1: ครุภัณฑ์เสียหายในคลัง (Damaged Units in Warehouse)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **ยอดสรุปครุภัณฑ์เสียหายในคลัง** | `p_damaged_equipment_summary` | `SELECT` | `EQUIPMENT` | `EQUIPMENT.base_status = 'DAMAGED'` | นับจำนวนครุภัณฑ์ที่ถูกระงับการยืมเนื่องจากชำรุด |
| 2 | **รายการครุภัณฑ์ที่เสียหาย** (ชื่อ, เลขครุภัณฑ์, ที่ตั้ง) | `p_damaged_equipment_rows` | `SELECT` | `EQUIPMENT` | `.name`, `.asset_tag`, `.location` | แสดงรายชิ้นที่ขึ้นสถานะชำรุด |
| 3 | **ปุ่ม "🛠️ ส่งซ่อม"** | `p_damaged_equipment_setStatus` | `UPDATE` | `EQUIPMENT` | `EQUIPMENT.base_status = 'MAINTENANCE'` | เปลี่ยนสถานะครุภัณฑ์เป็นอยู่ระหว่างการซ่อมบำรุง |
| 4 | **ปุ่ม "✅ ซ่อมเสร็จแล้ว"** | `p_damaged_equipment_setStatus` | `UPDATE` | `EQUIPMENT` | `EQUIPMENT.base_status = 'AVAILABLE'` | นำครุภัณฑ์กลับเข้าสู่สถานะพร้อมให้ยืม และปรับยอดคงเหลือ |

---

### แท็บที่ 2: รายการแจ้งชำรุดจากนักศึกษา (Damage Reports)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 5 | **ยอดสรุปเรื่องแจ้งซ่อมค้างดำเนินการ** | `p_damaged_reports_summary` | `SELECT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.status != 'RESOLVED'` | นับคำขอแจ้งชำรุดที่ยังปิดงานไม่เสร็จ |
| 6 | **รายการแจ้งชำรุด** (ผู้แจ้ง, สถานที่พบ, อาการ, รูป) | `p_damaged_reports_rows` | `SELECT` | `DAMAGE_REPORT`, `USER`, `EQUIPMENT` | `user_id`, `symptom`, `location`, `photo`, `created_at` | ดึงข้อมูลใบแจ้งชำรุดและรูปถ่ายหลักฐาน |
| 7 | **ป้ายสถานะงานซ่อม** | - | `SELECT` | `DAMAGE_REPORT` | `DAMAGE_REPORT.status` | 3 สถานะตาม ERD: `PENDING`, `IN_PROGRESS`, `RESOLVED` |
| 8 | **ปุ่ม "🛠️ รับเรื่อง/ส่งช่าง"** | `p_damaged_equipment_actionReport` | `UPDATE` | `DAMAGE_REPORT` | `DAMAGE_REPORT.status = 'IN_PROGRESS'` | อัปเดตสถานะเป็นกำลังดำเนินการซ่อม |
| 9 | **ปุ่ม "✅ ปิดงานซ่อม"** | `p_damaged_equipment_actionReport` | `UPDATE` | `DAMAGE_REPORT` | `DAMAGE_REPORT.status = 'RESOLVED'` | อัปเดตสถานะเป็นซ่อมเสร็จสิ้น |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **สถานะ 3 สถานะของ `DAMAGE_REPORT`:** สอดคล้องตาม ERD 100% (`PENDING`, `IN_PROGRESS`, `RESOLVED`)
- ✅ **สถานะ `base_status` ของ `EQUIPMENT`:** เปลี่ยนสถานะครุภัณฑ์ระหว่าง `AVAILABLE`, `DAMAGED`, `MAINTENANCE` ถูกต้อง
- ✅ **เชื่อมโยง `user_id`, `symptom` และ `location`:** รองรับทั้งฟิลด์ `user_id` และดึง `symptom` มาแสดงผลตรงตาม ERD
