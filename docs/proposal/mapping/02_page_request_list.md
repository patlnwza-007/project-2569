# หน้าที่ 2: หน้าหลักนักศึกษา (`page-request-list.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `USER`, `BORROW_REQUEST`, `BORROW_ITEM`, `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT`, `RETURN_REQUEST`, `RETURN_ITEM`, `QUEUE`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: ส่วนหัว แถบแจ้งเตือน และการ์ดสรุป 5 กล่อง
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **สวัสดี, [ชื่อนักศึกษา]** | `p_request_list_student-name` | `SELECT` | `USER` | `USER.name` | แสดงชื่อนักศึกษาที่ล็อกอินอยู่ |
| 2 | **แจ้งเตือนเร่งด่วน (ถึงคิวจอง)** | `p_request_list_alert` | `SELECT` | `QUEUE`, `DURABLE_MATERIAL`, `EQUIPMENT` | `QUEUE.status`, `DURABLE_MATERIAL.qty_available`, `EQUIPMENT.base_status` | แจ้งเตือนเมื่อของว่างและถึงคิว (`status = 'NOTIFIED'`) |
| 3 | **การ์ดสรุป: รอตรวจของ / กำลังยืม / เกินกำหนด / คืนสำเร็จ** | `p_request_list_summary` | `SELECT (COUNT)` | `BORROW_REQUEST` | `COUNT(BORROW_REQUEST.id)` แยกตาม `status` และ `due_date` | คำนวณจำนวนใบคำขอของ `user_id` ปัจจุบัน |
| 4 | **การ์ดสรุป: คิวที่จอง** | `p_request_list_summary` | `SELECT (COUNT)` | `QUEUE` | `COUNT(QUEUE.id)` | นับจำนวนคิวของ `user_id` ปัจจุบัน |

---

### ส่วนที่ 2: การ์ดรายการที่ต้องดำเนินการ (`PENDING`, `BORROWING`, `RETURN_PENDING`)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :---: | :--- | :--- | :--- |
| 5 | **ป้ายสถานะคำขอ** (รอตรวจของ / กำลังยืม / รอตรวจรับคืน) | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.status` | แสดงสถานะใบคำขอ + แถบ Step Progress |
| 6 | **ป้ายประเภทการยืม** (ครุภัณฑ์ / วัสดุคงทน / วัสดุเบิกใช้) | `SELECT (Derived)` | `BORROW_ITEM` | `BORROW_ITEM.equipment_id`, `durable_material_id`, `material_id` | พิจารณาจาก FK ที่ไม่เป็น `NULL` ใน `BORROW_ITEM` |
| 7 | **เลขที่คำขอ (`คำขอ #105`)** | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.id` | รหัสใบคำขอยืม (`PK`) |
| 8 | **เหตุผลการยืม** | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.reason` | เหตุผลที่นักศึกษากรอกตอนขอยืม |
| 9 | **วันที่ส่งคำขอ** | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.created_at` | วันเวลาที่สร้างใบคำขอ |
| 10 | **กำหนดคืน & จำนวนวันคงเหลือ/เกินกำหนด** | `SELECT` + `Derived` | `BORROW_REQUEST` | `BORROW_REQUEST.due_date` | สูตร: `วันปัจจุบัน - due_date` |
| 11 | **ยอดค่าปรับค้างชำระ (กรณีเกินกำหนด)** | `SELECT` + `Derived` | `BORROW_REQUEST`, `BORROW_ITEM`, `RETURN_ITEM`, `DURABLE_MATERIAL`, `EQUIPMENT` | `due_date`, `qty`, `qty_returned`, `fine_rate_per_day` | สูตร: `(วันเกินกำหนด) × SUM((BORROW_ITEM.qty - SUM(RETURN_ITEM.qty_returned)) × fine_rate_per_day)` |
| 12 | **แถบแจ้งเตือนทยอยคืนบางส่วน** (`ทยอยคืนแล้ว X/Y รายการ`) | `SELECT` + `Derived` | `BORROW_ITEM`, `RETURN_REQUEST`, `RETURN_ITEM` | `BORROW_ITEM.id`, `BORROW_ITEM.qty`, `RETURN_ITEM.qty_returned` | สูตร: นับรายการที่ `SUM(RETURN_ITEM.qty_returned) >= BORROW_ITEM.qty` เทียบกับ `COUNT(BORROW_ITEM.id)` ทั้งหมด |
| 13 | **รูปภาพ / ชื่อสิ่งของ / หน่วยนับ** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.image`, `.name`, `.unit` | ดึงจากตารางสิ่งของตาม FK ใน `BORROW_ITEM` |
| 14 | **รหัสครุภัณฑ์ประจำชิ้น (`🏷️ UBU-EQ-...`)** | `SELECT` | `EQUIPMENT` | `EQUIPMENT.asset_tag` | แสดงเฉพาะรายการที่เป็นครุภัณฑ์ (`equipment_id`) |
| 15 | **จำนวนที่ยืม (`จำนวน: X ชิ้น`)** | `SELECT` | `BORROW_ITEM` | `BORROW_ITEM.qty` | จำนวนที่ยืมในรายการนั้น |
| 16 | **ป้ายสถานะรายชิ้น** (กำลังยืม / รอตรวจรับคืน / คืนแล้ว) | `SELECT` | `RETURN_REQUEST`, `RETURN_ITEM` | `RETURN_REQUEST.status`, `RETURN_ITEM.qty_returned`, `condition_status` | รองรับกรณีทยอยคืนบางชิ้น (Partial Return) |
| 17 | **📍 ที่ตั้ง/ที่อยู่ปัจจุบันของครุภัณฑ์** | `SELECT` | `BORROW_ITEM` | `BORROW_ITEM.current_location` | แสดงพิกัดล่าสุดที่นักศึกษานำของไปตั้งไว้ |
| 18 | **เวลาที่อัปเดตที่ตั้งล่าสุด** | `SELECT` | `BORROW_ITEM` | `BORROW_ITEM.moved_at` | แสดงวันเวลาที่แจ้งย้ายล่าสุด |

---

### ส่วนที่ 3: ปุ่มกดและหน้าต่างแจ้งย้ายที่ตั้ง (Actions & Modal)
| ลำดับ | ปุ่ม / ช่องกรอกใน Modal | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 18 | **ปุ่ม "ยกเลิกคำขอ"** (เฉพาะสถานะ `PENDING`) | - | `UPDATE` | `BORROW_REQUEST` | `BORROW_REQUEST.status = 'CANCELLED'` | ยกเลิกคำขอที่เจ้าหน้าที่ยังไม่ได้อนุมัติ |
| 19 | **ปุ่ม "📍 แจ้งย้ายที่ตั้ง / ที่อยู่" + ช่องกรอกพิกัดใหม่** | `p_relocate_input` | `UPDATE` | `BORROW_ITEM` | `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at` | บันทึกที่ตั้งหรือที่อยู่ใหม่และเวลาที่ย้าย (`NOW()`) |

---

## ผลการตรวจสอบความสอดคล้อง (Validation)
- ✅ ลบส่วน "ประวัติการยืม-คืน" ด้านล่างของหน้าหลักออกแล้ว (ไม่ซ้ำซ้อนกับหน้า `page-history.html`)
- ✅ ทุกช่องข้อมูลและการคำนวณอ้างอิงจากตารางใน ERD ครบ 100%
