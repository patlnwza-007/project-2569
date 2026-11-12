# Field Mapping: `page-history.html` (ประวัติการยืมของฉัน)

> **หน้าจอ:** หน้าประวัติการยืม-คืนพัสดุในอดีตของนักศึกษา และลิงก์ไปประเมินรีวิว  
> **ไฟล์ต้นทาง:** `pages/page-history.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student)  
> **Use Case:** UC-11, UC-14  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| เลขที่คำขอยืม | Text | `BORROW_REQUEST.id` | รหัสคำขอยืม |
| วันที่ส่งคำขอ | Datetime | `BORROW_REQUEST.created_at` | วันที่ทำรายการยืม |
| สถานะคำขอ | Badge | `BORROW_REQUEST.status` | `RETURNED`, `ISSUED`, `REJECTED`, `CANCELLED` |
| รายการสิ่งของและจำนวน | Text | `BORROW_ITEM.qty`, `ITEM.name`, `ITEM.unit` | รายการพัสดุที่เคยยืม |
| รหัสครุภัณฑ์ประจำชิ้น | Text (Badge) | `EQUIPMENT.asset_tag` | รหัสเฉพาะชิ้นที่ยืมไป |
| สถานะการรีวิว / ปุ่มประเมิน | Button / Badge | ตรวจสอบจาก `REVIEW` | ตรวจสอบว่ามีแถวใน `REVIEW` ที่ตรงกับ `borrow_item_id` หรือยัง หากยังไม่มีจะแสดงปุ่ม `[ ⭐ เขียนรีวิว ]` นำทางไปหน้า `page-evaluation.html` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- ตัวกรองประวัติตามช่วงเวลา / สถานะ: เป็นพารามิเตอร์กรองการค้นหาของหน้าเว็บ

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `BORROW_REQUEST`
- `BORROW_ITEM`
- `ITEM`
- `EQUIPMENT`
- `REVIEW`
