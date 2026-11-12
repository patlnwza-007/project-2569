# Field Mapping: `page-notify-return.html` (แจ้งส่งคืนสิ่งของ)

> **หน้าจอ:** ฟอร์มแจ้งส่งคืนสิ่งของที่เคาน์เตอร์ รองรับการคืนบางส่วน และแนบรูปถ่ายหลักฐาน  
> **ไฟล์ต้นทาง:** `pages/page-notify-return.html`  
> **ผู้ใช้งาน:** 🎓 นักศึกษา (Student)  
> **Use Case:** UC-08  
> **ตาราง ERD อ้างอิง:** [00_erd_reference.md](./00_erd_reference.md)

---

## 1. รายการฟิลด์และองค์ประกอบบนหน้าจอ

| ฟิลด์ / องค์ประกอบบนหน้าจอ | ประเภท UI | ตาราง.คอลัมน์ (ERD) | คำอธิบาย / ตรรกะการดึงข้อมูล |
|---|---|---|---|
| **ข้อมูลคำขอยืมเดิม** | | | |
| เลขที่คำขอยืม | Text | `BORROW_REQUEST.id` | รหัสคำขอที่กำลังจะแจ้งคืน |
| วันที่เริ่มยืมและกำหนดคืน | Text | `BORROW_REQUEST.created_at`, `BORROW_ITEM.due_date` | ข้อมูลกำหนดคืนเดิม |
| **รายการสิ่งของที่จะแจ้งคืน (Checkbox เลือกคืน)** | | | |
| Checkbox เลือกคืนรายชิ้น | Checkbox | กรองเพื่อบันทึก `RETURN_ITEM` | รองรับการคืนบางส่วน (Partial Return) |
| ข้อมูลสิ่งของ | Text / Image | `ITEM.name`, `ITEM.image`, `ITEM.unit`, `ITEM.purchase_price` | ข้อมูลสิ่งของ |
| รหัสครุภัณฑ์ | Text (Badge) | `EQUIPMENT.asset_tag` | รหัส Asset Tag ชิ้นที่คืน |
| จำนวนที่กำลังยืมอยู่ | Text | `BORROW_ITEM.qty` | จำนวนที่อยู่ในความรับผิดชอบ |
| รูปถ่ายสภาพก่อนยืม (อ้างอิง) | Image | `BORROW_ITEM.initial_photo` | รูปที่ถ่ายไว้ตอนรับของ เพื่อเทียบสภาพ |
| ตัวเลือกแจ้งสภาพที่นำมาคืน | Radio / Select | `RETURN_ITEM.condition_status` | นักศึกษาแจ้งสภาพเบื้องต้น (`NORMAL`, `DAMAGED`, `LOST`) |
| **หลักฐานและบันทึกการส่งคืน** | | | |
| อัปโหลดรูปถ่ายหลักฐานการส่งคืน | Input (File) | `RETURN_REQUEST.return_photo` | บังคับแนบรูปสภาพสิ่งของ ณ จุดส่งคืนเคาน์เตอร์ |
| หมายเหตุเพิ่มเติมการส่งคืน | Input (Textarea) | `RETURN_REQUEST.note` | ระบุหมายเหตุเพิ่มเติม (ถ้ามี) |
| **การบันทึกข้อมูลเมื่อกดยืนยัน** | | | |
| ใบแจ้งคืน | Table Record | `RETURN_REQUEST` | บันทึก `borrow_request_id`, `status = 'RETURN_PENDING'`, `return_photo`, `note`, `created_at = NOW()` |
| รายการสิ่งของที่คืน | Table Record | `RETURN_ITEM` | บันทึกแถว `return_request_id`, `borrow_item_id`, `qty_returned`, `condition_status` |
| อัปเดตสถานะคำขอยืมหลัก | Status Update | `BORROW_REQUEST.status` | ปรับสถานะคำขอเป็น `'RETURN_PENDING'` (รอเจ้าหน้าที่ตรวจรับคืน) |

---

## 2. ฟิลด์บนหน้าจอที่ไม่ถูกเก็บใน ERD (หรือเป็นสถานะชั่วคราวบน UI)
- ช่องกรอกอาการชำรุด/สาเหตุสูญหายชั่วคราวในหน้าจอ (`p_notify_dmg_desc`, `p_notify_lost_desc`): ใน ERD ฉบับปัจจุบันตัดฟิลด์ข้อความอาการในส่วนนี้ออก โดยนำไปรวมไว้ที่ `RETURN_REQUEST.note` หรือใช้วิธีแจ้งผ่าน `DAMAGE_REPORT` (UC-38)

---

## 3. ตาราง ERD ที่เกี่ยวข้อง
- `BORROW_REQUEST`
- `BORROW_ITEM`
- `ITEM`
- `EQUIPMENT`
- `RETURN_REQUEST`
- `RETURN_ITEM`
