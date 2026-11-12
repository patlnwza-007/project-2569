# Field Mapping (Mockup UI ↔ ERD `00_erd_reference.md`)

เอกสารสรุปแบบกระชับว่าฟิลด์บนหน้าจอ Mockup แต่ละหน้าดึง/บันทึกข้อมูลจากตารางและคอลัมน์ใดใน [00_erd_reference.md](./00_erd_reference.md)

---

## 1. หน้าผู้ใช้งานทั่วไปและเข้าสู่ระบบ

### `page-welcome.html`
* ไม่มีฟิลด์จากฐานข้อมูล

### `page-login.html` (เข้าสู่ระบบ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| อีเมลเข้าสู่ระบบ UBU SSO | `USER.email` |
| ตรวจสอบสถานะการระงับสิทธิ์ / เหตุผล | `USER.blocked`, `USER.block_reason` |
| ชื่อบัญชีแอดมิน (Username) | `ADMIN.username` |

### `page-profile.html` (โปรไฟล์ส่วนตัว)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| รหัสนักศึกษา (11 หลัก) | `STUDENT.student_id` |
| ชื่อ - นามสกุล | `USER.name` |
| อีเมลมหาวิทยาลัย | `USER.email` |
| เบอร์โทรศัพท์ติดต่อ (10 หลัก) | `STUDENT.phone` |
| เข้าสู่ระบบครั้งแรก | `USER.first_login` |
| เข้าสู่ระบบล่าสุด | `USER.last_login` |

---

## 2. หน้านักศึกษา: ค้นหา ยืม คืน คิว รีวิว แจ้งซ่อม

### `page-item-list.html` (รายการวัสดุและครุภัณฑ์)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ค้นหาชื่อสิ่งของ / รหัสครุภัณฑ์ | `ITEM.name`, `EQUIPMENT.asset_tag` |
| ตัวกรองประเภทสิ่งของ / ป้ายประเภท | `ITEM.item_type` |
| ตัวกรอง/ป้ายสถานะ | `ITEM.base_status` |
| รูปภาพ, ชื่อ, ตำแหน่งจัดเก็บ, หน่วยนับ, ราคาจัดซื้อ | `ITEM.image`, `ITEM.name`, `ITEM.location`, `ITEM.unit`, `ITEM.purchase_price` |
| รหัสครุภัณฑ์รายชิ้น | `EQUIPMENT.asset_tag` |
| จำนวนคงเหลือ / จำนวนทั้งหมด | `MATERIAL.qty_available`, `MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_total` |
| ระยะเวลายืมสูงสุด | `DURABLE_MATERIAL.max_borrow_days`, `EQUIPMENT.max_borrow_days` |
| คะแนนดาวเฉลี่ย / จำนวนรีวิว | `REVIEW.rating` (คำนวณ `AVG`, `COUNT` ตาม `REVIEW.item_id`) |
| จองคิว (ปุ่มบนการ์ดที่หมด) | `QUEUE.item_id`, `QUEUE.user_id`, `QUEUE.status`, `QUEUE.joined_at` |

### `page-item-detail.html` (รายละเอียดสิ่งของ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ข้อมูลหลักของสิ่งของ | `ITEM.id`, `ITEM.item_type`, `ITEM.name`, `ITEM.image`, `ITEM.location`, `ITEM.unit`, `ITEM.purchase_price`, `ITEM.base_status`, `ITEM.description` |
| จำนวนคงเหลือ/ทั้งหมด (วัสดุ) | `MATERIAL.qty_total`, `MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_available` |
| วันยืมสูงสุดและค่าปรับต่อวัน | `DURABLE_MATERIAL.max_borrow_days`, `DURABLE_MATERIAL.fine_rate_per_day`, `EQUIPMENT.max_borrow_days`, `EQUIPMENT.fine_rate_per_day` |
| รหัสครุภัณฑ์รายชิ้น | `EQUIPMENT.asset_tag` |
| ที่ตั้งปัจจุบันกรณีถูกยืมและแจ้งย้าย | `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at` |
| รายการรีวิวและผู้เขียนรีวิว | `REVIEW.rating`, `REVIEW.comment`, `REVIEW.created_at`, `USER.name` |
| กดจองคิว | `QUEUE.item_id`, `QUEUE.user_id`, `QUEUE.status`, `QUEUE.joined_at` |

### `page-cart.html` (ตะกร้าของฉัน)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| แสดงรายละเอียดสิ่งของในตะกร้า | `ITEM.id`, `ITEM.item_type`, `ITEM.name`, `ITEM.image`, `ITEM.unit`, `ITEM.base_status`, `MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_available`, `DURABLE_MATERIAL.max_borrow_days`, `EQUIPMENT.asset_tag`, `EQUIPMENT.max_borrow_days` |
| จองคิวแทน (เมื่อถูกยืมตัดหน้า) | `QUEUE.item_id`, `QUEUE.user_id`, `QUEUE.status`, `QUEUE.joined_at` |

### `page-request-form.html` (ยืนยันส่งคำขอยืม)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ตรวจเบอร์โทรและสถานะระงับสิทธิ์ก่อนส่ง | `STUDENT.phone`, `USER.blocked`, `USER.block_reason` |
| รายการสิ่งของ, จำนวน, รูปสภาพเดิม | `BORROW_ITEM.item_id`, `BORROW_ITEM.qty`, `BORROW_ITEM.initial_photo` |
| ตัวเลือกขอยืมระยะยาวพิเศษ | `BORROW_REQUEST.is_special` |
| บันทึกคำขอยืม | `BORROW_REQUEST.user_id`, `BORROW_REQUEST.status`, `BORROW_REQUEST.created_at`, `BORROW_REQUEST.use_date` |

### `page-request-list.html` (หน้าหลัก / สถานะคำขอยืมของฉัน)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ชื่อนักศึกษาผู้ยืม | `USER.name` |
| เลขที่คำขอ, สถานะ, ประเภทพิเศษ, วันที่ส่ง, เหตุผลปฏิเสธ | `BORROW_REQUEST.id`, `BORROW_REQUEST.status`, `BORROW_REQUEST.is_special`, `BORROW_REQUEST.created_at`, `BORROW_REQUEST.reject_reason` |
| รายการสิ่งของ, จำนวน, กำหนดคืน | `BORROW_ITEM.item_id`, `BORROW_ITEM.qty`, `BORROW_ITEM.due_date`, `ITEM.name`, `ITEM.unit`, `ITEM.item_type`, `EQUIPMENT.asset_tag` |
| แจ้งย้ายที่ตั้งครุภัณฑ์ชั่วคราว | `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at` |
| สถานะค่าปรับและค่าชดใช้สูญหาย | `RETURN_REQUEST.fine_paid`, `RETURN_ITEM.condition_status`, `RETURN_ITEM.lost_compensation`, `RETURN_ITEM.lost_paid`, `DURABLE_MATERIAL.fine_rate_per_day`, `EQUIPMENT.fine_rate_per_day` |
| ลำดับคิวที่รออยู่ (ในแถบสรุป) | `QUEUE.id`, `QUEUE.item_id`, `QUEUE.user_id`, `QUEUE.status` |

### `page-notify-return.html` (แจ้งส่งคืนสิ่งของ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| คำขอที่กำลังยืมและกำหนดคืน | `BORROW_REQUEST.id`, `BORROW_REQUEST.status`, `BORROW_REQUEST.created_at`, `BORROW_ITEM.due_date` |
| รายการสิ่งของ, จำนวน, รูปก่อนยืม, ราคาจัดซื้อเดิม | `BORROW_ITEM.id`, `BORROW_ITEM.qty`, `BORROW_ITEM.initial_photo`, `ITEM.name`, `ITEM.image`, `ITEM.unit`, `ITEM.purchase_price`, `EQUIPMENT.asset_tag` |
| บันทึกใบแจ้งส่งคืนและรูปหลักฐานคืน | `RETURN_REQUEST.borrow_request_id`, `RETURN_REQUEST.status`, `RETURN_REQUEST.return_photo`, `RETURN_REQUEST.note`, `RETURN_REQUEST.created_at` |
| บันทึกรายการที่เลือกคืนและสภาพที่แจ้ง | `RETURN_ITEM.return_request_id`, `RETURN_ITEM.borrow_item_id`, `RETURN_ITEM.qty_returned`, `RETURN_ITEM.condition_status` |

### `page-queue-list.html` (คิวของฉัน)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ข้อมูลคิวและเวลาที่จอง | `QUEUE.id`, `QUEUE.item_id`, `QUEUE.user_id`, `QUEUE.status`, `QUEUE.joined_at` |
| ข้อมูลสิ่งของและประมาณการวันพร้อมยืม | `ITEM.name`, `ITEM.image`, `ITEM.item_type`, `EQUIPMENT.asset_tag`, `DURABLE_MATERIAL.max_borrow_days`, `EQUIPMENT.max_borrow_days`, `BORROW_ITEM.due_date`, `BORROW_REQUEST.is_special` |

### `page-history.html` (ประวัติการยืมของฉัน)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ประวัติคำขอและสถานะ | `BORROW_REQUEST.id`, `BORROW_REQUEST.user_id`, `BORROW_REQUEST.status`, `BORROW_REQUEST.created_at` |
| รายการสิ่งของที่ยืมและจำนวน | `BORROW_ITEM.item_id`, `BORROW_ITEM.qty`, `ITEM.name`, `ITEM.unit`, `EQUIPMENT.asset_tag` |
| สถานะการรีวิวรายชิ้น | `REVIEW.id`, `REVIEW.borrow_item_id` |

### `page-evaluation.html` (ประเมินความพึงพอใจและเขียนรีวิว)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ข้อมูลคำขอและวันที่คืน | `BORROW_REQUEST.id`, `BORROW_REQUEST.status`, `RETURN_REQUEST.returned_at` |
| รายการสิ่งของรายชิ้นที่ให้รีวิว | `BORROW_ITEM.id`, `BORROW_ITEM.item_id`, `BORROW_ITEM.qty`, `ITEM.name`, `ITEM.image`, `ITEM.unit`, `EQUIPMENT.asset_tag` |
| คะแนนดาว, ข้อความรีวิว, วันที่บันทึก | `REVIEW.borrow_item_id`, `REVIEW.user_id`, `REVIEW.item_id`, `REVIEW.rating`, `REVIEW.comment`, `REVIEW.created_at` |

### `page-report-damage.html` (แจ้งอุปกรณ์ชำรุด)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ค้นหาสิ่งของ / อ้างอิงตำแหน่งล่าสุด | `ITEM.id`, `ITEM.name`, `ITEM.location`, `ITEM.base_status`, `EQUIPMENT.asset_tag`, `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at` |
| บันทึกใบแจ้งซ่อมและแสดงประวัติ | `DAMAGE_REPORT.user_id`, `DAMAGE_REPORT.item_id`, `DAMAGE_REPORT.item_name`, `DAMAGE_REPORT.location`, `DAMAGE_REPORT.symptom`, `DAMAGE_REPORT.photo`, `DAMAGE_REPORT.status`, `DAMAGE_REPORT.created_at` |

### `page-suggestion.html` (เสนอแนะสิ่งของใหม่)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ชื่อสิ่งของ, เหตุผล/รายละเอียด, สถานะ, วันที่ | `SUGGESTION.user_id`, `SUGGESTION.name`, `SUGGESTION.detail`, `SUGGESTION.status`, `SUGGESTION.created_at` |

---

## 3. หน้าเจ้าหน้าที่ (Staff)

### `page-staff-dashboard.html` (แดชบอร์ดเจ้าหน้าที่)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ตัวเลขสรุปคำขอ / เกินกำหนด | `BORROW_REQUEST.status`, `BORROW_ITEM.due_date` |
| ตัวเลขสรุปคลังพัสดุ | `ITEM.item_type`, `ITEM.base_status` |
| ตัวเลขนักศึกษาถูกระงับสิทธิ์ | `USER.blocked` |

### `page-pending-requests.html` (คำขอรออนุมัติ / ปล่อยของหน้าเคาน์เตอร์)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ข้อมูลคำขอและผู้ยืม | `BORROW_REQUEST.id`, `BORROW_REQUEST.status`, `BORROW_REQUEST.is_special`, `BORROW_REQUEST.use_date`, `BORROW_REQUEST.created_at`, `BORROW_REQUEST.pickup_photo`, `USER.name`, `STUDENT.phone` |
| รายการสิ่งของ, จำนวน, รูปสภาพเดิม, คงเหลือ | `BORROW_ITEM.item_id`, `BORROW_ITEM.qty`, `BORROW_ITEM.initial_photo`, `ITEM.name`, `ITEM.item_type`, `ITEM.unit`, `EQUIPMENT.asset_tag`, `MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_available` |
| อนุมัติปล่อยของ / ปฏิเสธ | `BORROW_REQUEST.status`, `BORROW_REQUEST.approved_by`, `BORROW_REQUEST.approved_at`, `BORROW_REQUEST.reject_reason`, `BORROW_ITEM.due_date`, `ITEM.base_status`, `MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_available` |

### `page-return-list.html` (ตรวจรับคืนสิ่งของหน้าเคาน์เตอร์)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ข้อมูลคำขอ, ผู้ยืม, รูปวันรับของ | `BORROW_REQUEST.id`, `BORROW_REQUEST.status`, `BORROW_REQUEST.created_at`, `BORROW_REQUEST.pickup_photo`, `USER.name` |
| รายการสิ่งของ, กำหนดคืน, ตำแหน่งที่แจ้งย้าย | `BORROW_ITEM.due_date`, `BORROW_ITEM.initial_photo`, `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at`, `ITEM.name`, `ITEM.image`, `ITEM.unit`, `ITEM.purchase_price`, `EQUIPMENT.asset_tag` |
| ใบแจ้งคืน, รูปคืน, ค่าปรับ, ผู้ตรวจรับ | `RETURN_REQUEST.id`, `RETURN_REQUEST.borrow_request_id`, `RETURN_REQUEST.inspected_by`, `RETURN_REQUEST.status`, `RETURN_REQUEST.return_photo`, `RETURN_REQUEST.custom_fine`, `RETURN_REQUEST.fine_paid`, `RETURN_REQUEST.note`, `RETURN_REQUEST.created_at`, `RETURN_REQUEST.returned_at` |
| ผลตรวจสภาพ, ค่าปรับรายชิ้น, ค่าชดใช้สูญหาย | `RETURN_ITEM.qty_returned`, `RETURN_ITEM.condition_status`, `RETURN_ITEM.fine`, `RETURN_ITEM.lost_compensation`, `RETURN_ITEM.lost_paid` |
| คืนสต็อก/เปลี่ยนสถานะเมื่อตรวจรับ | `ITEM.base_status`, `MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_total` |

### `page-damaged-equipment.html` (จัดการครุภัณฑ์เสียหายและแจ้งซ่อม)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| แท็บครุภัณฑ์เสียหาย / ส่งซ่อม / ปลดระวาง | `ITEM.id`, `ITEM.name`, `ITEM.location`, `ITEM.base_status`, `EQUIPMENT.asset_tag` |
| แท็บรายการแจ้งซ่อมจากนักศึกษา | `DAMAGE_REPORT.id`, `DAMAGE_REPORT.user_id`, `DAMAGE_REPORT.item_id`, `DAMAGE_REPORT.item_name`, `DAMAGE_REPORT.location`, `DAMAGE_REPORT.symptom`, `DAMAGE_REPORT.photo`, `DAMAGE_REPORT.status`, `DAMAGE_REPORT.created_at`, `USER.name` |

### `page-all-history.html` (ประวัติการยืม-คืนทั้งระบบ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ตารางและ Modal รายละเอียดคำขอ | `BORROW_REQUEST.id`, `BORROW_REQUEST.status`, `BORROW_REQUEST.is_special`, `BORROW_REQUEST.created_at`, `BORROW_REQUEST.approved_at`, `BORROW_REQUEST.pickup_photo` |
| ข้อมูลผู้ยืม | `USER.name`, `USER.email`, `STUDENT.student_id`, `STUDENT.phone` |
| รายการสิ่งของ, กำหนดคืน, ตำแหน่งย้าย, สภาพคืน | `BORROW_ITEM.qty`, `BORROW_ITEM.due_date`, `BORROW_ITEM.initial_photo`, `BORROW_ITEM.current_location`, `BORROW_ITEM.moved_at`, `ITEM.name`, `ITEM.image`, `ITEM.unit`, `ITEM.item_type`, `ITEM.location`, `EQUIPMENT.asset_tag`, `RETURN_ITEM.condition_status`, `RETURN_ITEM.lost_compensation` |

### `page-item-overview.html` (จัดการคลังสิ่งของ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ตารางพัสดุและรหัสครุภัณฑ์ | `ITEM.id`, `ITEM.item_type`, `ITEM.name`, `ITEM.image`, `ITEM.location`, `ITEM.unit`, `ITEM.base_status`, `MATERIAL.qty_total`, `MATERIAL.qty_available`, `DURABLE_MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_available`, `EQUIPMENT.asset_tag` |
| อัปเดตสถานะแบบกลุ่ม (Bulk Status) | `ITEM.base_status` |

### `page-item-form.html` (เพิ่ม/แก้ไขข้อมูลสิ่งของ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ข้อมูลพื้นฐานสิ่งของ | `ITEM.name`, `ITEM.image`, `ITEM.location`, `ITEM.unit`, `ITEM.purchase_price`, `ITEM.description` |
| จำนวนทั้งหมด | `MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_total` |
| วันยืมสูงสุดและอัตราค่าปรับต่อวัน | `DURABLE_MATERIAL.max_borrow_days`, `DURABLE_MATERIAL.fine_rate_per_day`, `EQUIPMENT.max_borrow_days`, `EQUIPMENT.fine_rate_per_day` |
| รหัสครุภัณฑ์รายชิ้น | `EQUIPMENT.asset_tag` |

### `page-item-status-change.html` (เปลี่ยนสถานะครุภัณฑ์รายชิ้น)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| แสดงและบันทึกสถานะครุภัณฑ์ | `ITEM.name`, `ITEM.image`, `ITEM.item_type`, `ITEM.base_status`, `EQUIPMENT.asset_tag` |

### `page-item-delete.html` (ลบวัสดุสิ้นเปลือง)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| เลือกลบรายการวัสดุสิ้นเปลือง | `ITEM.id`, `ITEM.name`, `ITEM.item_type`, `MATERIAL.qty_total`, `MATERIAL.qty_available` |

### `page-bulk-import.html` (นำเข้าคลังแบบชุด CSV)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| นำเข้าข้อมูลสิ่งของจาก CSV | `ITEM.name`, `ITEM.item_type`, `MATERIAL.qty_total`, `DURABLE_MATERIAL.qty_total`, `DURABLE_MATERIAL.max_borrow_days`, `EQUIPMENT.max_borrow_days` |

### `page-student-list.html` (รายชื่อนักศึกษา Read-Only)ป
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ตารางรายชื่อนักศึกษาและสถานะสิทธิ์ | `STUDENT.student_id`, `USER.name`, `USER.email`, `STUDENT.phone`, `USER.blocked`, `USER.block_reason` |

### `page-suggestion-review.html` (พิจารณาคำเสนอแนะ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| รายการข้อเสนอแนะ | `SUGGESTION.id`, `SUGGESTION.user_id`, `SUGGESTION.name`, `SUGGESTION.detail`, `SUGGESTION.status`, `SUGGESTION.created_at`, `USER.name` |
| โอนเข้าแผนจัดซื้อ | `PURCHASE_PLAN.suggestion_id`, `PURCHASE_PLAN.name`, `PURCHASE_PLAN.detail`, `PURCHASE_PLAN.created_by`, `PURCHASE_PLAN.created_at` |

### `page-purchase-add.html` (จัดการแผนจัดซื้อ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| เพิ่มและแสดงรายการแผนจัดซื้อ | `PURCHASE_PLAN.id`, `PURCHASE_PLAN.suggestion_id`, `PURCHASE_PLAN.name`, `PURCHASE_PLAN.detail`, `PURCHASE_PLAN.created_by`, `PURCHASE_PLAN.created_at` |

### `page-report-export.html` (ส่งออกรายงาน)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| รายงานการยืม, ค้างส่ง, เสียหาย, ข้อเสนอแนะ | `BORROW_REQUEST.id`, `BORROW_REQUEST.status`, `BORROW_REQUEST.created_at`, `BORROW_ITEM.due_date`, `USER.name`, `STUDENT.student_id`, `ITEM.name`, `ITEM.base_status`, `EQUIPMENT.asset_tag`, `SUGGESTION.name`, `SUGGESTION.detail`, `SUGGESTION.status` |

---

## 4. หน้าผู้ดูแลระบบ (Admin)

### `page-user-list.html` (จัดการบัญชีผู้ใช้งานทั้งหมด)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ตารางบัญชีผู้ใช้งานและตัวกรองบทบาท | `USER.name`, `USER.email`, `USER.blocked`, `STUDENT.student_id`, `STAFF.is_override`, `ADMIN.username` |

### `page-user-detail.html` (รายละเอียดบัญชีผู้ใช้งาน)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ข้อมูลผู้ใช้ บทบาท และสิทธิ์ | `USER.name`, `USER.email`, `USER.blocked`, `USER.block_reason`, `STAFF.is_override`, `BORROW_REQUEST.status` |

### `page-student-permission.html` (จัดการสิทธิ์การยืมนักศึกษา)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| ข้อมูลนักศึกษาและสั่งระงับ/ปลดบล็อก | `STUDENT.student_id`, `USER.name`, `USER.email`, `USER.blocked`, `USER.block_reason` |

### `page-role-override.html` (กำหนดบทบาทพิเศษ)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| อีเมลเป้าหมายและบทบาทที่กำหนด | `USER.email`, `STAFF.user_id`, `STAFF.is_override` |

### `page-personnel-export.html` (ส่งออกรายชื่อบุคลากร CSV)
| ฟิลด์บนหน้าจอ | ตาราง.คอลัมน์ (ERD) |
|---|---|
| รายชื่อบุคลากรและบทบาทปัจจุบัน | `USER.name`, `USER.email`, `STAFF.is_override` |

---

## ⚠️ รายการฟิลด์ที่ไม่ถูกใช้ / ไม่มีคู่ใน ERD (ข้ามการ Mapping โดยไม่เดา)

### ก. คอลัมน์ที่มีใน `00_erd_reference.md` แต่ **ไม่พบการใช้งานในหน้าจอ Mockup**
1. `USER.created_at` — ไม่มีหน้าจอใดแสดงหรือกรอกวันเวลาสร้างบัญชีผู้ใช้
2. `USER.blocked_by` — ในหน้า `page-student-permission.html` และ `page-user-detail.html` ไม่มีการบันทึกหรือแสดงว่าใครเป็นคนระงับสิทธิ์
3. `STAFF.override_reason` — ในหน้า `page-role-override.html` ไม่มีช่องกรอกเหตุผลการกำหนดบทบาท
4. `STAFF.assigned_by` — ในหน้า `page-role-override.html` และ `page-user-detail.html` ไม่มีการบันทึกหรือแสดงผู้แต่งตั้งสิทธิ์
5. `STAFF.assigned_at` — ไม่มีหน้าจอใดบันทึกหรือแสดงวันเวลาที่แต่งตั้ง Role Override
6. `RETURN_REQUEST.fine_reason` — ในหน้า `page-return-list.html` ปุ่มแก้ไขค่าปรับกรอกเฉพาะตัวเลขยอดเงิน ไม่มีช่องกรอกเหตุผล
7. `QUEUE.notified_at` — ยังไม่มีหน้าจอหรือกลไกแจ้งเตือนและกดยืนยันรับสิทธิ์คิวใน Mockup
8. `QUEUE.expired_at` — ยังไม่มีหน้าจอหรือตัวจับเวลาหมดอายุคิวใน Mockup

### ข. ฟิลด์ที่มีใน Mockup แต่ **ไม่มีคอลัมน์รองรับใน `00_erd_reference.md`**
1. `category` / `category_id` ใน `page-item-list.html`, `page-item-detail.html`, `page-bulk-import.html` — ใน `00_erd_reference.md` ตาราง `ITEM` ไม่มีคอลัมน์หมวดหมู่แล้ว
2. `custom_due_date` และ `reason` ใน `page-pending-requests.html` (และ `p_request_form_custom_due` ใน `page-request-form.html`) — ใน `00_erd_reference.md` ตาราง `BORROW_REQUEST` ไม่มี `reason` หรือ `custom_due_date` (`due_date` ถูกย้ายไปอยู่ที่ `BORROW_ITEM` ตอนปล่อยของ)
3. `note` ของครุภัณฑ์รายชิ้น (`u.note` ใน `page-item-status-change.html`, `page-item-overview.html`, `page-damaged-equipment.html`, `page-report-export.html`) — ใน `00_erd_reference.md` ตาราง `ITEM` / `EQUIPMENT` ไม่มีคอลัมน์ `note` (มีเพียง `ITEM.description`)
4. `damaged_note` / `lost_note` รายชิ้นตอนตรวจรับคืน (`page-return-list.html`) — ใน `00_erd_reference.md` ตาราง `RETURN_ITEM` ไม่มีคอลัมน์ `note` รายชิ้น (มีเพียง `RETURN_REQUEST.note` ระดับใบแจ้งคืน)
5. รหัสผ่านแอดมิน (`p_login_admin_pass` ใน `page-login.html`) — ไม่มีคอลัมน์ในตาราง `ADMIN`
6. ตะกร้าสินค้า (`cart`) ใน `page-cart.html`, `page-item-list.html` — ไม่มีตาราง `CART_ITEM` ใน `00_erd_reference.md` (จัดการในระดับ Session/Client)
