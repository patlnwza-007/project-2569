# Field Mapping: `page-student-list.html` (รายชื่อนักศึกษา)

> **หน้าจอ:** ดูและค้นหารายชื่อนักศึกษา ข้อมูลติดต่อ และประวัติการยืม (Read-Only สำหรับเจ้าหน้าที่)  
> **ไฟล์ต้นทาง:** `pages/page-student-list.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-26  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| ช่องค้นหารหัสนักศึกษาหรือชื่อ (`p_student_list_q`) | Input (Search) | `STUDENT.student_id`, `USER.name` | ค้นหารายชื่อนักศึกษา |
| **ตารางรายชื่อนักศึกษา** | | | |
| รหัสนักศึกษา (11 หลัก) | Text | `STUDENT.student_id` | รหัสนักศึกษา |
| ชื่อ - นามสกุล | Text | `USER.name` | ชื่อ-นามสกุล |
| ข้อมูลติดต่อ (อีเมล @ubu.ac.th) | Text | `USER.email` | อีเมลมหาวิทยาลัย |
| ข้อมูลติดต่อ (เบอร์โทรศัพท์ 10 หลัก) | Text | `STUDENT.phone` | เบอร์โทรศัพท์สำหรับติดต่อติดตามของ |
| สถานะสิทธิ์การยืม | Badge | `USER.blocked`, `USER.block_reason` | แสดง "ปกติ" หรือ "ระงับสิทธิ์" พร้อมเหตุผล |
| จำนวนคำขอยืมทั้งหมด | Text | คำนวณจาก `BORROW_REQUEST` | `COUNT(BORROW_REQUEST.id)` ที่ `user_id = STUDENT.user_id` |
| จำนวนสิ่งของที่กำลังยืมค้างอยู่ | Text | คำนวณจาก `BORROW_REQUEST` | `COUNT(BORROW_REQUEST.id)` ที่ `status = 'BORROWING'` |
| ปุ่มจัดการสิทธิ์ `[ ⚙️ จัดการสิทธิ์ ]` | Button | Navigation | นำทางไปหน้า `page-student-permission.html?id=X` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- ตัวเลือกเรียงลำดับหัวตาราง (Sort by Student ID / Name): Client-side sorting

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `USER`
- `STUDENT`
- `BORROW_REQUEST`
