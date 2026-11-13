# Field Mapping: `page-item-list.html` (รายการวัสดุและครุภัณฑ์)

> **หน้าจอ:** แคตตาล็อกค้นหา แสดงรายการ และเพิ่มสิ่งของลงตะกร้า  
> **ไฟล์ต้นทาง:** `pages/page-item-list.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student)  
> **Use Case:** UC-01, UC-02, UC-05, UC-10  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **การค้นหาและตัวกรอง** | | | |
| ช่องค้นหาชื่อหรือรหัส (`p_item_list_q`) | Input (Search) | `ITEM.name`, `EQUIPMENT.asset_tag` | ค้นหาจากชื่อสิ่งของ หรือรหัสครุภัณฑ์ |
| ตัวกรองประเภทพัสดุ (3 ประเภท) | Filter Button | `ITEM.item_type` | กรองตามประเภท `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` |
| ตัวกรองสถานะ (`p_item_list_f-status`) | Filter Select | `ITEM.base_status`, `EQUIPMENT.status` | กรองความพร้อมใช้งาน (`AVAILABLE`, `BORROWED`, `MAINTENANCE` ฯลฯ) |
| **การ์ดแสดงสิ่งของ (Item Card)** | | | |
| รูปภาพสิ่งของ | Image | `ITEM.image` | รูปถ่ายประจำสิ่งของ |
| ป้ายประเภทพัสดุ | Badge | `ITEM.item_type` | แสดงป้าย วัสดุสิ้นเปลือง / วัสดุคงทน / ครุภัณฑ์ |
| ชื่อสิ่งของ | Text | `ITEM.name` | ชื่อรายการพัสดุ |
| รหัสทะเบียนครุภัณฑ์รายชิ้น | Text (Badge) | `EQUIPMENT.asset_tag` | แสดงเฉพาะครุภัณฑ์ เช่น `UBU-EQ-001-01` |
| สถานที่ตั้งวางในคลัง | Text | `ITEM.location` | ตำแหน่งจัดเก็บ เช่น ตู้ A ชั้น 2 |
| หน่วยนับ | Text | `ITEM.unit` | เช่น ชิ้น, อัน, เครื่อง, กล่อง |
| ราคาจัดซื้อ | Text | `ITEM.purchase_price` | ราคาจัดซื้อเดิมของสิ่งของ |
| จำนวนคงเหลือ / จำนวนทั้งหมด | Text | `MATERIAL.qty_available`, `MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_total` | แสดงสำหรับวัสดุสิ้นเปลืองและวัสดุคงทน |
| ระยะเวลายืมสูงสุด | Text | `DURABLE_MATERIAL.max_borrow_days`, `EQUIPMENT.max_borrow_days` | จำนวนวันที่อนุญาตให้ยืมได้สูงสุด |
| อัตราค่าปรับต่อวัน | Text | `DURABLE_MATERIAL.fine_rate_per_day`, `EQUIPMENT.fine_rate_per_day` | อัตราค่าปรับกรณีส่งคืนล่าช้า |
| สถานะความพร้อม | Badge | `ITEM.base_status`, `EQUIPMENT.status` | แสดงสถานะ "พร้อมให้ยืม", "ถูกยืมอยู่", "ส่งซ่อม" ฯลฯ |
| คะแนนดาวเฉลี่ย และจำนวนรีวิว | Star / Text | คำนวณจาก `REVIEW` | คำนวณ `AVG(REVIEW.rating)` และ `COUNT(REVIEW.id)` โดยเชื่อมโยงผ่าน `BORROW_ITEM.item_id = ITEM.id` |
| **ปุ่มและแอ็กชัน** | | | |
| ปุ่มใส่ตะกร้า `[ + ใส่ตะกร้า ]` | Button | บันทึก `CART_ITEM` | เพิ่มรายการลงตะกร้า: `cart_id`, `item_id`, `qty = 1` |
| ปุ่มจองคิว `[ ⏳ จองคิว ]` (เมื่อของหมด) | Button | บันทึก `QUEUE` | บันทึกเข้าคิว: `item_id`, `user_id`, `status = 'WAITING'`, `joined_at = NOW()` |
| ปุ่มตะกร้ายืมของมุมขวาบน | Button / Link | คำนวณจาก `CART_ITEM` | แสดงจำนวนรวมของสิ่งของในตะกร้า |

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `ITEM`
- `MATERIAL`
- `DURABLE_MATERIAL`
- `EQUIPMENT`
- `REVIEW`
- `CART`
- `CART_ITEM`
- `QUEUE`
