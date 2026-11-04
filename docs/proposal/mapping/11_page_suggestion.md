# หน้าที่ 11: เสนอแนะจัดซื้อสิ่งของใหม่ (`page-suggestion.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `SUGGESTION`, `USER`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: ฟอร์มส่งข้อเสนอแนะจัดซื้อสิ่งของใหม่
| ลำดับ | ชื่อช่อง / ช่องกรอกข้อมูล (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **ชื่อสิ่งของที่ต้องการเสนอแนะ** <span class="text-red-500">*</span> | `p_suggestion_f-name` | `INSERT` | `SUGGESTION` | `SUGGESTION.name` | เช่น กล้อง DSLR, เลนส์มุมกว้าง, ขาตั้งกล้อง |
| 2 | **รายละเอียด / เหตุผลที่ควรจัดซื้อ** <span class="text-red-500">*</span> | `p_suggestion_f-detail` | `INSERT` | `SUGGESTION` | `SUGGESTION.detail` | ระบุความจำเป็นและประโยชน์ในการจัดซื้อ |
| 3 | **ผู้เสนอแนะ (บันทึกอัตโนมัติ)** | - | `INSERT` | `SUGGESTION` | `SUGGESTION.user_id` | รหัสผู้ใช้งานปัจจุบัน (`user_id = S001`) |
| 4 | **สถานะเริ่มต้น (บันทึกอัตโนมัติ)** | - | `INSERT` | `SUGGESTION` | `SUGGESTION.status` | ค่าเริ่มต้นเมื่อส่งคือ `'SUBMITTED'` |
| 5 | **วันเวลาที่ส่ง (บันทึกอัตโนมัติ)** | - | `INSERT` | `SUGGESTION` | `SUGGESTION.created_at` | วันที่และเวลาที่บันทึกข้อมูล |

---

### ส่วนที่ 2: ประวัติข้อเสนอแนะของผู้ใช้
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 6 | **รายการข้อเสนอแนะย้อนหลัง** | `p_suggestion_rows` | `SELECT` | `SUGGESTION` | `id`, `name`, `detail`, `created_at` | กรองตาม `SUGGESTION.user_id = S001` |
| 7 | **ป้ายสถานะข้อเสนอแนะ (Badge)** | - | `SELECT` | `SUGGESTION` | `SUGGESTION.status` | แสดง 3 สถานะตาม ERD:<br>1. `SUBMITTED` (ส่งข้อเสนอแนะแล้ว)<br>2. `ACKNOWLEDGED` (เจ้าหน้าที่รับทราบแล้ว)<br>3. `PURCHASE_PLAN` (เพิ่มในแผนจัดซื้อแล้ว) |
| 8 | **กล่องแจ้งสถานะไม่มีข้อมูล (Empty State)** | - | `SELECT` | `SUGGESTION` | - | แสดงเมื่อยังไม่เคยมีประวัติการเสนอแนะ |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **เชื่อมโยง `user_id`:** บันทึกและดึงข้อมูลผ่าน `SUGGESTION.user_id` ให้สอดคล้องกับ ERD
- ✅ **สถานะ 3 สถานะตรงกับ ERD 100%:** `SUBMITTED`, `ACKNOWLEDGED`, `PURCHASE_PLAN`
- ✅ **ความสมบูรณ์ของการเชื่อมโยงแผนจัดซื้อ:** เมื่อสถานะเป็น `PURCHASE_PLAN` สามารถเชื่อมต่อกับตาราง `PURCHASE_PLAN.suggestion_id` ของเจ้าหน้าที่ได้
