# Field Mapping: `page-item-detail.html` (รายละเอียดสิ่งของ)

> **หน้าจอ:** หน้ารายละเอียดสิ่งของ ข้อมูลสเปก รหัสชิ้น และประวัติรีวิว  
> **ไฟล์ต้นทาง:** `pages/page-item-detail.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student), 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-03, UC-10, UC-37  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| รูปภาพสิ่งของ | Image | `ITEM.image` | รูปถ่ายพัสดุ |
| ชื่อสิ่งของ | Text | `ITEM.name` | ชื่อพัสดุ |
| ป้ายประเภทพัสดุ | Badge | `ITEM.item_type` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` |
| รหัสทะเบียนครุภัณฑ์รายชิ้น | Text (Badge) | `EQUIPMENT.asset_tag` | รหัสเฉพาะชิ้น (สำหรับครุภัณฑ์) |
| สถานะความพร้อมใช้งาน | Badge | `ITEM.base_status`, `EQUIPMENT.status` | สถานะของสิ่งของ |
| รายละเอียดและคุณลักษณะ (Specification) | Text | `ITEM.description` | คำอธิบายสเปกสิ่งของ |
| สถานที่ตั้งวางในคลัง | Text | `ITEM.location` | ที่ตั้งปกติในคลัง |
| หน่วยนับ | Text | `ITEM.unit` | เช่น ตัว, เครื่อง, อัน |
| ราคาจัดซื้อเดิม | Text | `ITEM.purchase_price` | ราคาจัดซื้อ |
| จำนวนคงเหลือ / ทั้งหมด (วัสดุ) | Text | `MATERIAL.qty_available`, `MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_total` | สต็อกคงเหลือสำหรับวัสดุสิ้นเปลืองและวัสดุคงทน |
| จำนวนวันยืมสูงสุด | Text | `DURABLE_MATERIAL.max_borrow_days`, `EQUIPMENT.max_borrow_days` | ระยะเวลายืมสูงสุด |
| อัตราค่าปรับต่อวัน | Text | `DURABLE_MATERIAL.fine_rate_per_day`, `EQUIPMENT.fine_rate_per_day` | ค่าปรับกรณีเกินกำหนด |
| หมายเหตุสภาพ/ตำหนิของชิ้น | Text | `EQUIPMENT.note` | หมายเหตุสภาพความเสียหายเดิม |
| ที่ตั้งปัจจุบันที่แจ้งย้าย (ถ้ากำลังถูกยืม) | Text | `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at` | สถานที่ใช้งานปัจจุบันที่นักศึกษาแจ้งย้ายไว้ |
| **ส่วนรีวิวและคะแนนดาว (Reviews & Ratings)** | | | |
| คะแนนเฉลี่ยและสถิติดาว | Rating Summary | คำนวณจาก `REVIEW` | `AVG(REVIEW.rating)` และ `COUNT(REVIEW.id)` ผ่าน `BORROW_ITEM.item_id = ITEM.id` |
| รายชื่อผู้รีวิว | Text | `USER.name` | สืบหาจาก `REVIEW -> BORROW_ITEM -> BORROW_REQUEST.user_id -> USER.name` |
| คะแนนดาวรายบุคคล (1-5 ดาว) | Stars | `REVIEW.rating` | คะแนนที่ผู้ยืมประเมิน |
| ความคิดเห็นรีวิวสภาพจริง | Text | `REVIEW.comment` | ข้อความรีวิวการใช้งาน |
| วันที่รีวิว | Datetime | `REVIEW.created_at` | วันเวลาที่ส่งรีวิว |
| **การดำเนินการ (Actions)** | | | |
| ปุ่มใส่ตะกร้า | Button | บันทึก `CART_ITEM` | บันทึก `cart_id`, `item_id`, `qty` |
| ปุ่มจองคิว (กรณีของหมด) | Button | บันทึก `QUEUE` | บันทึก `item_id`, `user_id`, `status = 'WAITING'`, `joined_at = NOW()` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
1. **`p_dt_modal_qty_input` (จำนวนในป๊อปอัปเลือกจำนวน):** ค่าชั่วคราวก่อนกดยืนยันใส่ตะกร้า

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `ITEM`
- `MATERIAL`
- `DURABLE_MATERIAL`
- `EQUIPMENT`
- `BORROW_ITEM`
- `BORROW_REQUEST`
- `USER`
- `REVIEW`
- `CART_ITEM`
- `QUEUE`
