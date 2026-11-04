# หน้าที่ 5: ตะกร้าของฉัน (`page-cart.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `CART_ITEM`, `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT`, `QUEUE`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: แถบแจ้งเตือนและรายการสิ่งของในตะกร้า (`#p_cart_rows`)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **แถบเตือน: ตะกร้ามีทั้งวัสดุและครุภัณฑ์ปนกัน** | `p_cart_mix_warning` | `SELECT (Derived)` | `CART_ITEM` | `material_id`, `durable_material_id`, `equipment_id` | แสดงเมื่อมีทั้งรายการที่ต้องคืน (`equipment_id` / `durable_material_id`) และไม่ต้องคืน (`material_id`) |
| 2 | **รูปภาพ / ไอคอนสิ่งของ** | - | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.image` | ดึงตาม FK ของแต่ละแถวใน `CART_ITEM` |
| 3 | **ชื่อสิ่งของ** | - | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.name` | ชื่อวัสดุหรือครุภัณฑ์ในตะกร้า |
| 4 | **ป้ายประเภทสิ่งของ** (ครุภัณฑ์ / วัสดุคงทน / วัสดุสิ้นเปลือง) | - | `SELECT (Derived)` | `CART_ITEM` | แยกตาม FK ที่ไม่เป็น `NULL` (`equipment_id`, `durable_material_id`, `material_id`) | ระบุประเภทสิ่งของ |
| 5 | **รหัสครุภัณฑ์ประจำชิ้น (`🏷️ ยืมครุภัณฑ์รหัสชิ้น: UBU-EQ-...`)** | - | `SELECT` | `EQUIPMENT` | `EQUIPMENT.asset_tag` | แสดงเฉพาะรายการที่เป็นครุภัณฑ์ (`equipment_id`) |
| 6 | **จำนวนคงเหลือในคลัง (`คงเหลือในคลัง: X ชิ้น`)** | - | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL` | `.qty_available`, `.unit` | ใช้ตรวจสอบว่าจำนวนที่ขอไม่เกินสต็อกที่มีอยู่ |
| 7 | **ระยะเวลายืมสูงสุด (`ยืมได้สูงสุด X วัน`)** | - | `SELECT` | `DURABLE_MATERIAL`, `EQUIPMENT` | `.max_borrow_days` | แสดงเฉพาะรายการที่ต้องนำมาส่งคืน |
| 8 | **ป้ายเตือนกรณีถูกยืม/เบิกตัดหน้า (`🔴 ครุภัณฑ์นี้ถูกยืมไปแล้ว / สต็อกหมด`)** | `p_cart_snipe_alert` | `SELECT (Check)` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `EQUIPMENT.base_status`, `.qty_available` | เช็คสดว่าของในตะกร้ายังมีสถานะ `AVAILABLE` หรือ `qty_available > 0` หรือไม่ |

---

### ส่วนที่ 2: ปุ่มปรับจำนวน ลบรายการ และสรุปท้ายตะกร้า (`#p_cart_footer`)
| ลำดับ | ชื่อช่อง / ปุ่มกดบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 9 | **ช่องกรอกและปุ่มปรับจำนวน (`-` / `+`)** (สำหรับวัสดุ) | - | `UPDATE` | `CART_ITEM` | `CART_ITEM.qty` | อัปเดตจำนวนในตะกร้า (ครุภัณฑ์ล็อกค่าเป็น `1 ชิ้น` เสมอ) |
| 10 | **ปุ่มลบรายการออกจากตะกร้า (`🗑️`)** | - | `DELETE` | `CART_ITEM` | `DELETE FROM CART_ITEM WHERE id = ...` | ลบแถวนั้นออกจากตาราง `CART_ITEM` |
| 11 | **ปุ่ม "⏳ จองคิวแทน"** (กรณีครุภัณฑ์/วัสดุคงทนถูกยืมตัดหน้า) | - | `INSERT` + `DELETE` | `QUEUE`, `CART_ITEM` | `INSERT INTO QUEUE (...)` และ `DELETE FROM CART_ITEM` | ย้ายรายการที่ถูกยืมตัดหน้าไปเข้าคิวจอง (`QUEUE`) แทน (เฉพาะครุภัณฑ์และวัสดุคงทน) |
| 12 | **ปุ่ม "🗑️ ลบรายการที่หมดทั้งหมด"** | - | `DELETE` | `cart` (Session/LocalStorage) | ลบรายการที่ไม่พร้อมยืมออกจากตะกร้า | ล้างรายการที่ถูกยืมตัดหน้าออกจากตะกร้าทั้งหมดในคลิกเดียว |
| 13 | **แถบสรุปท้ายตะกร้า** (รวม X รายการ, Y ชิ้น, กำหนดคืนภายใน Z วัน) | `p_cart_summary` | `SELECT (COUNT, SUM, MAX)` | `cart`, `DURABLE_MATERIAL`, `EQUIPMENT` | `COUNT(c.item_id)`, `SUM(c.qty)`, `MAX(.max_borrow_days)` | คำนวณจำนวนรวมและวันยืมสูงสุดจากรายการในตะกร้า |
| 14 | **ปุ่ม "ยืนยันส่งคำขอยืม →"** | `p_cart_submit-btn` | `Navigate` | - | ส่งต่อไปหน้า `page-request-form.html` | นำข้อมูลในตะกร้าไปสร้าง `BORROW_REQUEST` และ `BORROW_ITEM` ในขั้นตอนถัดไป |

---

## ผลการตรวจสอบความสอดคล้อง (Validation)
- 📌 **โครงสร้างตาราง:** ใน ERD 13 ตารางไม่มีตาราง `CART` เนื่องจากตะกร้าของระบบ YuemDee ถูกออกแบบให้เก็บชั่วคราวผ่าน **Browser Session / LocalStorage (`request.session['cart']`)** ก่อนที่ผู้ใช้จะกดยืนยันสร้างคำขอจริงในตาราง `BORROW_REQUEST` และ `BORROW_ITEM`
- ✅ **การจองคิว (`QUEUE`):** จำกัดปุ่ม `"⏳ จองคิวแทน"` เฉพาะ **ครุภัณฑ์ (`EQUIPMENT`)** และ **วัสดุคงทน (`DURABLE_MATERIAL`)** เท่านั้น (วัสดุสิ้นเปลือง `MATERIAL` ที่หมดจะขึ้นข้อความ `วัสดุหมดคลัง (ไม่ต้องคืน)` ไม่สามารถกดจองคิวได้ ตรงตามโครงสร้างตาราง `QUEUE` ใน ERD ที่ไม่มี `material_id`)
- ✅ **ความถูกต้องของฟิลด์ `QUEUE`:** ฟังก์ชัน `p_cart_convertToQueue` บันทึกแยก `equipment_id` / `durable_material_id` และกำหนด `status = "WAITING"` ครบถ้วนตาม ERD
- ✅ **การตรวจสอบสต็อกก่อนขอยืม:** ตรวจสอบทั้งกรณีของหมด (`qty_available <= 0`) และกรณีจำนวนในตะกร้าเกินสต็อกคงเหลือจริง (`c.qty > item.qty_available`) ก่อนนำส่งไปยังหน้าฟอร์มคำขอ

