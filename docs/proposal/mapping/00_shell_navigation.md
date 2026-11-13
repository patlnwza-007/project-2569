# Shell Navigation Mapping (Top Bar & Side Bar)

> **หน้าจอ:** โครงร่างหลักของระบบ (Mockup Shell Frame)  
> **ไฟล์ต้นทาง:** `index.html`, `shared.js`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student), 👷 เจ้าหน้าที่ (Staff), 👑 ผู้ดูแลระบบ (Admin)  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. Top Bar (แถบด้านบน)

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| โลโก้และชื่อระบบ "YuemDee" | Text / Brand | *ไม่มีใน ERD* | ข้อความคงที่ (Static Branding) |
| สโลแกน "ระบบยืม-คืนพัสดุออนไลน์" | Text | *ไม่มีใน ERD* | ข้อความคงที่ |
| ป้ายแสดงบทบาท (Role Badge) | Badge | `USER` + `STUDENT` / `STAFF` / `ADMIN` | แสดงบทบาทปัจจุบัน (`นักศึกษา`, `เจ้าหน้าที่`, `ผู้ดูแลระบบ`) ที่ได้จากการตรวจสอบสิทธิ์ |
| ชื่อผู้ใช้งาน (User Name) | Text | `USER.name` (นศ./จนท.) หรือ `ADMIN.name` (แอดมิน) | แสดงชื่อ-นามสกุลของผู้ใช้งานที่กำลังล็อกอินอยู่ |
| เมนูสลับบทบาท (Role Switcher) | Dropdown | *ไม่มีใน ERD* | เครื่องมือสำหรับทดสอบบน Mockup เท่านั้น |
| ปุ่มออกจากระบบ (Logout) | Button | *ไม่มีใน ERD* | ล้างสถานะการเข้าสู่ระบบ (Session Logout) |

---

## 2. Side Bar (เมนูด้านข้าง)

### 2.1 เมนูสำหรับนักศึกษา (Student Menu)
| เมนูบน Side Bar | ลิงก์หน้า | แหล่งข้อมูลใน ERD | คำอธิบาย / ตัวเลขแจ้งเตือน (Badge) |
|---|---|---|---|
| 🏠 หน้าหลัก | `page-request-list.html` | `BORROW_REQUEST`, `BORROW_ITEM` | รายการคำขอและสิ่งของที่กำลังยืมของตนเอง |
| 👤 โปรไฟล์ส่วนตัว | `page-profile.html` | `USER`, `STUDENT` | ข้อมูลบัญชีและข้อมูลติดต่อ |
| 📋 รายการวัสดุ/ครุภัณฑ์ | `page-item-list.html` | `ITEM`, `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | แคตตาล็อกพัสดุ 3 ประเภท |
| 🛒 ตะกร้า | `page-cart.html` | `CART`, `CART_ITEM` | จำนวนในตะกร้าคำนวณจาก `SUM(CART_ITEM.qty)` ของ `CART.user_id` |
| ⏳ คิวของฉัน | `page-queue-list.html` | `QUEUE` | จำนวนคิวคำนวณจาก `COUNT(QUEUE.id)` ที่ `user_id` มี `status IN ('WAITING', 'NOTIFIED')` |
| 📜 ประวัติการยืม | `page-history.html` | `BORROW_REQUEST`, `BORROW_ITEM`, `REVIEW` | ประวัติการยืมในอดีต |
| 🛠️ แจ้งอุปกรณ์ชำรุด | `page-report-damage.html` | `DAMAGE_REPORT` | ฟอร์มและประวัติแจ้งชำรุด |
| 💡 เสนอแนะสิ่งของ | `page-suggestion.html` | `SUGGESTION` | ฟอร์มและประวัติการเสนอแนะสิ่งของ |

### 2.2 เมนูสำหรับเจ้าหน้าที่ (Staff Menu)
| เมนูบน Side Bar | ลิงก์หน้า | แหล่งข้อมูลใน ERD | คำอธิบาย / ตัวเลขแจ้งเตือน (Badge) |
|---|---|---|---|
| 📊 แดชบอร์ด | `page-staff-dashboard.html` | `BORROW_REQUEST`, `RETURN_REQUEST`, `EQUIPMENT`, `DAMAGE_REPORT` | สรุปภาพรวมสถิติระบบ |
| ✅ คำขอรออนุมัติ | `page-pending-requests.html` | `BORROW_REQUEST` | ตัวเลขนับจาก `COUNT(BORROW_REQUEST.id)` ที่ `status = 'PENDING'` |
| ↩️ รับคืนครุภัณฑ์ | `page-return-list.html` | `RETURN_REQUEST` | ตัวเลขนับจาก `COUNT(RETURN_REQUEST.id)` ที่ `status = 'RETURN_PENDING'` |
| ⚠️ ครุภัณฑ์เสียหาย | `page-damaged-equipment.html` | `EQUIPMENT`, `DAMAGE_REPORT` | ตัวเลขนับจาก `COUNT(EQUIPMENT.status = 'DAMAGED')` + `COUNT(DAMAGE_REPORT.status = 'PENDING')` |
| 📜 ประวัติทั้งระบบ | `page-all-history.html` | `BORROW_REQUEST`, `BORROW_ITEM`, `EQUIPMENT` | ประวัติใบคำขอและติดตามรายชิ้น |
| 📦 จัดการคลังสิ่งของ | `page-item-overview.html` | `ITEM`, `MATERIAL`, `DURABLE_MATERIAL`, `EQUIPMENT` | จัดการสต็อกและสถานะพัสดุ |
| 🎓 รายชื่อนักศึกษา | `page-student-list.html` | `USER`, `STUDENT`, `BORROW_REQUEST` | รายชื่อนักศึกษาและประวัติยืม (Read-Only) |
| 💡 คำเสนอแนะสิ่งของ | `page-suggestion-review.html` | `SUGGESTION` | ตัวเลขนับจาก `COUNT(SUGGESTION.id)` ที่ `status = 'SUBMITTED'` |
| 🧾 รายการจัดซื้อ | `page-purchase-add.html` | `PURCHASE_PLAN`, `SUGGESTION` | แผนการจัดซื้อพัสดุ |
| 📤 ส่งออกรายงาน | `page-report-export.html` | `BORROW_REQUEST`, `RETURN_ITEM`, `ITEM` | ส่งออกรายงาน PDF/CSV |

### 2.3 เมนูสำหรับผู้ดูแลระบบ (Admin Menu)
| เมนูบน Side Bar | ลิงก์หน้า | แหล่งข้อมูลใน ERD | คำอธิบาย / ตัวเลขแจ้งเตือน (Badge) |
|---|---|---|---|
| 👥 จัดการบัญชีและสิทธิ์ผู้ใช้ | `page-user-list.html` | `USER`, `STUDENT`, `STAFF`, `ADMIN` | จัดการบัญชี ระงับสิทธิ์ และ Role Override |
| 📤 ส่งออกรายชื่อผู้ใช้งาน (CSV) | `page-personnel-export.html` | `USER`, `STAFF`, `ADMIN` | ส่งออกไฟล์รายชื่อบุคลากร |

