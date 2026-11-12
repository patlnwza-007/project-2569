# Field Mapping: `page-cart.html` (ตะกร้าของฉัน)

> **หน้าจอ:** ตรวจสอบรายการในตะกร้า จัดการจำนวน และตรวจจับการถูกยืมตัดหน้า  
> **ไฟล์ต้นทาง:** `pages/page-cart.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student)  
> **Use Case:** UC-05, UC-10  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **รายการสิ่งของในตะกร้า** | | | |
| รายการในตะกร้า | List Item | `CART_ITEM.id` | รหัสแถวในตะกร้าของผู้ใช้ |
| รูปภาพสิ่งของ | Image | `ITEM.image` | ดึงผ่าน `CART_ITEM.item_id` |
| ชื่อสิ่งของ | Text | `ITEM.name` | ชื่อสิ่งของ |
| ป้ายประเภทพัสดุ | Badge | `ITEM.item_type` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` |
| รหัสครุภัณฑ์ | Text (Badge) | `EQUIPMENT.asset_tag` | แสดงเฉพาะครุภัณฑ์ |
| สถานะความพร้อม (ตรวจตัดหน้า) | Badge / Alert | `MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_available`, `EQUIPMENT.status` | เช็กแบบเรียลไทม์ว่าของยังว่างพอหรือไม่ หากไม่ว่างจะแสดงป้ายเตือนของหมด |
| หน่วยนับ | Text | `ITEM.unit` | เช่น ชิ้น, อัน |
| จำนวนที่ต้องการยืม | Input (Number) | `CART_ITEM.qty` | ปรับเพิ่ม/ลดจำนวนในตะกร้า |
| ระยะเวลายืมสูงสุด | Text | `DURABLE_MATERIAL.max_borrow_days`, `EQUIPMENT.max_borrow_days` | แสดงระยะเวลาที่ยืมได้ของแต่ละรายการ |
| ปุ่มลบรายการออกจากตะกร้า | Button | ลบ `CART_ITEM` | ลบแถว `CART_ITEM.id` ออกจากตะกร้า |
| ปุ่มจองคิวแทน (เมื่อของหมด/ถูกตัดหน้า) | Button | บันทึก `QUEUE` | บันทึก `item_id`, `user_id`, `status = 'WAITING'`, `joined_at = NOW()` |
| **แถบสรุปตะกร้า (Cart Summary Bar)** | | | |
| จำนวนรายการทั้งหมด | Summary Text | คำนวณจาก `CART_ITEM` | `COUNT(CART_ITEM.id)` ของตะกร้า |
| ปุ่มดำเนินการต่อ `[ ไปหน้าส่งคำขอยืม → ]` | Button | Navigation | ตรวจสอบความถูกต้องและนำทางไป `page-request-form.html` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- Checkbox เลือกรายการในตะกร้า (`selectedItems`): เป็นสถานะการเลือกชั่วคราวบนหน้าเว็บก่อนส่งฟอร์ม

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `CART`
- `CART_ITEM`
- `ITEM`
- `MATERIAL`
- `DURABLE_MATERIAL`
- `EQUIPMENT`
- `QUEUE`
