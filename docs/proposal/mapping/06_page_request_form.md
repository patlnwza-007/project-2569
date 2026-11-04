# หน้าที่ 6: ยืนยันส่งคำขอยืม (`page-request-form.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `USER`, `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT`, `BORROW_REQUEST`, `BORROW_ITEM`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: การตรวจสอบสิทธิ์และสรุปรายการที่จะยืม
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **กล่องแจ้งเตือนถูกระงับสิทธิ์การยืม** | `p_request_form_blocked-notice` | `SELECT` | `USER` | `USER.blocked`, `USER.block_reason` | หาก `blocked = true` จะซ่อนฟอร์มและแจ้งเตือนเหตุผลที่ถูกระงับสิทธิ์ |
| 2 | **รายการสิ่งของที่เลือกยืม/เบิก** (รูป, ชื่อ, ประเภท, รหัสครุภัณฑ์) | `p_request_form_summary` | `SELECT` | `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | `.image`, `.name`, `.unit`, `EQUIPMENT.asset_tag` | ดึงข้อมูลสิ่งของตามรายการที่อยู่ในตะกร้า |
| 3 | **จำนวนที่ยืม/เบิกแต่ละรายการ** | - | `SELECT` | ตะกร้า (Cart) | `qty` | จำนวนชิ้นที่ระบุมาจากหน้าตะกร้า |
| 4 | **ช่องอัปโหลดรูปถ่ายสภาพสิ่งของ/ตำหนิเดิมก่อนยืม (รายชิ้น)** | `p_rf_photo_[index]` | `INSERT` | `BORROW_ITEM` | `BORROW_ITEM.initial_photo` | หลักฐานภาพถ่ายสภาพของ ณ จุดรับของ (On-the-Spot Inspection) เพื่อคุ้มครองนักศึกษา |

---

### ส่วนที่ 2: ฟอร์มกรอกเหตุผลและขอยืมกรณีพิเศษ
| ลำดับ | ชื่อช่อง / ช่องกรอกข้อมูล (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 5 | **เหตุผลความจำเป็นในการขอยืม/เบิก** <span class="text-red-500">*</span> | `p_request_form_reason` | `INSERT` | `BORROW_REQUEST` | `BORROW_REQUEST.reason` | ข้อความระบุความจำเป็นในการนำของไปใช้งานจริง |
| 6 | **กล่องติ๊ก: ขอยืมระยะยาวเป็นกรณีพิเศษ** | `p_request_form_is_special` | `INSERT` | `BORROW_REQUEST` | `BORROW_REQUEST.is_special` | ค่าบูลีน (`true` / `false`) |
| 7 | **วันที่ประสงค์จะส่งคืน (กรณีพิเศษ)** | `p_request_form_custom_due` | `INSERT` | `BORROW_REQUEST` | `BORROW_REQUEST.due_date` | บันทึกเป็นกำหนดคืนของใบคำขอ (เจ้าหน้าที่มีสิทธิ์ปรับลดได้ตอนอนุมัติ) |
| 8 | **เหตุผลความจำเป็นในการขอยืมระยะยาวพิเศษ** | `p_request_form_special_reason` | `INSERT` | `BORROW_REQUEST` | `BORROW_REQUEST.reason` | รวมข้อความประกอบเข้ากับฟิลด์ `reason` |

---

### ส่วนที่ 3: ปุ่มดำเนินการ (Action Buttons & Submission)
| ลำดับ | ปุ่มกดบนหน้าจอ (UI) | การทำงาน (CRUD) | ตาราง (Table) | ผลลัพธ์ในฐานข้อมูล |
| :---: | :--- | :---: | :--- | :--- |
| 9 | **ปุ่ม "← แก้ไขตะกร้า"** | `Navigate` | - | ย้อนกลับไปหน้า `page-cart.html` โดยยังคงข้อมูลในตะกร้าไว้ |
| 10 | **ปุ่ม "ยืนยันส่งคำขอ →"** | `INSERT` | `BORROW_REQUEST` | สร้างใบคำขอใหม่: `user_id = S001`, `reason`, `due_date`, `is_special`, `status = 'PENDING'`, `created_at = NOW()` |
| 11 | **(ระบบสร้างอัตโนมัติ)** | `INSERT` | `BORROW_ITEM` | บันทึกรายการสิ่งของลงใบคำขอ: แยกบันทึก `material_id`, `durable_material_id`, หรือ `equipment_id` พร้อม `qty` และ `initial_photo` |
| 12 | **(ระบบล้างข้อมูล)** | `DELETE` | ตะกร้า (Cart) | ล้างข้อมูลในตะกร้าหลังส่งคำขอสำเร็จ และนำทางไปยังหน้าหลัก `page-request-list.html` |

---

## ผลการตรวจสอบความสอดคล้อง (Validation)
- ✅ **เหตุผลการยืม (`reason`):** กรณียืมปกติกำหนดค่าเริ่มต้นเป็น `"ยืมใช้งานปกติ"` เพื่อความสะดวกรวดเร็วของนักศึกษา และหากติ๊ก "ขอยืมระยะยาวเป็นกรณีพิเศษ" จะมีกล่องข้อความขยายออกมาให้พิมพ์เหตุผลความจำเป็น พร้อมนำไปบันทึกลงฟิลด์ `BORROW_REQUEST.reason`
- ✅ **กำหนดส่งคืน (`due_date`):** คำนวณวันส่งคืนให้อัตโนมัติ (`วันปัจจุบัน + max_borrow_days`) หากเป็นการยืมปกติ และใช้วันที่ที่ระบุหากเป็นกรณีพิเศษ โดยบันทึกลงในคอลัมน์ `BORROW_REQUEST.due_date` โดยตรงตาม ERD
- ✅ **แยก Foreign Key ใน `BORROW_ITEM`:** แตกข้อมูลสิ่งของในตะกร้าลง `BORROW_ITEM` โดยระบุ `material_id`, `durable_material_id`, หรือ `equipment_id` ตรงตามตารางปลายทางใน ERD
- ✅ **แก้ไขบั๊ก `unitLabel`:** ปรับเป็น `${i?.unit || 'ชิ้น'}` แสดงหน่วยนับของสิ่งของถูกต้องทุกประเภท

