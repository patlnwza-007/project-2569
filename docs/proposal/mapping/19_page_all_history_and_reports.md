# หน้าที่ 19: ประวัติการทำรายการทั้งระบบและส่งออกรายงาน (`page-all-history.html` & `page-report-export.html`)
**บทบาทผู้ใช้งาน:** เจ้าหน้าที่พัสดุ (`staff`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `BORROW_REQUEST`, `BORROW_ITEM`, `RETURN_REQUEST`, `DAMAGE_REPORT`, `SUGGESTION`, `EQUIPMENT`, `DURABLE_MATERIAL`, `MATERIAL`, `USER`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: ประวัติการยืม-คืนทั้งระบบ (`page-all-history.html`)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **ค้นหาชื่อ/รหัสนักศึกษา** | `p_all_history_q` | `SELECT` | `USER`, `BORROW_REQUEST` | `USER.name`, `USER.id`, `BORROW_REQUEST.user_id` | ค้นหาประวัติของนักศึกษาทุกคน |
| 2 | **ช่วงวันที่เริ่มต้น - สิ้นสุด** | `p_all_history_from`, `to` | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.created_at` | กรองตามช่วงวันที่ส่งคำขอ |
| 3 | **ตารางประวัติคำขอทั้งระบบ** | `p_all_history_rows` | `SELECT` | `BORROW_REQUEST`, `BORROW_ITEM` | `.id`, `user_id`, `.created_at`, `.status` | แสดงรายการคำขอทุกสถานะในระบบ |

---

### ส่วนที่ 2: การออกรายงานสรุปและส่งออกข้อมูล (`page-report-export.html`)
| ลำดับ | รูปแบบรายงาน (Report Types) | การทำงาน (CRUD) | ตาราง (Table) | ข้อมูลที่นำมาประมวลผล |
| :---: | :--- | :---: | :--- | :--- |
| 4 | **สรุปสถานะการยืม-คืนรายเดือน** | `SELECT` | `BORROW_REQUEST`, `BORROW_ITEM` | ยอดคำขอและจำนวนสิ่งของแยกตาม 8 สถานะใน ERD |
| 5 | **รายงานของชำรุด** | `SELECT` | `DAMAGE_REPORT`, `EQUIPMENT` | ข้อมูลจาก `DAMAGE_REPORT` และครุภัณฑ์ที่ขึ้นสถานะ `DAMAGED` |
| 6 | **รายงานคนค้างส่ง (เกินกำหนด)** | `SELECT` | `BORROW_REQUEST`, `USER`, `EQUIPMENT` | คำขอที่ `status IN ('BORROWING', 'RETURN_PENDING')` และ `due_date < วันปัจจุบัน` พร้อมยอดค่าปรับ |
| 7 | **รายงานคำเสนอแนะสิ่งของ** | `SELECT` | `SUGGESTION`, `USER` | ข้อมูลรายการและเหตุผลความต้องการจากนักศึกษา |
| 8 | **ส่งออกข้อมูลคลังทั้งหมด (CSV)** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | ทะเบียนพัสดุและครุภัณฑ์พร้อมยอดคงเหลือและสถานะ |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **เชื่อมโยง `user_id` ทั่วถึง:** รองรับทั้ง `user_id` และ `student_id`
- ✅ **ครอบคลุม 8 สถานะของคำขอยืม:** คัดกรองและประมวลผลคำขอตามสถานะใน ERD
- ✅ **รายงานเกินกำหนดครอบคลุม `RETURN_PENDING`:** ตรวจสอบคำขอที่ค้างส่งทั้งสถานะ `BORROWING` และ `RETURN_PENDING`
