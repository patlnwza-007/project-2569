# หน้าที่ 3: รายการวัสดุและครุภัณฑ์ (`page-item-list.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT`, `REVIEW`, `CART_ITEM`, `QUEUE`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: แถบค้นหา ตัวกรอง และการเรียงลำดับ (Search, Filter & Sort Toolbar)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **ปุ่มตะกร้ายืมของ + ตัวเลขจำนวนในตะกร้า** | `p_item_list_cart_badge` | `SELECT (SUM)` | `CART_ITEM` | `SUM(CART_ITEM.qty)` | รวมจำนวนชิ้นในตะกร้าของ `user_id` ปัจจุบัน |
| 2 | **ช่องค้นหาชื่อสิ่งของ / รหัสครุภัณฑ์** | `p_item_list_q` | `SELECT (WHERE LIKE)` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.name`, `EQUIPMENT.asset_tag` | ค้นหาจากชื่อสิ่งของ หรือรหัสครุภัณฑ์ประจำชิ้น |
| 3 | **ตัวกรอง: หมวดหมู่** | `p_item_list_f-cat` | `SELECT (DISTINCT)` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.category` | กรองตามหมวดหมู่สิ่งของ |
| 4 | **ตัวกรอง: ประเภทสิ่งของ** + **ปุ่มทางลัด (Quick Tags)** | `p_item_list_f-type` | `SELECT` | แยกตามตาราง | ตาราง `EQUIPMENT` / `DURABLE_MATERIAL` / `MATERIAL` | เลือกดูเฉพาะครุภัณฑ์, วัสดุคงทน, หรือวัสดุสิ้นเปลือง |
| 5 | **ตัวกรอง: สถานะ** (พร้อมให้ยืม / ถูกยืมหมด / ไม่พร้อมใช้งาน) | `p_item_list_f-status` | `SELECT (WHERE)` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.base_status`, `.qty_available` | เช็คสถานะว่างพร้อมยืม หรือถูกยืมหมด |
| 6 | **ตัวเลือก: เรียงลำดับ** (คงเหลือมาก-น้อย / ชื่อ ก-ฮ / ยืมได้นานสุด) | `p_item_list_sort` | `ORDER BY` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.qty_available`, `.name`, `.max_borrow_days` | จัดเรียงลำดับการแสดงผลการ์ด |

---

### ส่วนที่ 2: การ์ดแสดงรายการสิ่งของ (Grid Card — แยกตามประเภท)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :---: | :--- | :--- | :--- |
| 7 | **รูปภาพ / ไอคอนสิ่งของ** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.image` | แสดงรูปภาพหรือไอคอนประจำสิ่งของ |
| 8 | **ป้ายสถานะบนการ์ด** (พร้อมยืม / ถูกยืมไปแล้ว / ชำรุด) | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.base_status`, `.qty_available` | ครุภัณฑ์ดูจาก `EQUIPMENT.base_status` (`AVAILABLE`, `BORROWED`, `DAMAGED`) |
| 9 | **ป้ายประเภทสิ่งของ** (ครุภัณฑ์ / วัสดุคงทน / วัสดุเบิกใช้) | `SELECT (Derived)` | แยกตามตาราง | มาจากตาราง `EQUIPMENT` / `DURABLE_MATERIAL` / `MATERIAL` | ระบุประเภทตามตารางต้นทาง |
| 10 | **รหัสครุภัณฑ์ประจำชิ้น (`🏷️ UBU-EQ-...`)** | `SELECT` | `EQUIPMENT` | `EQUIPMENT.asset_tag` | แสดงเฉพาะการ์ดครุภัณฑ์รายชิ้น |
| 11 | **คะแนนดาวเฉลี่ย (`⭐ 5.0`) และจำนวนรีวิว (`(X รีวิว)`)** | `SELECT (AVG, COUNT)` | `REVIEW` | `AVG(REVIEW.rating)`, `COUNT(REVIEW.id)` | คำนวณสดจากตาราง `REVIEW` ของครุภัณฑ์หรือวัสดุคงทนนั้น |
| 12 | **ชื่อสิ่งของ** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.name` | ชื่อวัสดุหรือครุภัณฑ์ |
| 13 | **หมวดหมู่ (`🏷️ โสตทัศนูปกรณ์`)** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.category` | หมวดหมู่ของสิ่งของ |
| 14 | **ตำแหน่งจัดเก็บ (`📍 ห้อง EN6-101 · ตู้ A1 ชั้น 2`)** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.location` | พิกัดตู้และชั้นวางในคลัง |
| 15 | **ระยะเวลายืมสูงสุด (`⏱️ สูงสุด X วัน` / `♾️ เบิกใช้แล้วหมดไป`)** | `SELECT` | `DURABLE_MATERIAL`, `EQUIPMENT` | `.max_borrow_days` | วัสดุสิ้นเปลือง (`MATERIAL`) ไม่ต้องคืน จึงแสดงว่าเบิกใช้แล้วหมดไป |
| 16 | **จำนวนคงเหลือในคลัง (`X / Y หน่วย`) + แถบ Progress Bar** | `SELECT` + `Derived` | `MATERIAL`, `DURABLE_MATERIAL` | `.qty_available`, `.qty_total`, `.unit` | เปอร์เซ็นต์หลอดคำนวณจาก `(qty_available / qty_total) × 100` |
| 17 | **ปุ่ม "⏳ จองคิวรหัสนี้ / จองคิวล่วงหน้า"** (เมื่อถูกยืมหมด) | `INSERT` | `QUEUE` | `user_id`, `equipment_id` หรือ `durable_material_id`, `status='WAITING'`, `joined_at` | จองคิวได้เฉพาะ **ครุภัณฑ์** และ **วัสดุคงทน** ที่ต้องนำมาคืน |

---

### ส่วนที่ 3: หน้าต่างเลือกจำนวนใส่ตะกร้า (Borrow / Issue Modal)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลใน Modal | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 18 | **ข้อมูลสิ่งของในหัว Modal** (รูป, ชื่อ, หมวดหมู่, ตำแหน่ง, คงเหลือ/รหัสครุภัณฑ์) | `p_modal_img`, `p_modal_name`, `p_modal_pos`, `p_modal_stock`, `p_modal_tag_badge` | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.image`, `.name`, `.category`, `.location`, `.qty_available`, `EQUIPMENT.asset_tag` | แสดงข้อมูลสรุปของชิ้นที่กำลังจะหยิบใส่ตะกร้า |
| 19 | **ช่องกรอก/ปุ่มปรับจำนวนที่ต้องการยืมหรือเบิก (`-` / `+`)** | `p_modal_qty_input` | `INSERT` / `UPDATE` | `CART_ITEM` | `CART_ITEM.qty` | ครุภัณฑ์ล็อกค่าเป็น `1` เสมอ, วัสดุปรับได้ไม่เกิน `qty_available` |
| 20 | **ปุ่มยืนยัน "🛒 ใส่ตะกร้า / บันทึกจำนวนในตะกร้า"** | `p_modal_confirm_btn` | `INSERT` / `UPDATE` | `CART_ITEM` | `user_id`, `material_id` / `durable_material_id` / `equipment_id`, `qty`, `added_at` | บันทึกรายการลงตาราง `CART_ITEM` |
| 21 | **ปุ่ม "🗑️ นำรายการนี้ออกจากตะกร้า"** | `p_modal_remove_wrap` | `DELETE` | `CART_ITEM` | `DELETE FROM CART_ITEM WHERE ...` | แสดงเฉพาะกรณีที่สิ่งของชิ้นนี้อยู่ในตะกร้าแล้ว |

---

## ผลการตรวจสอบความสอดคล้อง (Validation)
- ✅ อ้างอิง `category` และ `location` จากตาราง `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` โดยตรงตาม ERD
- ✅ จำกัดปุ่ม `"⏳ จองคิว"` เฉพาะ **ครุภัณฑ์ (`EQUIPMENT`)** และ **วัสดุคงทน (`DURABLE_MATERIAL`)** เท่านั้น (วัสดุสิ้นเปลือง `MATERIAL` แสดงป้าย `วัสดุหมดคลัง (ไม่ต้องคืน)` ตรงกับตาราง `QUEUE` ใน ERD ที่ไม่มี `material_id`)
- ✅ ทุกช่องข้อมูลในหน้า `page-item-list.html` ตรงกับ ERD ครบ 100%

