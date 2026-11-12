# Field Mapping: `page-return-list.html` (รับคืนสิ่งของหน้าเคาน์เตอร์)

> **หน้าจอ:** เคาน์เตอร์ตรวจรับคืนพัสดุ ตรวจสภาพจริง คำนวณค่าปรับเกินกำหนด และตั้งยอดชดใช้สูญหาย  
> **ไฟล์ต้นทาง:** `pages/page-return-list.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-18, UC-36  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **การค้นหาและแท็บตัวกรอง** | | | |
| ค้นหาคำขอ/ชื่อ นศ./รหัสครุภัณฑ์ | Input (Search) | `BORROW_REQUEST.id`, `USER.name`, `STUDENT.student_id`, `EQUIPMENT.asset_tag` | ค้นหาข้อมูลที่นำมาคืน |
| แท็บกรองสถานะ | Tabs | `RETURN_REQUEST.status`, `BORROW_REQUEST.status` | ทั้งหมด / รอตรวจรับคืน / เกินกำหนด / คืนบางส่วน |
| **ข้อมูลคำขอและผู้ส่งคืน** | | | |
| เลขที่คำขอยืม | Text | `BORROW_REQUEST.id` | รหัสคำขอ |
| ชื่อนักศึกษา | Text | `USER.name` | ดึงชื่อผู้ยืม |
| รูปถ่ายหลักฐานตอนส่งคืน | Image | `RETURN_REQUEST.return_photo` | รูปที่ นศ. ถ่ายส่งมาตอนแจ้งคืน |
| หมายเหตุการส่งคืนที่ นศ. แจ้ง | Text | `RETURN_REQUEST.note` | ข้อความที่ผู้ยืมระบุ |
| **การตรวจรับสภาพจริงรายชิ้น (Smart Pre-check)** | | | |
| Checkbox เลือกรับคืนชิ้นนี้ | Checkbox | ระบุแถวใน `RETURN_ITEM` | ติ๊กนำร่องให้อัตโนมัติตามที่ นศ. แจ้งคืนมา |
| ข้อมูลสิ่งของและรหัสชิ้น | Text / Badge | `ITEM.name`, `EQUIPMENT.asset_tag`, `ITEM.unit` | ข้อมูลสิ่งของ |
| กำหนดส่งคืนเดิม | Date | `BORROW_ITEM.due_date` | ใช้วันนี้เทียบเพื่อคำนวณค่าปรับ |
| รูปถ่ายสภาพก่อนยืม (เทียบสภาพ) | Image | `BORROW_ITEM.initial_photo` | รูปถ่ายตอนรับของ |
| ตัวเลือกผลตรวจสภาพจริง | Radio / Select | `RETURN_ITEM.condition_status` | **ปกติ (NORMAL):** คืนสต็อกเข้าคลัง, ครุภัณฑ์กลับเป็น `AVAILABLE`<br>**ชำรุด (DAMAGED):** ครุภัณฑ์เปลี่ยนเป็น `DAMAGED` ไม่คืนสต็อก<br>**สูญหาย (LOST):** ครุภัณฑ์เปลี่ยนเป็น `LOST` (ตัดสต็อกรวม) |
| **การคำนวณค่าปรับและยอดชดใช้** | | | |
| ค่าปรับเกินกำหนดคำนวณอัตโนมัติ | Text | `RETURN_ITEM.fine` | คำนวณจาก `max(0, วันที่คืน − BORROW_ITEM.due_date) × fine_rate_per_day × qty_returned` |
| ยอดค่าปรับที่เรียกเก็บจริง | Input (Number) | `RETURN_REQUEST.custom_fine` | ค่าเริ่มต้นคือผลรวม `fine` เจ้าหน้าที่สามารถปรับลดหย่อนได้ |
| เหตุผลการปรับ/ลดหย่อนค่าปรับ | Input (Text) | `RETURN_REQUEST.fine_reason` | ระบุเหตุผลหากมีการปรับลดค่าปรับ |
| ปุ่มสลับสถานะชำระค่าปรับ | Toggle / Checkbox | `RETURN_REQUEST.fine_paid` | บันทึกว่าชำระแล้ว (`true`) หรือค้างชำระ (`false`) |
| ยอดชดใช้กรณีสูญหาย | Input (Number) | `RETURN_ITEM.lost_compensation` | ค่าเริ่มต้นจาก `ITEM.purchase_price` แก้ไขได้ |
| ปุ่มสลับสถานะชำระค่าชดใช้ | Toggle / Checkbox | `RETURN_ITEM.lost_paid` | บันทึกว่าชำระค่าชดใช้แล้วหรือไม่ |
| **การยืนยันรับคืน** | | | |
| ปุ่ม `[ ✓ ยืนยันการรับคืน ]` | Button | บันทึกตรวจรับคืน | - ปรับสถานะใบแจ้งคืน: `RETURN_REQUEST.status = 'RETURNED'`<br>- บันทึกผู้ตรวจ: `RETURN_REQUEST.inspected_by = STAFF.user_id`<br>- บันทึกเวลาคืน: `RETURN_REQUEST.returned_at = NOW()`<br>- อัปเดตสถานะคำขอหลัก: หากคืนครบทุกชิ้นแล้ว `BORROW_REQUEST.status = 'RETURNED'` หากยังไม่ครบเป็น `'BORROWING'` (คืนบางส่วน) |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
1. **`p_rl_search` (ช่องค้นหาบนหัวตาราง):** Client-side filter
2. **สรุปข้อความ "คืนแล้ว X จาก Y ชิ้น":** คำนวณจากผลรวมจำนวน `RETURN_ITEM.qty_returned` เทียบกับ `BORROW_ITEM.qty` ไม่ได้เก็บเป็นฟิลด์ข้อความในฐานข้อมูล

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `RETURN_REQUEST`
- `RETURN_ITEM`
- `BORROW_REQUEST`
- `BORROW_ITEM`
- `ITEM`
- `DURABLE_MATERIAL`
- `EQUIPMENT`
- `USER`
- `STAFF`
