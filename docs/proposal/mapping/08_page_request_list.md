# Field Mapping: `page-request-list.html` (หน้าหลัก / สถานะคำขอของฉัน)

> **หน้าจอ:** หน้าหลักของนักศึกษา แสดงสถานะคำขอปัจจุบัน สิ่งของที่กำลังยืม และแจ้งย้ายที่ตั้ง  
> **ไฟล์ต้นทาง:** `pages/page-request-list.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student)  
> **Use Case:** UC-07, UC-08, UC-09, UC-10  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **การ์ดคำขอยืม (Request Card)** | | | |
| เลขที่คำขอ | Text | `BORROW_REQUEST.id` | เช่น คำขอ #105 |
| วันที่ส่งคำขอ | Datetime | `BORROW_REQUEST.created_at` | วันเวลาที่ส่งคำขอ |
| สถานะคำขอ | Badge | `BORROW_REQUEST.status` | `PENDING`, `BORROWING`, `RETURN_PENDING`, `ISSUED`, `REJECTED`, `CANCELLED` |
| ป้ายขอยืมกรณีพิเศษ | Badge | `BORROW_REQUEST.is_special` | แสดงป้าย "ยืมกรณีพิเศษ" หาก `is_special = true` |
| เหตุผลที่ไม่อนุมัติ (กรณี REJECTED) | Text / Alert | `BORROW_REQUEST.reject_reason` | แสดงข้อความชี้แจงจากเจ้าหน้าที่ |
| **รายการสิ่งของภายในคำขอ** | | | |
| ชื่อและประเภทสิ่งของ | Text / Badge | `ITEM.name`, `ITEM.item_type`, `ITEM.unit` | ข้อมูลสิ่งของ |
| รหัสครุภัณฑ์ประจำชิ้น | Text (Badge) | `EQUIPMENT.asset_tag` | รหัสเฉพาะชิ้น |
| จำนวนที่ยืม | Text | `BORROW_ITEM.qty` | จำนวนของรายการนี้ |
| วันครบกำหนดคืนรายชิ้น | Date / Badge | `BORROW_ITEM.due_date` | วันที่ต้องส่งคืน คำนวณจากวันปล่อยของ + `max_borrow_days` หรือ `custom_due_date` |
| ปุ่มแจ้งย้ายที่ตั้งชั่วคราว | Button / Modal | `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at` | บันทึกสถานที่ใช้งานใหม่และเวลาที่แจ้งย้าย |
| **การคืนและค่าปรับ** | | | |
| ปุ่มแจ้งส่งคืน `[ ↩️ แจ้งคืนสิ่งของ ]` | Button | Navigation | นำทางไปหน้า `page-notify-return.html` พร้อมส่ง `requestId` |
| ยอดค่าปรับเกินกำหนด / ยอดชดใช้ | Text / Alert | `RETURN_REQUEST.custom_fine`, `RETURN_REQUEST.fine_paid`, `RETURN_ITEM.lost_compensation`, `RETURN_ITEM.lost_paid` | แสดงยอดที่ต้องชำระและสถานะการจ่ายเงิน |
| **แถบแจ้งเตือนสถานะคิว (Queue Summary Card)** | | | |
| ลำดับคิวที่รออยู่ | Summary Card | `QUEUE.id`, `QUEUE.status`, `ITEM.name` | แสดงคิวที่ตนเองจองไว้และกำลังรอเรียก |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
1. **`p_relocate_input` (ที่ตั้งใหม่ใน Modal แจ้งย้าย):** ข้อมูลชั่วคราวก่อนกดยืนยันบันทึกลง `BORROW_ITEM.current_location`
2. **ตัวนับถอยหลัง / วันที่เหลือ (Calculated UI State):** คำนวณจาก `BORROW_ITEM.due_date - TODAY` ไม่ได้เก็บเป็นฟิลด์ในตาราง

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `BORROW_REQUEST`
- `BORROW_ITEM`
- `ITEM`
- `EQUIPMENT`
- `DURABLE_MATERIAL`
- `RETURN_REQUEST`
- `RETURN_ITEM`
- `QUEUE`
