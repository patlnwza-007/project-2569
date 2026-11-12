# Field Mapping: `page-queue-list.html` (คิวของฉัน)

> **หน้าจอ:** หน้ารายการคิวจองพัสดุ ลำดับคิว และประมาณการวันพร้อมยืม  
> **ไฟล์ต้นทาง:** `pages/page-queue-list.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student)  
> **Use Case:** UC-10  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **การ์ดข้อมูลคิว (Queue Card)** | | | |
| ลำดับที่ในคิว | Text / Badge | คำนวณจาก `QUEUE` | ลำดับคิวนับจากแถวที่มี `joined_at` ก่อนหน้าตนเองในสิ่งของชิ้นเดียวกัน |
| ชื่อและประเภทสิ่งของ | Text / Badge | `ITEM.name`, `ITEM.item_type`, `ITEM.image` | ข้อมูลสิ่งของที่จอง |
| รหัสครุภัณฑ์ (กรณีจองระดับชิ้น) | Text (Badge) | `EQUIPMENT.asset_tag` | รหัส Asset Tag ชิ้นที่จอง (unit-level) |
| วันเวลาที่เข้าคิว | Datetime | `QUEUE.joined_at` | เวลาที่กดจองคิว |
| สถานะคิว | Badge | `QUEUE.status` | `WAITING` (รอคิว), `NOTIFIED` (ถึงคิวแล้ว), `CONFIRMED` (ยืนยันแล้ว), `EXPIRED` (หมดอายุ), `CANCELLED` (ยกเลิก) |
| **การคำนวณวันพร้อมยืม (Estimated Available Date)** | | | |
| วันที่คาดว่าจะได้ยืมคร่าวๆ | Text / Alert | คำนวณจาก `BORROW_ITEM.due_date` | คำนวณจากกำหนดส่งคืนจริงของผู้ยืมคนปัจจุบัน + สะสมตามระยะเวลายืม `max_borrow_days` ของคิวก่อนหน้า |
| ข้อความชี้แจงกำหนดคืนผู้ยืมปัจจุบัน | Text | `BORROW_ITEM.due_date`, `BORROW_REQUEST.is_special` | แสดงเหตุผล เช่น "ผู้ยืมปัจจุบันยืมกรณีพิเศษ มีกำหนดส่งคืน..." |
| **การแจ้งเตือนและการยืนยันรับสิทธิ์** | | | |
| เวลาที่ระบบแจ้งเตือนถึงคิว | Datetime | `QUEUE.notified_at` | บันทึกเวลาที่ของว่างและส่งแจ้งเตือนให้นักศึกษา |
| เวลาหมดอายุการรับสิทธิ์ (1 วัน) | Datetime | `QUEUE.expired_at` | คำนวณ `notified_at + 1 วัน` หากไม่ยืนยันจะตัดสิทธิ์อัตโนมัติ |
| ปุ่มยืนยันรับสิทธิ์คิว `[ ✓ ยืนยันรับสิทธิ์ ]` | Button | บันทึก `QUEUE` | ปรับ `status = 'CONFIRMED'`, บันทึก `confirmed_at = NOW()` |
| ปุ่มยกเลิกคิว `[ ออกจากคิว ]` | Button | บันทึก `QUEUE` | ปรับ `status = 'CANCELLED'` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- ตัวนับเวลาถอยหลัง 24 ชั่วโมง (Countdown Timer): คำนวณจาก `expired_at - NOW()` บนหน้าจอ

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `QUEUE`
- `ITEM`
- `EQUIPMENT`
- `DURABLE_MATERIAL`
- `BORROW_ITEM`
- `BORROW_REQUEST`
