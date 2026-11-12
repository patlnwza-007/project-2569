# Field Mapping: `page-bulk-import.html` (นำเข้าข้อมูลคลังแบบชุด CSV)

> **หน้าจอ:** นำเข้าข้อมูลพัสดุจำนวนมากผ่านไฟล์ CSV (Batch Import) รองรับพัสดุ 3 ประเภท  
> **ไฟล์ต้นทาง:** `pages/page-bulk-import.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-24  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ในไฟล์ CSV / หน้าจอ | ประเภท UI / CSV Header | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| ช่องอัปโหลดไฟล์ CSV | Input (File) | *ประมวลผลเป็นชุด* | รับไฟล์ CSV เข้ามาตรวจสอบความถูกต้อง |
| ชื่อสิ่งของ | คอลัมน์ `name` | `ITEM.name` | บันทึกชื่อพัสดุ |
| ประเภทสิ่งของ (3 ประเภท) | คอลัมน์ `item_type` | `ITEM.item_type` | `material`, `durable_material`, `equipment` |
| สถานที่ตั้งวางในคลัง | คอลัมน์ `location` | `ITEM.location` | ที่ตั้งสิ่งของ |
| หน่วยนับ | คอลัมน์ `unit` | `ITEM.unit` | เช่น อัน, กล่อง, เครื่อง |
| ราคาจัดซื้อเดิม | คอลัมน์ `purchase_price` | `ITEM.purchase_price` | ราคาจัดซื้อ |
| รายละเอียดคุณลักษณะ | คอลัมน์ `description` | `ITEM.description` | คำอธิบายสเปก |
| จำนวนพัสดุ | คอลัมน์ `qty` | `MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_total` | สต็อกทั้งหมด (สำหรับวัสดุ) |
| จำนวนวันยืมสูงสุด | คอลัมน์ `max_borrow_days` | `DURABLE_MATERIAL.max_borrow_days`, `EQUIPMENT.max_borrow_days` | จำนวนวันที่อนุญาตให้ยืม |
| อัตราค่าปรับต่อวัน | คอลัมน์ `fine_rate_per_day` | `DURABLE_MATERIAL.fine_rate_per_day`, `EQUIPMENT.fine_rate_per_day` | อัตราค่าปรับ |
| รหัสทะเบียนครุภัณฑ์ | คอลัมน์ `asset_tag` | `EQUIPMENT.asset_tag` | รหัสเฉพาะชิ้น (สำหรับครุภัณฑ์ 1 แถว = 1 ชิ้น) |
| สถานะเริ่มต้น | คอลัมน์ `status` | `ITEM.base_status`, `EQUIPMENT.status` | ตั้งเป็น `AVAILABLE` |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- ตารางพรีวิวผลการนำเข้า (Preview Table) และการแจ้งเตือนบรรทัดที่มีข้อผิดพลาด: ประมวลผลบนหน่วยความจำชั่วคราวก่อนกดยืนยันบันทึกจริง

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `ITEM`
- `MATERIAL`
- `DURABLE_MATERIAL`
- `EQUIPMENT`
