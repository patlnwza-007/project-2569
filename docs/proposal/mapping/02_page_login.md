# Field Mapping: `page-login.html` (เข้าสู่ระบบ)

> **หน้าจอ:** หน้าเข้าสู่ระบบ (Dual Authentication) และ Onboarding เข้าใช้งานครั้งแรก  
> **ไฟล์ต้นทาง:** `pages/page-login.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา, 👷 เจ้าหน้าที่, 👑 ผู้ดูแลระบบ  
> **Use Case:** UC-15  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **ช่องทางที่ 1: UBU SSO (Google OAuth)** | | | |
| อีเมล Google OAuth (@ubu.ac.th) | Auth Callback | `USER.email` | ยืนยันตัวตนผ่านบริการ UBU Single Sign-On |
| ชื่อ-นามสกุลจาก SSO | Auth Callback | `USER.name` | ดึงชื่อผู้ใช้จากระบบ Google OAuth มาเก็บ |
| ตรวจสอบสถานะระงับสิทธิ์ | Logic Check | `USER.blocked`, `USER.block_reason` | หาก `blocked = true` ระบบปฏิเสธการล็อกอินและแจ้งเตือนเหตุผล |
| บันทึกเวลาเข้าสู่ระบบครั้งแรก | Timestamp | `USER.first_login` | บันทึกเมื่อล็อกอินครั้งแรกในระบบ |
| บันทึกเวลาเข้าสู่ระบบล่าสุด | Timestamp | `USER.last_login` | ปรับปรุงทุกครั้งที่ล็อกอินสำเร็จ |
| **First-time Onboarding Modal (นศ. เข้าครั้งแรก)** | | | |
| รหัสนักศึกษา 11 หลัก | Input (Text) | `STUDENT.student_id` | บังคับกรอกในการเข้าสู่ระบบครั้งแรก (UC-15) |
| เบอร์โทรศัพท์ติดต่อ 10 หลัก | Input (Text) | `STUDENT.phone` | บังคับกรอกในการเข้าสู่ระบบครั้งแรก |
| ชื่อ-นามสกุล | Input (Text) | `USER.name` | ตรวจสอบ/แก้ไขชื่อตนเอง |
| **ช่องทางที่ 2: Django Admin Local** | | | |
| ชื่อผู้ใช้งาน (Username) | Input (Text) | `ADMIN.username` | ยืนยันตัวตนผู้ดูแลระบบ |
| เข้าสู่ระบบล่าสุด | Timestamp | `ADMIN.last_login` | ปรับปรุงเวลาล็อกอินล่าสุดของแอดมิน |

---

## 2. ตาราง ERD ที่เกี่ยวข้อง
- `USER`
- `STUDENT`
- `ADMIN`
