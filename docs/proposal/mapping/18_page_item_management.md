# หน้าที่ 18: การจัดการพัสดุ ครุภัณฑ์ และตำแหน่งคลัง (`page-item-overview.html`, `page-item-form.html` ฯลฯ)
**บทบาทผู้ใช้งาน:** เจ้าหน้าที่พัสดุ (`staff`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: ภาพรวมรายการสิ่งของในคลัง (`page-item-overview.html`)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **ช่องค้นหาและตัวกรอง (ชื่อ, หมวดหมู่, ประเภท, สถานะ)** | `p_item_overview_q`, `f-cat`, `f-type`, `f-status` | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.name`, `.category`, `.base_status` | คัดกรองสิ่งของตามเกณฑ์ |
| 2 | **ตารางรายการสิ่งของ (รูป, ชื่อ, หมวดหมู่, ชนิด, คงเหลือ/ทั้งหมด)** | `p_item_overview_rows` | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.image`, `.name`, `.unit`, `.qty_available`, `.qty_total` | แสดงจำนวนคงเหลือเทียบกับยอดทั้งหมด |
| 3 | **ป้ายสถานะ (พร้อมให้ยืม / กำลังยืมหมด / ไม่พร้อมใช้งาน)** | - | `SELECT` | `DURABLE_MATERIAL`, `EQUIPMENT` | `base_status` | สถานะความพร้อมใช้งานในคลัง |

---

### ส่วนที่ 2: ฟอร์มเพิ่ม/แก้ไขสิ่งของ (`page-item-form.html`)
| ลำดับ | ชื่อช่อง / ช่องกรอกข้อมูล (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 4 | **ชื่อสิ่งของ** <span class="text-red-500">*</span> | `p_item_form_f-name` | `INSERT` / `UPDATE` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.name` | ชื่อสิ่งของ |
| 5 | **รูปภาพ (Emoji / URL)** | `p_item_form_f-image` | `INSERT` / `UPDATE` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.image` | รูปภาพตัวแทนสิ่งของ |
| 6 | **หมวดหมู่สิ่งของ** <span class="text-red-500">*</span> | `p_item_form_f-cat` | `INSERT` / `UPDATE` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.category` | เช่น โสตทัศนูปกรณ์, เครื่องมือช่าง |
| 7 | **ตำแหน่งจัดเก็บในคลัง** <span class="text-red-500">*</span> | `p_item_form_f-loc` | `INSERT` / `UPDATE` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.location` | เช่น ห้อง EN6-101 · ตู้ A1 ชั้น 2 |
| 8 | **ประเภทสิ่งของ** <span class="text-red-500">*</span> | `p_item_form_f-type` | `INSERT` | - | แยกตารางปลายทาง | เลือกระหว่าง: `material`, `durable_material`, `equipment` |
| 9 | **จำนวนทั้งหมด** <span class="text-red-500">*</span> | `p_item_form_f-qty` | `INSERT` / `UPDATE` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.qty_total`, `.qty_available` | ยอดจำนวนชิ้นในระบบ |
| 10 | **หน่วยนับ** <span class="text-red-500">*</span> | `p_item_form_f-unit` | `INSERT` / `UPDATE` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.unit` | เช่น เครื่อง, ชุด, ตัว, รีม |
| 11 | **ราคาจัดซื้อเดิม (บาท)** | `p_item_form_f-price` | `INSERT` / `UPDATE` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.purchase_price` | ราคาจัดซื้อสำหรับใช้คิดค่าชดใช้สูญหาย |
| 12 | **จำนวนวันสูงสุดที่ยืมได้** | `p_item_form_f-days` | `INSERT` / `UPDATE` | `DURABLE_MATERIAL`, `EQUIPMENT` | `.max_borrow_days` | เฉพาะวัสดุคงทนและครุภัณฑ์ |
| 13 | **อัตราค่าปรับล่าช้า (บาท/วัน)** | `p_item_form_f-fine` | `INSERT` / `UPDATE` | `DURABLE_MATERIAL`, `EQUIPMENT` | `.fine_rate_per_day` | เฉพาะวัสดุคงทนและครุภัณฑ์ |
| 14 | **รายละเอียด/สเปก (Description)** | `p_item_form_f-desc` | `INSERT` / `UPDATE` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.description` | ข้อมูลประกอบและคำอธิบาย |
| 15 | **รหัสครุภัณฑ์รายชิ้น (Asset Tag / Serial No.)** | `.unit-tag-input` | `INSERT` / `UPDATE` | `EQUIPMENT` | `EQUIPMENT.asset_tag` | รหัสประจำชิ้นสำหรับครุภัณฑ์ (Unique Key) |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **แยกประเภทและฟิลด์ตรง 3 ตาราง:**
  - `MATERIAL`: ไม่มี `max_borrow_days` และ `fine_rate_per_day`
  - `DURABLE_MATERIAL`: มี `max_borrow_days`, `fine_rate_per_day`, `base_status`
  - `EQUIPMENT`: มี `asset_tag` ประจำชิ้น, `max_borrow_days`, `fine_rate_per_day`, `base_status`
- ✅ **บันทึก `purchase_price`:** ปรับโค้ดให้บันทึกฟิลด์ `purchase_price` ควบคู่กับ `price` ตาม ERD
- ✅ **เชื่อมโยงตำแหน่งจัดเก็บ (`location`):** บันทึกระบุตู้/ชั้น/ห้องจัดเก็บลงในคอลัมน์ `.location` โดยตรง
