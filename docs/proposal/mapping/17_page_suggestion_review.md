# หน้าที่ 17: พิจารณาข้อเสนอแนะและแผนจัดซื้อ (`page-suggestion-review.html` & `page-purchase-add.html`)
**บทบาทผู้ใช้งาน:** เจ้าหน้าที่พัสดุ (`staff`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `SUGGESTION`, `PURCHASE_PLAN`, `USER`

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

### ส่วนที่ 1: ตรวจสอบข้อเสนอแนะของนักศึกษา (`page-suggestion-review.html`)
| ลำดับ | ชื่อช่อง / ส่วนแสดงผลบนหน้าจอ (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **ตัวกรองสถานะข้อเสนอแนะ** | `p_suggestion_review_f-status` | `SELECT` | `SUGGESTION` | `SUGGESTION.status` | กรองตาม 3 สถานะ: `SUBMITTED`, `ACKNOWLEDGED`, `PURCHASE_PLAN` |
| 2 | **รายการข้อเสนอแนะ** (ชื่อสิ่งของ, เหตุผล, ผู้เสนอ, วันที่) | `p_suggestion_review_rows` | `SELECT` | `SUGGESTION`, `USER` | `.name`, `.detail`, `user_id`, `created_at` | ดึงข้อมูลข้อเสนอแนะจากนักศึกษา |
| 3 | **ปุ่ม "✓ รับทราบ"** | `p_suggestion_review_markAcknowledge` | `UPDATE` | `SUGGESTION` | `SUGGESTION.status = 'ACKNOWLEDGED'` | เปลี่ยนสถานะเป็นรับทราบแล้ว |
| 4 | **ปุ่ม "🛒 เพิ่มเข้าแผนจัดซื้อ"** | `p_suggestion_review_addToPurchasePlan` | `UPDATE` / `INSERT` | `SUGGESTION`, `PURCHASE_PLAN` | 1. อัปเดต `SUGGESTION.status = 'PURCHASE_PLAN'`<br>2. เพิ่มลงตาราง `PURCHASE_PLAN` โดยผูก `suggestion_id = SUGGESTION.id` |

---

### ส่วนที่ 2: บันทึกแผนการจัดซื้อพัสดุ/ครุภัณฑ์ (`page-purchase-add.html`)
| ลำดับ | ชื่อช่อง / ช่องกรอกข้อมูล (UI) | รหัส Element (`id`) | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | หมายเหตุ |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| 5 | **ชื่อสิ่งของที่จะจัดซื้อ** <span class="text-red-500">*</span> | `p_purchase_add_f-name` | `INSERT` | `PURCHASE_PLAN` | `PURCHASE_PLAN.name` | ระบุชื่อพัสดุ/ครุภัณฑ์ที่จะจัดซื้อ |
| 6 | **รายละเอียดการจัดซื้อ** | `p_purchase_add_f-detail` | `INSERT` | `PURCHASE_PLAN` | `PURCHASE_PLAN.detail` | สเปก หรือเหตุผลการจัดซื้อ |
| 7 | **รหัสข้อเสนอแนะที่เชื่อมโยง** | - | `INSERT` | `PURCHASE_PLAN` | `PURCHASE_PLAN.suggestion_id` | รหัสอ้างอิง `SUGGESTION.id` (หรือ `NULL` หากเจ้าหน้าที่เพิ่มเอง) |
| 8 | **ผู้บันทึกแผนจัดซื้อ** | - | `INSERT` | `PURCHASE_PLAN` | `PURCHASE_PLAN.created_by` | รหัสเจ้าหน้าที่ผู้บันทึก (`USER.id`) |
| 9 | **วันเวลาที่บันทึก** | - | `INSERT` | `PURCHASE_PLAN` | `PURCHASE_PLAN.created_at` | วันที่ทำรายการบันทึก |

---

## ผลการตรวจสอบความสอดคล้องกับ ERD และการแก้ไข
- ✅ **เชื่อมโยง `suggestion_id` ระหว่าง 2 ตาราง:** เมื่อกดย้ายเข้าแผนจัดซื้อ จะส่ง `suggestion_id` ไปผูกกับตาราง `PURCHASE_PLAN` ทันที
- ✅ **บันทึก `created_by`:** จัดเก็บรหัสผู้บันทึกแผนจัดซื้อลง `PURCHASE_PLAN.created_by` ตรงตาม Foreign Key สู่ตาราง `USER`
- ✅ **สถานะ 3 สถานะใน `SUGGESTION` ครบถ้วน:** `SUBMITTED`, `ACKNOWLEDGED`, `PURCHASE_PLAN`
