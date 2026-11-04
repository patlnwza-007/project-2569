# หน้าที่ 4: รายละเอียดวัสดุ/ครุภัณฑ์ และรีวิวการใช้งาน (`page-item-detail.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา (`student`) และ เจ้าหน้าที่คลัง (`staff`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT`, `BORROW_REQUEST`, `BORROW_ITEM`, `REVIEW`, `USER`, `CART_ITEM`, `QUEUE`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: การ์ดแสดงข้อมูลหลักด้านบน (Top Showcase Card — ซ้าย & ขวา)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :---: | :--- | :--- | :--- |
| 1 | **ป้ายรหัสครุภัณฑ์ (`🏷️ UBU-EQ-...`)** | `SELECT` | `EQUIPMENT` | `EQUIPMENT.asset_tag` | แสดงเฉพาะกรณีเป็นครุภัณฑ์ (`equipment`) |
| 2 | **ป้ายสถานะสิ่งของ** (พร้อมให้ยืม / ถูกยืมไปแล้ว / ชำรุด) | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.base_status`, `.qty_available` | แสดงสถานะความพร้อมใช้งานปัจจุบัน |
| 3 | **รูปภาพ / ไอคอนสิ่งของขนาดใหญ่** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.image` | รูปภาพหรือไอคอนประจำสิ่งของ |
| 4 | **📍 ตำแหน่งจัดเก็บในคลัง** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.location` | ตำแหน่งห้อง ตู้ และชั้นวางในคลัง |
| 5 | **🚨 ที่ตั้ง/ที่อยู่ปัจจุบัน (กรณีถูกยืมอยู่และมีการแจ้งย้าย)** | `SELECT` | `BORROW_ITEM`, `BORROW_REQUEST` | `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at`, `BORROW_REQUEST.user_id` | ดึงจากใบคำขอที่กำลังยืม (`status = 'BORROWING'`) ของครุภัณฑ์ชิ้นนี้ |
| 6 | **หมวดหมู่สิ่งของ** และ **ป้ายประเภทสิ่งของ** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.category` | แยกประเภทตามตารางต้นทาง |
| 7 | **ชื่อสิ่งของ (`h1`)** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.name` | ชื่อครุภัณฑ์ วัสดุคงทน หรือวัสดุสิ้นเปลือง |
| 8 | **คะแนนดาวเฉลี่ย (`⭐ X.X`) และจำนวนรีวิว (`(N รีวิว)`)** | `SELECT (AVG, COUNT)` | `REVIEW` | `AVG(REVIEW.rating)`, `COUNT(REVIEW.id)` | แสดงเฉพาะครุภัณฑ์ (`EQUIPMENT`) และวัสดุคงทน (`DURABLE_MATERIAL`) |
| 9 | **ราคาจัดซื้อเดิม (มูลค่าทางบัญชี)** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.purchase_price` | ใช้คำนวณค่าชดใช้กรณีสูญหาย |
| 10 | **จำนวนคงเหลือพร้อมเบิก/ยืม** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.qty_available`, `.qty_total`, `.unit` | ครุภัณฑ์รายชิ้นมีจำนวน `1/1 ชิ้น` |
| 11 | **กล่องสรุป 3 ช่อง: ยืมได้สูงสุด / หน่วยนับ / อัตราค่าปรับต่อวัน** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.max_borrow_days`, `.unit`, `.fine_rate_per_day` | วัสดุสิ้นเปลืองไม่มีวันยืมสูงสุดและไม่มีค่าปรับ |
| 12 | **ปุ่มหลัก: "🛒 ขอยืม / ยืมวัสดุคงทน / เบิกวัสดุลงตะกร้า"** | `INSERT` / `UPDATE` | `CART_ITEM` | `user_id`, `equipment_id` / `durable_material_id` / `material_id`, `qty`, `added_at` | เปิด Modal เลือกจำนวนและบันทึกลงตาราง `CART_ITEM` |
| 13 | **ปุ่มหลัก: "⏳ จองคิวครุภัณฑ์รหัสนี้ / จองคิวล่วงหน้า"** (เมื่อถูกยืมหมด) | `INSERT` | `QUEUE` | `user_id`, `equipment_id` หรือ `durable_material_id`, `status='WAITING'`, `joined_at` | จองคิวได้เฉพาะ `EQUIPMENT` และ `DURABLE_MATERIAL` |

---

### ส่วนที่ 2: แท็บที่ 1 — รายละเอียดและคุณลักษณะ (`details` Tab)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :---: | :--- | :--- | :--- |
| 14 | **รายละเอียดและหมายเหตุสภาพสิ่งของ (`description`)** | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.description` | คำอธิบายคุณลักษณะและหมายเหตุสภาพเครื่อง |
| 15 | **การ์ดคุณลักษณะ 4 กล่อง** (รหัสอ้างอิง / ราคาจัดซื้อ / ระยะเวลายืมสูงสุด / อัตราค่าปรับต่อวัน) | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `id` หรือ `asset_tag`, `.purchase_price`, `.max_borrow_days`, `.fine_rate_per_day` | แสดงข้อมูลจำเพาะจากตารางสิ่งของโดยตรง |

---

### ส่วนที่ 3: แท็บที่ 2 — รีวิวการใช้งานจริง (`reviews` Tab — เฉพาะครุภัณฑ์และวัสดุคงทน)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :---: | :--- | :--- | :--- |
| 16 | **คะแนนเฉลี่ยรวม (`X.X`) และจำนวนรีวิวทั้งหมด** | `SELECT (AVG, COUNT)` | `REVIEW` | `AVG(REVIEW.rating)`, `COUNT(REVIEW.id)` | คำนวณจากรีวิวทั้งหมดของสิ่งของชิ้นนั้น |
| 17 | **ปุ่มกรองตามระดับดาว (5 ดาว – 1 ดาว พร้อมตัวเลขนับจำนวน)** | `SELECT (COUNT GROUP BY)` | `REVIEW` | `COUNT(REVIEW.id) GROUP BY REVIEW.rating` | กรองดูรีวิวตามระดับคะแนนดาว |
| 18 | **ชื่อผู้รีวิว (`student_name`)** | `SELECT (JOIN)` | `REVIEW` $\rightarrow$ `USER` | `USER.name` (เชื่อมผ่าน `REVIEW.user_id`) | แสดงชื่อนักศึกษาผู้เขียนรีวิว |
| 19 | **วันที่เขียนรีวิว** | `SELECT` | `REVIEW` | `REVIEW.created_at` | วันเวลาที่ส่งผลการประเมินหลังคืนของ |
| 20 | **คะแนนดาวของรีวิวนั้น (`★ 1–5`)** | `SELECT` | `REVIEW` | `REVIEW.rating` | คะแนนความพึงพอใจ 1–5 ดาว |
| 21 | **ข้อความความคิดเห็น (`comment`)** | `SELECT` | `REVIEW` | `REVIEW.comment` | ข้อเสนอแนะหรือรีวิวสภาพจากการใช้งานจริง |
| 22 | **รหัสครุภัณฑ์ที่ยืมในรีวิวนั้น** | `SELECT` | `REVIEW` $\rightarrow$ `EQUIPMENT` | `EQUIPMENT.asset_tag` | อ้างอิงผ่าน `REVIEW.equipment_id` |

---

## ผลการตรวจสอบความสอดคล้อง (Validation)
- ✅ ซ่อนแท็บรีวิวและปิดการจองคิวสำหรับ **วัสดุสิ้นเปลือง (`MATERIAL`)** ให้ตรงกับตาราง `REVIEW` และ `QUEUE` ใน ERD (ที่มีเฉพาะ `equipment_id` และ `durable_material_id`)
- ✅ แสดงอัตราค่าปรับรายวัน (`fine_rate_per_day`) แทนข้อความ `"พร้อมใช้ 100%"` ที่เคย Hardcode ไว้
- ✅ ลบข้อความ `"· ส่งคืนตรงเวลา"` ในการ์ดรีวิวออก แสดงเฉพาะ `REVIEW.created_at` ตามคอลัมน์จริงใน ERD
- ✅ ทุกช่องข้อมูลในหน้า `page-item-detail.html` ตรงกับ ERD ครบ 100%

