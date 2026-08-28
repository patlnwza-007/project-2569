# YuemDee · บันทึกการปรับปรุงและเพิ่มฟังก์ชัน Mockup (mockup_changes_log.md)

> **วันที่ปรับปรุง:** 25 สิงหาคม 2569
> **ขอบเขต:** สรุปการปรับปรุงระบบ Mockup (`mockup/yuemdee/`) เพื่อนำไปใช้อัปเดตเอกสารสเปก Functional Requirements (FR), Use Case Description, และ PlantUML Diagrams ใน Claude หรือขั้นตอนถัดไป

---

## 📌 สรุปฟังก์ชันใหม่ที่เพิ่มเข้ามาใน Mockup (4 ฟังก์ชันหลัก)

### 1. ระบบแนบหลักฐานภาพถ่ายสภาพสิ่งของตอนยืม-คืน (Photo Evidence)
* **เหตุผลการปรับปรุง:** ป้องกันข้อพิพาทเรื่องสิ่งของชำรุดก่อนยืมหรือพังในมือผู้ยืมคนล่าสุด
* **พฤติกรรมใน Mockup:**
  * **ตอนยืม (รับของ):** ในหน้า [page-confirm-pickup.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-confirm-pickup.html) เพิ่มช่องถ่ายรูป/แนบรูปหลักฐานสภาพสิ่งของก่อนรับ (`pickup_photo`) เพื่อยืนยันรอยตำหนิเดิมที่มีก่อนยืม
  * **ตอนคืน (ส่งของ):** ในหน้า [page-notify-return.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-notify-return.html) เพิ่มช่องถ่ายรูป/แนบรูปหลักฐานสภาพครุภัณฑ์ ณ วันคืน (`return_photo`)
  * **ฝั่งเจ้าหน้าที่:** ในหน้า [page-return-list.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-return-list.html) แสดงภาพถ่ายเปรียบเทียบสภาพสิ่งของ "ตอนยืม (รับของ) vs ตอนคืน (ส่งมอบ)" ให้เจ้าหน้าที่ตรวจก่อนกดรับคืน

### 2. นักศึกษาบังคับเลือกรหัสครุภัณฑ์รายชิ้นเอง และจองคิวรายชิ้นได้ (Mandatory Serial Selection & Unit Queueing)
* **เหตุผลการปรับปรุง:** เปลี่ยนจากการสุ่ม/ยืมแบบนับจำนวนรวม มาเป็นบังคับให้นักศึกษาเห็นและกดเลือก **"รหัสครุภัณฑ์รายชิ้น (Asset Tag)"** (เช่น `UBU-EQ-001-01`, `UBU-EQ-001-02`) ได้เองตามสภาพ คะแนนดาว และรีวิวความเห็นจากผู้ยืมคนก่อนหน้า พร้อมทั้งเปิดให้จองคิวเฉพาะชิ้นกรณีชิ้นนั้นถูกยืมอยู่
* **พฤติกรรมใน Mockup:**
  * **หน้ารายการสิ่งของ (`page-item-list.html`):** ปุ่มการ์ดครุภัณฑ์เปลี่ยนเป็น `🏷️ เลือกรหัสชิ้นที่จะยืม →` บังคับพานักศึกษาไปหน้ารายละเอียดสิ่งของก่อนเพิ่มลงตะกร้าเสมอ
  * **หน้ารายละเอียดสิ่งของ (`page-item-detail.html`):** แสดงรายการรหัส Asset Tag แต่ละชิ้น พร้อมคะแนนดาว ⭐ โดยข้อความรีวิวแบบละเอียดจะซ่อนไว้เป็นค่าเริ่มต้น (กดดูผ่านปุ่ม `💬 ดูรีวิว (N)`) ชิ้นที่พร้อมยืมจะมีปุ่ม `+ เลือกชิ้นนี้ลงตะกร้า` และชิ้นที่ถูกยืมอยู่จะมีปุ่ม `⏳ จองคิวรหัสนี้`
  * **หน้าตะกร้า (`page-cart.html`):** แสดงป้ายน้ำเงินเด่นชัด `🏷️ ยืมครุภัณฑ์รหัสชิ้น: UBU-EQ-001-01` บนทุกรายการ หากมีรายการครุภัณฑ์ที่ยังไม่ได้เลือกรหัสชิ้น ระบบจะแสดงป้ายเตือนสีแดง และไม่อนุญาตให้กดส่งคำขอจนกว่าจะไปเลือกรหัสชิ้นให้เรียบร้อย
  * **หน้าคำขอรออนุมัติฝั่ง Staff (`page-pending-requests.html`):** เจ้าหน้าที่ **ไม่ต้องกดเลือกรหัสชิ้นที่จะจ่ายเองอีกต่อไป** โดยระบบจะแสดงป้ายรหัส Asset Tag ที่นักศึกษาเลือกยืมมาโดยตรง เจ้าหน้าที่มีหน้าที่เพียงกดปุ่ม **`✓ อนุมัติ`** เพื่อยืนยันตัดจ่ายตรงตามชิ้นที่นักศึกษาเลือก
  * **หน้าคิวของฉัน (`page-queue-list.html`):** แสดงป้ายรหัส Asset Tag ที่นักศึกษาต่อคิวอยู่อย่างชัดเจน และเมื่อถึงคิวจะโอนเข้าตะกร้าพร้อมรหัสชิ้นเดิมที่จองไว้โดยอัตโนมัติ

### 3. ระบบรีวิวและให้คะแนนสภาพสิ่งของรายชิ้น (Item-Level Review & Rating)
* **เหตุผลการปรับปรุง:** ให้ผู้ที่เคยยืมสิ่งของชิ้นนั้นจริงๆ มาช่วยกันเขียนรีวิวและให้คะแนนดาวสภาพการใช้งาน (1-5 ดาว) เพื่อให้ผู้ยืมคนถัดไปใช้ประกอบการตัดสินใจ
* **พฤติกรรมใน Mockup:**
  * ในหน้า [page-evaluation.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-evaluation.html) เมื่อนักศึกษาทำแบบประเมินหลังคืนสำเร็จ ระบบจะบันทึกคะแนนดาวและรีวิวลงในรหัส Asset Tag ของครุภัณฑ์ชิ้นนั้นๆ โดยอัตโนมัติ
  * ในหน้า [page-item-detail.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-item-detail.html) แสดงประวัติรีวิวและคะแนนดาวเฉลี่ยใต้รหัสครุภัณฑ์รายชิ้นแต่ละชิ้น

### 4. ระบบคำนวณและตั้งค่าค่าปรับยืมเกินกำหนด (Overdue Fine & Manual Fine Override)
* **เหตุผลการปรับปรุง:** สร้างแรงจูงใจให้นักศึกษาส่งคืนตรงเวลา โดย Staff/Admin สามารถกำหนดอัตราค่าปรับมาตรฐานรวม และสามารถตั้งค่า/ปรับลด/ยกเว้นค่าปรับเป็นรายกรณีตามดุลยพินิจได้
* **พฤติกรรมใน Mockup:**
  * **การตั้งค่ากลาง:** ในหน้า [page-warehouse-settings.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-warehouse-settings.html) เพิ่มแท็บ **"💸 อัตราค่าปรับ"** ให้ Staff/Admin กรอกและบันทึกอัตราค่าปรับ (บาท/วัน) (ค่าเริ่มต้น: 10 บาท/วัน)
  * **การปรับแก้รายกรณี (ฝั่งเจ้าหน้าที่):** ในหน้า [page-return-list.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-return-list.html) เพิ่มปุ่ม **`✏️ แก้ไขยอดเงิน`** ให้เจ้าหน้าที่กดพิมพ์แก้ไขยอดเงินค่าปรับเองได้ตามเหมาะสม (เช่น กรอก `0` เพื่อลดหย่อน/ยกเว้นค่าปรับ) พร้อมปุ่มสลับสถานะ **`[✓ ชำระค่าปรับแล้ว]`**
  * **ฝั่งนักศึกษา:** ในหน้า [page-request-list.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-request-list.html) แสดงยอดคำนวณค่าปรับค้างชำระอย่างชัดเจน โดยอ้างอิงตามยอดอัตราคำนวณหรือยอดที่เจ้าหน้าที่แก้ไขให้โดยตรง

---

## 🛠️ สรุปไฟล์ที่ได้รับการแก้ไขใน `mockup/yuemdee/`

| ไฟล์ | รายละเอียดการปรับแก้ |
|---|---|
| [shared.js](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/shared.js) | • เพิ่ม `SEED_SETTINGS` (ค่าปรับ 10 บาท/วัน)<br>• เพิ่ม `rating` และ `reviews` ใน `SEED_UNITS`<br>• เพิ่ม helper functions: `getFineRatePerDay()`, `calculateOverdueFine()`, `getOverdueDays()`, `getUnitsByItemId()`, `addUnitReview()` |
| [page-item-detail.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-item-detail.html) | • แสดงรายการครุภัณฑ์รายชิ้น (Asset Tag)<br>• แสดงคะแนนดาวและประวัติรีวิวสภาพแต่ละชิ้น<br>• ปุ่มเลือกครุภัณฑ์เฉพาะชิ้นลงตะกร้า (`p_item_detail_addToCartWithSerial`) |
| [page-confirm-pickup.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-confirm-pickup.html) | • เพิ่มช่องถ่ายรูป/แนบรูปภาพหลักฐานสภาพก่อนรับ (`pickup_photo`) |
| [page-notify-return.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-notify-return.html) | • เพิ่มช่องถ่ายรูป/แนบรูปภาพหลักฐานสภาพ ณ วันคืน (`return_photo`) |
| [page-request-list.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-request-list.html) | • แสดงยอดค่าปรับค้างชำระกรณีเกินกำหนดคืน (`calculateOverdueFine`) |
| [page-evaluation.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-evaluation.html) | • ส่งบันทึกคะแนนดาวและรีวิวลงในรหัสครุภัณฑ์ Asset Tag รายชิ้นเมื่อทำแบบประเมินสำเร็จ |
| [page-warehouse-settings.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-warehouse-settings.html) | • เพิ่มแท็บ **"💸 อัตราค่าปรับ"** สำหรับตั้งค่าอัตราค่าปรับยืมเกินกำหนด (บาท/วัน) |
| [page-return-list.html](file:///Users/macservice/Desktop/project_lasted/project-2569/mockup/yuemdee/pages/page-return-list.html) | • แสดงกล่องเปรียบเทียบภาพถ่ายสภาพก่อนยืม vs หลังคืน<br>• แสดงยอดคำนวณค่าปรับเกินกำหนด<br>• ปุ่มบันทึกสลับสถานะการชำระค่าปรับ (`p_return_list_toggleFinePaid`) |

---

## 📋 คำแนะนำสำหรับนำไปอัปเดตเอกสารต่อใน Claude

เมื่อนำข้อมูลไปอัปเดตเอกสารสเปกอื่นๆ สามารถอัปเดตได้ดังนี้:
1. **`yuemdee_functional_requirements.md`**:
   * **FR-03 (แก้ไข):** ระบุการแสดงรายการครุภัณฑ์รายชิ้น (Serialized Units) พร้อมคะแนนดาวและรีวิวจากผู้ใช้งานก่อนหน้า
   * **FR-08 / FR-09 (แก้ไข):** ระบุการแนบรูปภาพหลักฐานสภาพสิ่งของ ณ ตอนรับของและตอนแจ้งคืน
   * **FR-16 (แก้ไข):** บันทึกรีวิวสภาพครุภัณฑ์ผูกกับรหัส Asset Tag รายชิ้น
   * **FR-26 (แก้ไข):** เพิ่มสิทธิ์ Staff/Admin ในการตั้งค่าอัตราค่าปรับกรณีส่งคืนล่าช้า (บาท/วัน)
   * **FR-37 (เพิ่มใหม่):** ระบบคำนวณค่าปรับยืมเกินกำหนดและบันทึกสถานะการชำระค่าปรับ
   * *หมายเหตุ:* ตัดข้อความ "ไม่รองรับระบบค่าปรับ" ออกจากเอกสาร Proposal
2. **`proposal/usecase/use_case_description.md`**:
   * อัปเดต Basic Flow / Alternative Flow ของ UC-03, UC-08, UC-09, UC-15, UC-19, UC-26 ให้ครอบคลุม 4 ฟังก์ชันข้างต้น
3. **`proposal/proposal.md` & `script.md`**:
   * ตัดข้อจำกัดเรื่อง "ไม่มีระบบค่าปรับ" ออกจากขอบเขตโครงงาน
   * เพิ่ม 4 จุดเด่นใหม่เข้าไปในสคริปต์การนำเสนอ 8 นาที
