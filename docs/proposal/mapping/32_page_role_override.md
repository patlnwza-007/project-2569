# Field Mapping: `page-role-override.html` (กำหนดบทบาทพิเศษ / Role Override)

> **หน้าจอ:** กำหนดสิทธิ์บทบาทเฉพาะบุคคล มีผลเหนือกว่าบทบาทเริ่มต้นจาก UBU SSO  
> **ไฟล์ต้นทาง:** `pages/page-role-override.html`  
> **ผู้ใช้งาน:** 👑 ผู้ดูแลระบบ (Admin)  
> **Use Case:** UC-33  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **ข้อมูลผู้ใช้เป้าหมาย** | | | |
| ชื่อ - นามสกุล | Text | `USER.name` | ดึงชื่อผู้ใช้ที่เลือกมากำหนดสิทธิ์ |
| อีเมลเป้าหมาย | Input (Text) / Read-Only | `USER.email` | อีเมล @ubu.ac.th ของผู้ใช้ (รองรับการกรอกอีเมลใหม่ที่ยังไม่เคย login) |
| บทบาทเริ่มต้นจาก UBU SSO | Badge | `STUDENT` / `STAFF` | บทบาทที่ได้รับตามระบบทะเบียนมหาวิทยาลัย |
| **ฟอร์มการกำหนดบทบาทพิเศษ (Role Override)** | | | |
| บทบาทที่ต้องการกำหนด | Select / Radio | จัดการแถว `STAFF` | เลือกกำหนดเป็น "เจ้าหน้าที่" หรือคืนสิทธิ์เป็น "บทบาทเริ่มต้น" |
| เหตุผลการกำหนดบทบาท | Input (Textarea) | `STAFF.override_reason` | ระบุเหตุผล เช่น แต่งตั้งเป็นนักศึกษาช่วยงานคลังพัสดุ |
| **การบันทึกข้อมูลเมื่อกดยืนยัน** | | | |
| กรณีแต่งตั้งเป็นเจ้าหน้าที่ | Record Insert/Update | `STAFF` | สร้างหรืออัปเดตแถวใน `STAFF`:<br>- `user_id = USER.id`<br>- `is_override = true`<br>- `override_reason = ข้อความที่กรอก`<br>- `assigned_by = ADMIN.id`<br>- `assigned_at = NOW()` |
| กรณียกเลิก Role Override | Record Delete | ลบ `STAFF` | ลบแถวใน `STAFF` เพื่อให้กลับไปใช้บทบาทเดิมจาก UBU SSO |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- `p_role_override_f-role`: Client-side input สำหรับเลือกบทบาท

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `USER`
- `STAFF`
- `ADMIN`
- `STUDENT`
