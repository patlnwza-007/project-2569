# หน้าที่ 8: ประวัติการยืม-คืน (`page-history.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `BORROW_REQUEST`, `BORROW_ITEM`, `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT`, `REVIEW`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: ตารางประวัติการยืม-คืน
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **เลขที่คำขอ (#ID)** | `p_history_rows` | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.id` | รหัสอ้างอิงคำขอ เช่น `#101`, `#102` |
| 2 | **รายการสิ่งของที่ยืม/เบิก** | - | `SELECT` | `BORROW_ITEM`, `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.name` | รวมรายชื่อสิ่งของในคำขอนั้นคั่นด้วยเครื่องหมายจุลภาค |
| 3 | **วันที่ส่งคำขอ** | - | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.created_at` | วันที่บันทึกคำขอลงระบบ |
| 4 | **สถานะคำขอ (Badge)** | - | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.status` | แสดง 8 สถานะตาม ERD: `PENDING`, `BORROWING`, `RETURN_PENDING`, `ISSUED`, `RETURNED`, `REJECTED`, `CANCELLED`, `EXPIRED` |
| 5 | **คอลัมน์ประเมิน/ดำเนินการต่อ** | - | `SELECT` | `REVIEW`, `BORROW_ITEM` | `REVIEW.id`, `rating`, `comment` | หากสถานะเป็น `RETURNED` หรือ `ISSUED` จะแสดงลิงก์ไปรีวิว (`page-evaluation.html`) หรือหากรีวิวครบแล้วจะแสดงเครื่องหมาย ✓ |
| 6 | **กล่องแสดงสถานะไม่มีข้อมูล (Empty State)** | `p_history_empty` | `SELECT` | `BORROW_REQUEST` | - | แสดงเมื่อยังไม่เคยมีประวัติการยืมในระบบ |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการปรับปรุง
- ✅ **รองรับ `user_id` / `student_id`:** ปรับโค้ดให้ค้นหาคำขอด้วยเงื่อนไข `(r.user_id === stu || r.student_id === stu)` ให้สอดคล้องกับ ERD
- ✅ **สถานะ 8 สถานะใน ERD:** แสดงผลผ่าน `badgeHtml(r.status)` ถูกต้องครบถ้วน
- ✅ **เชื่อมโยงการประเมินกับตาราง `REVIEW`:** เชื่อมโยงผลการรีวิวรายชิ้นผ่าน `borrow_item_id` ไปยังหน้า `page-evaluation.html`
