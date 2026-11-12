# Field Mapping: `page-item-form.html` (เพิ่ม/แก้ไขข้อมูลวัสดุและครุภัณฑ์)

> **หน้าจอ:** ฟอร์มเพิ่มรายการสิ่งของใหม่เข้าสู่คลัง หรือแก้ไขข้อมูลสิ่งของเดิม  
> **ไฟล์ต้นทาง:** `pages/page-item-form.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-20  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **ข้อมูลทั่วไปของสิ่งของ (Common Attributes)** | | | |
| ชื่อสิ่งของ | Input (Text) | `ITEM.name` | ระบุชื่อพัสดุ |
| ประเภทสิ่งของ (3 ประเภท) | Select | `ITEM.item_type` | เลือก `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` |
| รูปภาพสิ่งของ | Input (File) / URL | `ITEM.image` | รูปภาพพัสดุ |
| สถานที่ตั้งวางในคลัง | Input (Text) | `ITEM.location` | ระบุตำแหน่ง เช่น ตู้ A ชั้น 2 |
| หน่วยนับ | Input (Text) | `ITEM.unit` | เช่น ตัว, อัน, กล่อง, เครื่อง |
| ราคาจัดซื้อเดิม | Input (Number) | `ITEM.purchase_price` | ราคาต่อหน่วย/ต่อชิ้น |
| รายละเอียดและคุณลักษณะ | Input (Textarea) | `ITEM.description` | สเปกและรายละเอียด |
| สถานะพื้นฐาน | Select | `ITEM.base_status` | `AVAILABLE`, `DAMAGED`, `INACTIVE`, `RETIRED` |
| **กรณีประเภทวัสดุสิ้นเปลือง (MATERIAL)** | | | |
| จำนวนทั้งหมด | Input (Number) | `MATERIAL.qty_total` | สต็อกทั้งหมดที่เพิ่มเข้าคลัง |
| จำนวนคงเหลือเริ่มต้น | Number (Auto) | `MATERIAL.qty_available` | เริ่มต้นเท่ากับ `qty_total` |
| **กรณีประเภทวัสดุคงทน (DURABLE_MATERIAL)** | | | |
| จำนวนทั้งหมด | Input (Number) | `DURABLE_MATERIAL.qty_total` | สต็อกทั้งหมดที่เพิ่มเข้าคลัง |
| จำนวนคงเหลือเริ่มต้น | Number (Auto) | `DURABLE_MATERIAL.qty_available` | เริ่มต้นเท่ากับ `qty_total` |
| จำนวนวันยืมสูงสุด | Input (Number) | `DURABLE_MATERIAL.max_borrow_days` | ระยะเวลาที่อนุญาตให้ยืม |
| อัตราค่าปรับต่อวัน | Input (Number) | `DURABLE_MATERIAL.fine_rate_per_day` | อัตราค่าปรับกรณีส่งคืนล่าช้า |
| **กรณีประเภทครุภัณฑ์ (EQUIPMENT — เฉพาะขั้นตอนเพิ่มใหม่)** | | | |
| จำนวนชิ้นที่เพิ่ม | Input (Number) | กำหนดจำนวนแถว | จำนวนชิ้นที่จะสร้าง (1 ชิ้น = 1 แถวใน DB) |
| กล่องระบุรหัสครุภัณฑ์รายชิ้น | Inputs (Text) | `EQUIPMENT.asset_tag` | กรอกรหัส Asset Tag แต่ละชิ้น เช่น `UBU-EQ-001-01` |
| จำนวนวันยืมสูงสุด | Input (Number) | `EQUIPMENT.max_borrow_days` | ระยะเวลาที่อนุญาตให้ยืม |
| อัตราค่าปรับต่อวัน | Input (Number) | `EQUIPMENT.fine_rate_per_day` | อัตราค่าปรับกรณีส่งคืนล่าช้า |
| สถานะเริ่มต้นของครุภัณฑ์ | Status (Auto) | `EQUIPMENT.status` | ตั้งเป็น `'AVAILABLE'` (พร้อมให้ยืม) ทุกชิ้น |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- ในโหมด **แก้ไขสิ่งของ (Edit Item):** ระบบจะซ่อนกล่องรหัสครุภัณฑ์รายชิ้น เพื่อรักษาความถูกต้องของทะเบียนครุภัณฑ์ (Audit Trail) โดยจะแก้ไขได้เฉพาะข้อมูลรุ่นและคุณลักษณะหลักในตาราง `ITEM` เท่านั้น

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `ITEM`
- `MATERIAL`
- `DURABLE_MATERIAL`
- `EQUIPMENT`
