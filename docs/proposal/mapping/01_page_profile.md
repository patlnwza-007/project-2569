# หน้าที่ 1: โปรไฟล์ส่วนตัว (`page-profile.html`)
**บทบาทผู้ใช้งาน:** นักศึกษา (`student`)  
**ตารางฐานข้อมูลที่เกี่ยวข้อง:** `USER` (1 ตาราง)

---

## ตารางจับคู่ฟิลด์ข้อมูล (Field-Level Data Mapping)

| ลำดับ | ชื่อช่องบนหน้าจอ (UI Label) | รหัส Element (`id`) | ประเภท UI | การทำงาน (CRUD) | ตาราง (Table) | ฟิลด์ในฐานข้อมูล (Column) | ชนิดข้อมูล | หมายเหตุ |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| 1 | **รหัสนักศึกษา** | `p_profile_f-id` | Input (Disabled) | `SELECT` (Read) | `USER` | `USER.id` | `VARCHAR(20) PK` | ดึงรหัสประจำตัวผู้ใช้อัตโนมัติ (แก้ไขไม่ได้) |
| 2 | **ชื่อ-นามสกุล** | `p_profile_f-name` | Input (Disabled) | `SELECT` (Read) | `USER` | `USER.name` | `VARCHAR(100)` | ดึงชื่อจากบัญชี UBU SSO (แก้ไขไม่ได้) |
| 3 | **อีเมล** | `p_profile_f-email` | Input (Disabled) | `SELECT` (Read) | `USER` | `USER.email` | `VARCHAR(100) UK` | ดึงอีเมล `@ubu.ac.th` จาก UBU SSO (แก้ไขไม่ได้) |
| 4 | **เบอร์โทรศัพท์ \*** | `p_profile_f-phone` | Input (Text) | `SELECT` / `UPDATE` | `USER` | `USER.phone` | `VARCHAR(20)` | นักศึกษากรอกและกดปุ่ม **"บันทึกข้อมูล"** เพื่ออัปเดตลง `USER.phone` |
| 5 | **เข้าสู่ระบบครั้งแรก** | `p_profile_f-first` | Text Display | `SELECT` (Read) | `USER` | `USER.first_login` | `DATETIME` | แสดงวันเวลาที่ล็อกอินเข้าใช้งานระบบครั้งแรก |
| 6 | **เข้าสู่ระบบล่าสุด** | `p_profile_f-last` | Text Display | `SELECT` (Read) | `USER` | `USER.last_login` | `DATETIME` | แสดงวันเวลาที่ล็อกอินเข้าใช้งานระบบครั้งล่าสุด |

---

## ผลการตรวจสอบความสอดคล้อง (Validation)
- ✅ **ทุกช่องในหน้า `page-profile.html` (ครบทั้ง 6 ช่อง)** มีคอลัมน์รองรับในตาราง `USER` ครบ 100%
- ✅ **ไม่มีข้อมูลที่สร้างลอยขึ้นมาเอง** นอกเหนือจากตาราง `USER`
