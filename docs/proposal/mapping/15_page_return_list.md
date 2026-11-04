# หน้าที่ 15: ตรวจรับคืนครุภัณฑ์และจัดการค่าปรับ (`page-return-list.html`)
**บทบาทผู้ใช้งาน:** เจ้าหน้าที่พัสดุ (`staff`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `RETURN_REQUEST`, `RETURN_ITEM`, `BORROW_REQUEST`, `BORROW_ITEM`, `EQUIPMENT`, `DURABLE_MATERIAL`, `USER`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: รายการคำขอที่นำของมาส่งคืน (On-the-Spot Checklist)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **สถิติจำนวนคำขอรอตรวจรับคืน / กำลังยืม / เกินกำหนด** | `p_rl_pending_count` | `SELECT` | `BORROW_REQUEST`, `RETURN_REQUEST` | `status`, `due_date` | นับจำนวนคำขอที่รอดำเนินการ |
| 2 | **ช่องค้นหาและแถบตัวกรองสถานะ** | `p_rl_search`, `#p_rl_tab_*` | `SELECT` | `BORROW_REQUEST`, `USER`, `EQUIPMENT` | `id`, `name`, `asset_tag` | กรองตามสถานะ: ทั้งหมด, รอตรวจรับคืน, เกินกำหนด, ค้างส่งบางชิ้น |
| 3 | **รายการสิ่งของในคำขอ (Checklist ตรวจนับบนโต๊ะ)** | `input[type="checkbox"]` | `SELECT` | `BORROW_ITEM`, `EQUIPMENT`, `DURABLE_MATERIAL` | `asset_tag`, `qty`, `name` | ติ๊กเลือกเฉพาะชิ้นที่นำมาส่งคืนจริงในรอบนี้ (รองรับ Partial Return) |
| 4 | **ตัวเลือกสภาพสิ่งของตอนรับคืน** | สวิตช์สภาพ (ปกติ / ชำรุด / สูญหาย) | `INSERT` / `UPDATE` | `RETURN_ITEM` | `RETURN_ITEM.condition_status` | ค่า Enum: `NORMAL`, `DAMAGED`, `LOST` |
| 5 | **ระบุอาการชำรุดเพื่อส่งซ่อม** | `input[text]` | `INSERT` / `UPDATE` | `RETURN_ITEM`, `RETURN_REQUEST` | `RETURN_REQUEST.note` | เมื่อเลือกสภาพ `DAMAGED` จะส่งต่อเข้าสู่ระบบงานแจ้งซ่อม |
| 6 | **คิดค่าชดใช้สิ่งของสูญหาย** | `input[text]`, เช็คบ็อกซ์ชำระเงิน | `INSERT` / `UPDATE` | `RETURN_ITEM` | `lost_compensation`, `lost_paid` | คำนวณจากราคาจัดซื้อเดิม และบันทึกสถานะการชำระเงินค่าชดใช้ |

---

### ส่วนที่ 2: การคำนวณและปรับลดหย่อนค่าปรับเกินกำหนด
| ลำดับ | ชื่อช่อง / ช่องกรอกข้อมูล (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 7 | **ยอดค่าปรับคำนวณตามสูตร** | - | `SELECT` | `EQUIPMENT`, `DURABLE_MATERIAL`, `RETURN_REQUEST` | `fine_rate_per_day`, `custom_fine` | คำนวณตามอัตราค่าปรับรวมของชิ้นที่ค้างส่งจริง |
| 8 | **ปุ่ม "✏️ กำหนดยอดเอง / ลดหย่อน"** | `p_return_list_editFine` | `UPDATE` | `RETURN_REQUEST` | `RETURN_REQUEST.custom_fine`, `fine_reason` | เจ้าหน้าที่สามารถปรับลดหย่อนค่าปรับ (เช่น กรอก 0 บาท กรณียกเว้น) |
| 9 | **ปุ่ม "บันทึกการชำระเงิน"** | `p_return_list_toggleFinePaid` | `UPDATE` | `RETURN_REQUEST` | `RETURN_REQUEST.fine_paid` | สลับสถานะชำระค่าปรับ (`true` / `false`) |

---

### ส่วนที่ 3: ปุ่มดำเนินการยืนยันหรือปฏิเสธการรับคืน
| ลำดับ | ปุ่มกดบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ผลลัพธ์ในฐานข้อมูล |
| :---: | :--- | :---: | :--- | :--- |
| 10 | **ปุ่ม "✕ ปฏิเสธการรับคืน"** | `UPDATE` | `RETURN_REQUEST`, `BORROW_REQUEST` | ปรับ `RETURN_REQUEST.status = 'REJECTED'`, `inspected_by = [เจ้าหน้าที่]`, `BORROW_REQUEST.status = 'BORROWING'` |
| 11 | **ปุ่ม "✓ ยืนยันการตรวจรับคืน"** | `INSERT` / `UPDATE` | `RETURN_REQUEST`, `RETURN_ITEM`, `BORROW_REQUEST`, `EQUIPMENT` | 1. สร้าง/บันทึก `RETURN_REQUEST` (`inspected_by = [เจ้าหน้าที่]`, `status = 'RETURNED'`, `returned_at = NOW()`)<br>2. บันทึก `RETURN_ITEM` (`condition_status`, `lost_compensation`, `lost_paid`)<br>3. หากคืนครบทุกชิ้น ปรับ `BORROW_REQUEST.status = 'RETURNED'` (หากคืนบางส่วน ปรับ `status = 'BORROWING'` และบันทึกยอดค้างส่ง)<br>4. นำสต็อกกลับเข้าคลัง `qty_available` และปรับสถานะครุภัณฑ์กลับเป็น `AVAILABLE` (หรือ `DAMAGED` หากชำรุด) |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **เชื่อมโยง `RETURN_REQUEST` และ `RETURN_ITEM`:** บันทึกข้อมูลการตรวจรับคืนลงตาราง `return_requests` และ `return_items` พร้อมระบุ `inspected_by` เป็นรหัสเจ้าหน้าที่
- ✅ **Enum `condition_status` ถูกต้อง:** จัดเก็บค่าเป็นตัวพิมพ์ใหญ่ `'NORMAL'`, `'DAMAGED'`, `'LOST'` ตรงตาม ERD
- ✅ **ส่งผ่านอาร์กิวเมนต์ `getFineRatePerDay(r)`:** แก้ไขการเรียกคำนวณค่าปรับในบรรทัดที่ 311 ให้ส่งพารามิเตอร์ `r` เพื่อคิดค่าปรับตามอัตราของครุภัณฑ์ที่ค้างส่งจริง
