# Field Mapping: `page-staff-dashboard.html` (แดชบอร์ดภาพรวมระบบ)

> **หน้าจอ:** แดชบอร์ดสรุปตัวเลขสถิติภาพรวมและการดำเนินงานของเจ้าหน้าที่  
> **ไฟล์ต้นทาง:** `pages/page-staff-dashboard.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-16  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **การ์ดสถิติสรุปภาพรวม (KPI Stat Cards)** | | | |
| คำขอรอตรวจของ / รออนุมัติ | Stat Card | คำนวณจาก `BORROW_REQUEST` | `COUNT(BORROW_REQUEST.id)` ที่ `status = 'PENDING'` |
| รายการรอตรวจรับคืน | Stat Card | คำนวณจาก `RETURN_REQUEST` | `COUNT(RETURN_REQUEST.id)` ที่ `status = 'RETURN_PENDING'` |
| สิ่งของที่กำลังถูกยืมอยู่ | Stat Card | คำนวณจาก `BORROW_REQUEST` | `COUNT(BORROW_REQUEST.id)` ที่ `status = 'BORROWING'` |
| รายการที่เกินกำหนดคืน (Overdue) | Stat Card | คำนวณจาก `BORROW_ITEM` | `COUNT(BORROW_ITEM.id)` ที่อยู่ในคำขอ `BORROWING` และ `due_date < CURRENT_DATE` |
| ครุภัณฑ์เสียหาย / แจ้งซ่อม | Stat Card | คำนวณจาก `EQUIPMENT` + `DAMAGE_REPORT` | `COUNT(EQUIPMENT)` ที่ `status = 'DAMAGED'` + `COUNT(DAMAGE_REPORT)` ที่ `status = 'PENDING'` |
| คำเสนอแนะรอพิจารณา | Stat Card | คำนวณจาก `SUGGESTION` | `COUNT(SUGGESTION.id)` ที่ `status = 'SUBMITTED'` |
| **ตารางคำขอยืมล่าสุดที่รอตรวจสอบ** | | | |
| เลขที่คำขอ | Text | `BORROW_REQUEST.id` | รหัสคำขอ เช่น #105 |
| ผู้ยืม (นักศึกษา) | Text | `USER.name` | ดึงชื่อผู้ยืมผ่าน `BORROW_REQUEST.user_id -> USER.name` |
| รายการสิ่งของ | Text | `ITEM.name`, `BORROW_ITEM.qty`, `ITEM.unit` | รายการพัสดุในคำขอ |
| วันที่ส่งคำขอ | Datetime | `BORROW_REQUEST.created_at` | เวลาที่ส่งคำขอ |
| สถานะคำขอ | Badge | `BORROW_REQUEST.status` | แสดงสถานะ `PENDING` |
| ปุ่มจัดการ `[ ตรวจของ → ]` | Button | Navigation | ลิงก์ไปยังหน้า `page-pending-requests.html` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- กราฟสถิติภาพรวมรายสัปดาห์/รายเดือน: ประมวลผลจาก `COUNT(BORROW_REQUEST)` และ `RETURN_REQUEST` ตามช่วงเวลา

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `BORROW_REQUEST`
- `BORROW_ITEM`
- `RETURN_REQUEST`
- `EQUIPMENT`
- `DAMAGE_REPORT`
- `SUGGESTION`
- `USER`
- `ITEM`
