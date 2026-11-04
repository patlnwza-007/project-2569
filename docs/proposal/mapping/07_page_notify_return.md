# หน้าที่ 7: รายการครุภัณฑ์ที่ต้องส่งคืน / แจ้งส่งคืน (`page-notify-return.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา / ผู้ยืม (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `BORROW_REQUEST`, `BORROW_ITEM`, `EQUIPMENT`, `DURABLE_MATERIAL`, `RETURN_REQUEST`, `RETURN_ITEM`, `REVIEW`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: สรุปรายการคำขอและการแจ้งเตือนค่าปรับเกินกำหนด
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :--- :| :--- | :--- | :--- |
| 1 | **กล่องเตือนคำขอเกินกำหนดคืน** (จำนวนคำขอ, จำนวนวันเกินกำหนด, อัตราค่าปรับ) | `p_notify_return_overdue_alert` | `SELECT` | `BORROW_REQUEST`, `EQUIPMENT`, `DURABLE_MATERIAL` | `BORROW_REQUEST.due_date`, `fine_rate_per_day` | คำนวณวันเกินกำหนดจาก `due_date < วันปัจจุบัน` และคิดค่าปรับตามอัตราของสิ่งของที่ยังไม่คืน |
| 2 | **จำนวนคำขอที่กำลังถือครอง** | `p_notify_return_count_badge` | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.status` | นับคำขอที่มีสถานะ `BORROWING` หรือ `RETURN_PENDING` |
| 3 | **เลขที่คำขอและสถานะคำขอ** | `p_nr_card_[rid]` | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.id`, `BORROW_REQUEST.status` | แสดงเลขที่คำขอ `#104`, `#105` และสถานะ เช่น `กำลังยืม` หรือ `รอเจ้าหน้าที่ตรวจรับคืน` |
| 4 | **กำหนดส่งคืนและวันที่ยืม** | - | `SELECT` | `BORROW_REQUEST` | `BORROW_REQUEST.due_date`, `BORROW_REQUEST.created_at` | แสดงวันที่ครบกำหนดคืนและวันที่ได้รับของ |
| 5 | **ยอดค่าปรับค้างชำระของคำขอ** | - | `SELECT` | `BORROW_REQUEST`, `EQUIPMENT`, `DURABLE_MATERIAL` | `BORROW_REQUEST.due_date`, `fine_rate_per_day` | แสดงผล `จำนวนวันเกิน × อัตราค่าปรับต่อวัน` (เฉพาะคำขอที่เกินกำหนด) |

---

### ส่วนที่ 2: รายการสิ่งของที่ต้องคืน และการระบุสภาพตอนส่งคืน
| ลำดับ | ชื่อช่อง / ช่องกรอกข้อมูล (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :--- :| :--- | :--- | :--- |
| 6 | **กล่องเลือกสิ่งของที่จะส่งคืน (Checkbox)** | `input[type="checkbox"]` | `SELECT` | `BORROW_ITEM` | `BORROW_ITEM.id`, `qty` | รองรับการคืนแบบแยกคืนบางส่วน (Partial Return) สิ่งของสิ้นเปลือง (`material`) จะไม่ถูกนำมาแสดงในหน้านี้ |
| 7 | **ข้อมูลสิ่งของ (รูป, ชื่อ, เลขครุภัณฑ์, หน่วยนับ)** | - | `SELECT` | `EQUIPMENT`, `DURABLE_MATERIAL` | `.name`, `.image`, `.unit`, `EQUIPMENT.asset_tag` | ดึงข้อมูลสิ่งของและเลขรหัสครุภัณฑ์ประจำชิ้น |
| 8 | **ปุ่ม "📷 ดูรูปตอนรับของ"** | - | `SELECT` | `BORROW_ITEM` | `BORROW_ITEM.initial_photo` | เปิด Modal แสดงรูปถ่ายหลักฐานสภาพของตอนรับ เพื่อเปรียบเทียบก่อนคืน |
| 9 | **ตัวเลือกสภาพสิ่งของที่จะส่งคืน** (ปกติ / ชำรุด / สูญหาย) | ปุ่มตัวเลือกสภาพ | `INSERT` / `UPDATE` | `RETURN_ITEM` | `RETURN_ITEM.condition_status` | ค่า Enum: `NORMAL`, `DAMAGED`, `LOST` |
| 10 | **ช่องระบุอาการชำรุด/มีตำหนิ** | `input[text]` | `INSERT` / `UPDATE` | `RETURN_REQUEST` / `RETURN_ITEM` | `RETURN_REQUEST.note` | แสดงขึ้นมาเมื่อเลือกสภาพ `DAMAGED` เพื่อแจ้งเจ้าหน้าที่ล่วงหน้า |
| 11 | **การแจ้งสูญหายและยอดค่าชดใช้** | `input[text]` | `INSERT` / `UPDATE` | `RETURN_ITEM`, `EQUIPMENT`, `DURABLE_MATERIAL` | `RETURN_ITEM.lost_compensation`, `purchase_price` | แสดงราคาจัดซื้อเดิม และบันทึกยอดค่าชดใช้ที่ต้องชำระเมื่อเลือก `LOST` |
| 12 | **รายการสิ่งของที่คืนเข้าคลังแล้ว (รอบก่อนหน้า)** | - | `SELECT` | `RETURN_ITEM`, `BORROW_ITEM` | `RETURN_ITEM.qty_returned`, `returned_at` | แสดงขีดฆ่าพร้อมวันที่ตรวจรับเสร็จสิ้น |
| 13 | **ปุ่ม "⭐ ประเมินชิ้นนี้"** | - | `SELECT` / `Navigate` | `REVIEW` | `REVIEW.id`, `rating`, `comment` | หากคืนแล้วและยังไม่ได้ประเมิน สามารถกดไปหน้า `page-evaluation.html` ได้ |

---

### ส่วนที่ 3: ปุ่มดำเนินการ (Action Buttons & Submission)
| ลำดับ | ปุ่มกดบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ผลลัพธ์ในฐานข้อมูล |
| :---: | :--- | :---: | :--- | :--- |
| 14 | **ปุ่ม "✓ เลือกทั้งหมด"** | `Client State` | - | สลับการติ๊กเลือกสิ่งของทุกชิ้นในคำขอ |
| 15 | **ปุ่ม "✕ ยกเลิกการแจ้ง"** (กรณีแจ้งไว้แล้วแต่เปลี่ยนใจ) | `UPDATE` | `BORROW_REQUEST`, `RETURN_REQUEST` | ปรับสถานะรายการกลับเป็นปกติ และหากไม่มีรายการค้างคืนจะปรับ `BORROW_REQUEST.status` กลับเป็น `BORROWING` |
| 16 | **ปุ่ม "↩️ แจ้งส่งคืน [X] ชิ้นที่เลือก"** | `INSERT` / `UPDATE` | `BORROW_REQUEST`, `RETURN_REQUEST`, `RETURN_ITEM` | 1. อัปเดต `BORROW_REQUEST.status = 'RETURN_PENDING'`<br>2. บันทึกข้อมูลใบแจ้งคืน `RETURN_REQUEST` (`status = 'RETURN_PENDING'`)<br>3. บันทึกรายการส่งคืน `RETURN_ITEM` (`condition_status = 'NORMAL' / 'DAMAGED' / 'LOST'`, `lost_compensation`) |

---

## การตรวจสอบความสอดคล้องกับ ERD และบั๊กที่พบในหน้านี้

1. **บั๊กการคำนวณอัตราค่าปรับต่อวัน (`getFineRatePerDay()`):**
   - **ปัญหา:** ในบรรทัดที่ 210 และ 451 มีการเรียก `getFineRatePerDay()` โดยลืมส่งอาร์กิวเมนต์ `r` (คำขอ) เข้าไป ทำให้ระบบไปหยิบค่าปรับกลาง `20 บาท/วัน` เสมอ แทนที่จะคิดคำนวณตาม `fine_rate_per_day` ของครุภัณฑ์ชิ้นที่ยังค้างส่งในคำขอนั้น (เช่น คำขอ #104 มีกล้องค้างส่ง 1 ตัว อัตราค่าปรับต้องเป็น 40 บาท/วัน)
   - **แนวทางแก้ไข:** เปลี่ยนเป็น `getFineRatePerDay(r)` ให้ถูกต้อง

2. **ความสอดคล้องของ Enum สภาพสิ่งของ (`condition_status`):**
   - **ปัญหา:** ใน ERD กำหนดค่า Enum ของ `RETURN_ITEM.condition_status` เป็นตัวพิมพ์ใหญ่คือ `NORMAL`, `DAMAGED`, `LOST` แต่ในโค้ด mockup เดิมใช้ค่าตัวพิมพ์เล็ก (`normal`, `damaged`, `lost`)
   - **แนวทางแก้ไข:** ปรับค่าที่จัดเก็บและเช็คเงื่อนไขให้รองรับ `NORMAL`, `DAMAGED`, `LOST` ตามมาตรฐาน ERD

3. **ความสมบูรณ์ของค่าชดใช้กรณีสูญหาย (`lost_compensation`):**
   - **ปัญหา:** หน้าเว็บแสดงราคาเดิมแต่ไม่ได้ผูกชื่อฟิลด์กับ `purchase_price` และ `lost_compensation` อย่างชัดเจน
   - **แนวทางแก้ไข:** ให้อ่านจาก `item.purchase_price || item.price` และเมื่อผู้ใช้แจ้งสูญหาย ให้ส่งค่ายอดชดใช้นี้บันทึกลง `RETURN_ITEM.lost_compensation`

4. **การบันทึกข้อมูลตาราง `RETURN_REQUEST` และ `RETURN_ITEM` เมื่อกดแจ้งส่งคืน:**
   - **ปัญหา:** โค้ดเดิมอัปเดตเฉพาะแฟล็ก `it.pending_return = true` ในคำขอยืม แต่ไม่ได้จำลองการสร้าง Record ลงตาราง `RETURN_REQUEST` และ `RETURN_ITEM`
   - **แนวทางแก้ไข:** ในฟังก์ชัน `p_notify_return_submitPending()` เพิ่มการบันทึก Record ในตารางจำลอง `return_requests` และ `return_items` ให้ตรงกับ ERD 100% พร้อมคงแฟล็กสถานะเดิมไว้เพื่อความเข้ากันได้กับหน้า Staff
