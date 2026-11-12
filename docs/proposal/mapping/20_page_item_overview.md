# Field Mapping: `page-item-overview.html` (ภาพรวมจัดการคลังสิ่งของ)

> **หน้าจอ:** ภาพรวมคลังพัสดุ 3 ประเภท แสดงจำนวนคงเหลือ และลิงก์ไปจัดการพัสดุ  
> **ไฟล์ต้นทาง:** `pages/page-item-overview.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-21  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **การค้นหาและตัวกรองคลัง** | | | |
| ช่องค้นหาชื่อหรือรหัส | Input (Search) | `ITEM.name`, `EQUIPMENT.asset_tag` | ค้นหาพัสดุในคลัง |
| ตัวกรองประเภทพัสดุ (3 ประเภท) | Filter Button | `ITEM.item_type` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` |
| ตัวกรองสถานะ | Filter Select | `ITEM.base_status`, `EQUIPMENT.status` | กรองตามสถานะความพร้อม |
| **ตารางรายการพัสดุในคลัง** | | | |
| รูปภาพสิ่งของ | Image | `ITEM.image` | รูปถ่ายสิ่งของ |
| ชื่อสิ่งของ | Text | `ITEM.name` | ชื่อรายการพัสดุ |
| ป้ายประเภทพัสดุ | Badge | `ITEM.item_type` | แสดงประเภทสิ่งของ |
| รหัสประจำชิ้น (ครุภัณฑ์) | Text (Badge) | `EQUIPMENT.asset_tag` | แสดงรหัส Asset Tag รายชิ้น |
| สถานที่ตั้งวางในคลัง | Text | `ITEM.location` | ที่ตั้งปกติในคลัง |
| ราคาจัดซื้อ | Text | `ITEM.purchase_price` | ราคาจัดซื้อเดิม |
| หน่วยนับ | Text | `ITEM.unit` | หน่วยนับพัสดุ |
| จำนวนคงเหลือ / ทั้งหมด (วัสดุ) | Text | `MATERIAL.qty_available`, `MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_total` | สต็อกคงเหลือสำหรับวัสดุสิ้นเปลืองและวัสดุคงทน |
| สถานะความพร้อม | Badge | `ITEM.base_status`, `EQUIPMENT.status` | สถานะของสิ่งของ |
| วันยืมสูงสุด / ค่าปรับต่อวัน | Text | `DURABLE_MATERIAL.max_borrow_days`, `DURABLE_MATERIAL.fine_rate_per_day`, `EQUIPMENT.max_borrow_days`, `EQUIPMENT.fine_rate_per_day` | กติกาการยืมและค่าปรับ |
| ปุ่มแก้ไข `[ ✏️ แก้ไข ]` | Button | Navigation | ลิงก์ไป `page-item-form.html?id=X` |
| ปุ่มเปลี่ยนสถานะ `[ 🔄 เปลี่ยนสถานะ ]` | Button | Navigation | ลิงก์ไป `page-item-status-change.html?id=X` |
| ปุ่มลบพัสดุ (กรณีวัสดุ) | Button | Navigation | ลิงก์ไป `page-item-delete.html?id=X` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- Checkbox เลือกหลายรายการ (`p_io_check_all`): สถานะการเลือกบนหน้าจอสำหรับ Batch Update ชั่วคราว

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `ITEM`
- `MATERIAL`
- `DURABLE_MATERIAL`
- `EQUIPMENT`
