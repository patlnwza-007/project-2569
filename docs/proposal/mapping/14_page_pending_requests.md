# หน้าที่ 14: ตรวจเช็คและพิจารณาอนุมัติคำขอยืม (`page-pending-requests.html`)
**บทบาทผู้ใช้งาน:** เจ้าหน้าที่พัสดุ (`staff`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `BORROW_REQUEST`, `BORROW_ITEM`, `EQUIPMENT`, `DURABLE_MATERIAL`, `MATERIAL`, `USER`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: รายการคำขอรออนุมัติ (Checklist & Details)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **เลขที่คำขอและข้อมูลผู้ยืม** | - | `SELECT` | `BORROW_REQUEST`, `USER` | `BORROW_REQUEST.id`, `USER.name`, `USER.phone` | แสดงเลขที่คำขอ พร้อมชื่อและเบอร์โทรศัพท์ของนักศึกษา |
| 2 | **รายการสิ่งของในคำขอ (Checklist)** | `p_pr_chk_[rid]_[idx]` | `SELECT` | `BORROW_ITEM`, `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.name`, `.image`, `.unit`, `asset_tag`, `qty` | เจ้าหน้าที่ตรวจนับของจริงบนโต๊ะ และติ๊กยืนยันรายชิ้น |
| 3 | **ปุ่มดูรูปถ่ายสภาพเดิม/ตำหนิ (ณ จุดรับของ)** | - | `SELECT` | `BORROW_ITEM`, `BORROW_REQUEST` | `BORROW_ITEM.initial_photo`, `BORROW_REQUEST.pickup_photo` | เปิดดูภาพถ่ายหลักฐานที่นักศึกษาถ่ายไว้เพื่อตรวจสอบร่วมกัน |
| 4 | **วัตถุประสงค์การใช้งานและวันที่เริ่มใช้** | - | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.reason`, `BORROW_REQUEST.use_date` | เหตุผลความจำเป็นในการยืม |
| 5 | **กล่องขอยืมระยะยาวเป็นกรณีพิเศษ** | `appr_due_[rid]` | `SELECT` / `UPDATE` | `BORROW_REQUEST` | `BORROW_REQUEST.is_special`, `BORROW_REQUEST.due_date` | เจ้าหน้าที่สามารถปรับลดหรือระบุวันกำหนดส่งคืนได้ตามความเหมาะสม |

---

### ส่วนที่ 2: ปุ่มดำเนินการ (Approval & Rejection)
| ลำดับ | ปุ่มกดบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ผลลัพธ์ในฐานข้อมูล |
| :---: | :--- | :---: | :--- | :--- |
| 6 | **ปุ่ม "✕ ปฏิเสธคำขอ"** | `UPDATE` | `BORROW_REQUEST` | บันทึก `status = 'REJECTED'`, `approved_by = [เจ้าหน้าที่]`, `reject_reason = [เหตุผล]` |
| 7 | **ปุ่ม "✓ ตรวจของครบแล้ว — ปล่อยของ"** | `UPDATE` | `BORROW_REQUEST`, `BORROW_ITEM`, `EQUIPMENT`, `DURABLE_MATERIAL`, `MATERIAL` | 1. บันทึก `approved_by = [เจ้าหน้าที่]`, `approved_at = NOW()`<br>2. หากมีครุภัณฑ์/วัสดุคงทน ปรับ `status = 'BORROWING'` (หากมีเฉพาะวัสดุสิ้นเปลือง ปรับ `status = 'ISSUED'`)<br>3. กำหนดวันคืน `due_date`<br>4. ตัดยอดสต็อก `qty_available` และเปลี่ยนสถานะครุภัณฑ์เป็น `BORROWED` |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **บันทึกผู้อนุมัติ (`approved_by`):** เพิ่มการบันทึกรหัสเจ้าหน้าที่ลงใน `BORROW_REQUEST.approved_by` ตาม ERD
- ✅ **แยกสถานะคำขออัตโนมัติ:** หากเป็นคำขอยืมครุภัณฑ์/วัสดุคงทน สถานะจะเปลี่ยนเป็น `BORROWING` หากเป็นวัสดุสิ้นเปลืองล้วน สถานะจะเปลี่ยนเป็น `ISSUED` (เบิกสำเร็จ)
- ✅ **เชื่อมโยง `pickup_photo`:** บันทึกรูปถ่ายรับของลงใน `BORROW_REQUEST.pickup_photo`
- ✅ **บันทึกเหตุผลการปฏิเสธ (`reject_reason`):** เก็บข้อความปฏิเสธลง `BORROW_REQUEST.reject_reason`
