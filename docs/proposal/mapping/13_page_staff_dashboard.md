# หน้าที่ 13: แดชบอร์ดภาพรวมระบบของเจ้าหน้าที่ (`page-staff-dashboard.html`)
**บทบาทผู้ใช้งาน:** เจ้าหน้าที่พัสดุ (`staff`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `BORROW_REQUEST`, `USER`, `EQUIPMENT`, `DURABLE_MATERIAL`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: แบนเนอร์งานด่วนและการ์ดสรุป KPI ภาพรวม
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **แบนเนอร์แจ้งเตือนงานด่วน** (คำขอรออนุมัติ, รายการรอรับคืน, รายการเกินกำหนด) | `p_staff_dashboard_action_banner` | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.status`, `BORROW_REQUEST.due_date` | คำนวณยอดรายการค้างที่ต้องเร่งดำเนินการเพื่อแจ้งเตือนเจ้าหน้าที่ |
| 2 | **การ์ด KPI: คำขอรออนุมัติ** | `p_staff_dashboard_kpis` | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.status = 'PENDING'` | จำนวนคำขอยืมที่รอเจ้าหน้าที่พิจารณา |
| 3 | **การ์ด KPI: กำลังยืมอยู่ (รอส่งคืน)** | - | `SELECT` | `BORROW_REQUEST` | `status IN ('BORROWING', 'RETURN_PENDING')` | จำนวนคำขอที่อยู่ระหว่างการยืมใช้งาน |
| 4 | **การ์ด KPI: เกินกำหนดคืน** | - | `SELECT` | `BORROW_REQUEST` | `due_date < NOW()` | คำขอที่ผู้ยืมยังไม่นำของมาคืนและพ้นกำหนดส่งคืน |
| 5 | **การ์ด KPI: คืน/เบิกสำเร็จแล้ว** | - | `SELECT` | `BORROW_REQUEST` | `status IN ('RETURNED', 'ISSUED')` | ยอดคำขอที่สิ้นสุดกระบวนการแล้ว |

---

### ส่วนที่ 2: กราฟสถิติสถานะและสัดส่วนผู้ใช้งาน
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 6 | **กราฟแท่งแจกแจงสถานะคำขอทั้งระบบ** | `p_staff_dashboard_bar-chart` | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.status` | แจกแจงครบทั้ง 8 สถานะตาม ERD: `PENDING`, `BORROWING`, `RETURN_PENDING`, `ISSUED`, `RETURNED`, `REJECTED`, `CANCELLED`, `EXPIRED` พร้อมยอดเกินกำหนด |
| 7 | **แผนภูมิวงกลมสัดส่วนสถานะนักศึกษา** | `p_staff_dashboard_donut` | `SELECT` | `USER` | `USER.role = 'STUDENT'`, `USER.blocked` | สัดส่วนนักศึกษาสถานะปกติ เทียบกับนักศึกษาที่ถูกระงับสิทธิ์ |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **สถานะ 8 สถานะตาม ERD:** แสดงผลแจกแจงบนกราฟแท่งครบทุกสถานะในระบบ
- ✅ **เชื่อมโยงตาราง `USER`:** รองรับการดึงข้อมูลนักศึกษาจากตาราง `USER` โดยตรง (`role = 'STUDENT'`)
- ✅ **คำนวณวันเกินกำหนดแบบไดนามิก:** ตรวจสอบ `daysLeft(r.due_date) < 0` ร่วมกับสถานะ `BORROWING` และ `RETURN_PENDING`
