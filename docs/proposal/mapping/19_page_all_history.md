# Field Mapping: `page-all-history.html` (ประวัติการยืม-คืนทั้งระบบ)

> **หน้าจอ:** ดูประวัติการยืม-คืนทั้งระบบ รองรับ 2 มุมมอง (ตามใบคำขอ และติดตามสิ่งของรายชิ้น)  
> **ไฟล์ต้นทาง:** `pages/page-all-history.html`  
> **ผู้ใช้งาน:** 👷 เจ้าหน้าที่ (Staff)  
> **Use Case:** UC-19  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **ช่องค้นหาและตัวกรอง** | | | |
| ค้นหาคำขอ/ชื่อ นศ./รหัสชิ้น (`p_all_history_q`) | Input (Search) | `BORROW_REQUEST.id`, `USER.name`, `STUDENT.student_id`, `EQUIPMENT.asset_tag` | ค้นหาประวัติ |
| กรองตามสถานะ (`p_all_history_status`) | Filter Select | `BORROW_REQUEST.status`, `EQUIPMENT.status` | กรองตามสถานะคำขอหรือสถานะครุภัณฑ์ |
| กรองตามช่วงวันที่ (`from` / `to`) | Input (Date) | `BORROW_REQUEST.created_at` | กรองช่วงเวลาการยืม |
| **แท็บที่ 1: มุมมองตามคำขอ (Request Orders)** | | | |
| เลขที่คำขอ | Text | `BORROW_REQUEST.id` | รหัสคำขอ |
| ผู้ยืม (นักศึกษา) | Text | `USER.name`, `STUDENT.student_id` | ชื่อและรหัสนักศึกษา |
| รายการสิ่งของ | Text | `ITEM.name`, `BORROW_ITEM.qty`, `ITEM.unit` | รายการพัสดุในคำขอ |
| วันที่ยืม / กำหนดคืน | Datetime / Date | `BORROW_REQUEST.created_at`, `BORROW_ITEM.due_date` | วันที่ทำรายการและกำหนดคืน |
| สถานะคำขอ | Badge | `BORROW_REQUEST.status` | `BORROWING`, `RETURNED`, `REJECTED` ฯลฯ |
| **แท็บที่ 2: ติดตามสิ่งของรายชิ้น (Item & Unit Tracking)** | | | |
| ชื่อสิ่งของ | Text | `ITEM.name` | ชื่อพัสดุ |
| รหัสประจำชิ้น (Asset Tag) | Text (Badge) | `EQUIPMENT.asset_tag` | รหัสครุภัณฑ์เฉพาะชิ้น |
| สถานะของชิ้นนั้น | Badge | `EQUIPMENT.status` | `BORROWED`, `AVAILABLE`, `DAMAGED`, `LOST` |
| ผู้ที่กำลังยืมอยู่ | Text | `USER.name`, `STUDENT.student_id`, `STUDENT.phone` | ข้อมูลนักศึกษาที่กำลังถือครองของชิ้นนี้ |
| สถานที่ใช้งานปัจจุบันที่แจ้งย้าย | Text | `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at` | ตำแหน่งที่ตั้งล่าสุดที่ นศ. แจ้งย้ายไว้ |
| วันครบกำหนดคืน | Date | `BORROW_ITEM.due_date` | กำหนดคืนของชิ้นนี้ |
| **หน้าต่างเจาะลึกรายละเอียด (Detail Modal)** | | | |
| ผู้อนุมัติปล่อยของ | Text | `STAFF.user_id -> USER.name` | ชื่อเจ้าหน้าที่ผู้ปล่อยของ (`approved_by`) |
| วันเวลาที่อนุมัติ | Datetime | `BORROW_REQUEST.approved_at` | เวลาที่กดปล่อยของ |
| ผู้ตรวจรับคืน | Text | `STAFF.user_id -> USER.name` | ชื่อเจ้าหน้าที่ผู้ตรวจรับคืน (`inspected_by`) |
| วันเวลาที่ตรวจรับคืน | Datetime | `RETURN_REQUEST.returned_at` | เวลาที่รับคืนสำเร็จ |
| รูปถ่ายสภาพก่อนยืม / ตอนส่งคืน | Images | `BORROW_ITEM.initial_photo`, `RETURN_REQUEST.return_photo` | รูปเปรียบเทียบสภาพ |
| ยอดค่าปรับและยอดชดใช้สูญหาย | Text | `RETURN_REQUEST.custom_fine`, `RETURN_REQUEST.fine_paid`, `RETURN_ITEM.lost_compensation`, `RETURN_ITEM.lost_paid` | รายละเอียดการเงิน |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- ตัวสลับแท็บ (Tab Switcher): Client-side UI State

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `BORROW_REQUEST`
- `BORROW_ITEM`
- `RETURN_REQUEST`
- `RETURN_ITEM`
- `ITEM`
- `EQUIPMENT`
- `USER`
- `STUDENT`
- `STAFF`
