/* ============================================================================
 * YuemDee · shared.js
 * Mock data + localStorage helpers + session/role helpers ใช้ร่วมกันทุกหน้า
 * ระบบจริง: Django ORM + session (UBU Single Sign-On @ubu.ac.th)
 *
 * ใช้ร่วมกันโดย: index.html (shell) และทุกไฟล์ใน pages/*.html
 * โหลดผ่าน: <script src="shared.js"></script> (จาก index.html) หรือ
 *          <script src="../shared.js"></script> (จากภายใน pages/)
 * ==========================================================================*/

const LS_PREFIX = "yuemdee_";

/* ---------------------------- Seed Mock Data ---------------------------- */

const SEED_CATEGORIES = [
  { id: 1, name: "โสตทัศนูปกรณ์" },
  { id: 2, name: "เครื่องมือช่าง" },
  { id: 3, name: "เครื่องเขียน/วัสดุสิ้นเปลือง" },
  { id: 4, name: "อุปกรณ์ไฟฟ้า" },
  { id: 5, name: "เสียง/ไมโครโฟน" },
];

const SEED_ROOMS = [
  {
    id: 1,
    code: "EN6-101",
    name: "ห้องคลังพัสดุกลาง (Central Storage & Counter)",
    building: "อาคารวิศวกรรมศาสตร์ 6 (EN6)",
    floor: "ชั้น 1",
    location_detail: "ทางเข้าทิศเหนือ ติดโถงลิฟต์กลาง ตรงข้ามห้องธุรการ",
    type: "storage",
    image: "🏢",
    counter_name: "เคาน์เตอร์เจ้าหน้าที่ตรวจรับของ",
    door_name: "ประตูทางเข้าหลัก (ทิศเหนือ)",
    cabinets: ["ตู้ A1", "ตู้ A2", "ตู้ B1"]
  },
  {
    id: 2,
    code: "EN6-205",
    name: "ห้องปฏิบัติการระบบไฟฟ้าและอิเล็กทรอนิกส์ (EE Lab)",
    building: "อาคารวิศวกรรมศาสตร์ 6 (EN6)",
    floor: "ชั้น 2",
    location_detail: "ปีกตะวันออก ติดบันไดหนีไฟ ตรงข้ามห้องพักอาจารย์",
    type: "lab",
    image: "🔬",
    counter_name: "โต๊ะผู้ดูแลห้องปฏิบัติการ",
    door_name: "ประตูทางเข้าห้องแล็บ",
    cabinets: ["ตู้ E1", "ตู้ E2"]
  },
  {
    id: 3,
    code: "EN6-302",
    name: "ห้องสตูดิโอและโสตทัศนูปกรณ์ (Media Studio)",
    building: "อาคารวิศวกรรมศาสตร์ 6 (EN6)",
    floor: "ชั้น 3",
    location_detail: "ปีกตะวันตก โซนห้องเก็บเสียง",
    type: "studio",
    image: "🎥",
    counter_name: "โต๊ะควบคุมมิกเซอร์และระบบเสียง",
    door_name: "ประตูกันเสียงห้องสตู",
    cabinets: ["ตู้ M1", "ตู้ M2"]
  }
];

const SEED_POSITIONS = [
  // ห้อง EN6-101: คลังกลาง
  { id: 1, room_id: 1, cabinet: "ตู้ A1", shelf: 2, shelf_name: "ชั้นที่ 2 (ชั้นกลาง)", name: "ห้อง EN6-101 · ตู้ A1 ชั้น 2" },
  { id: 2, room_id: 1, cabinet: "ตู้ A2", shelf: 2, shelf_name: "ชั้นที่ 2 (ชั้นกลาง)", name: "ห้อง EN6-101 · ตู้ A2 ชั้น 2" },
  { id: 3, room_id: 1, cabinet: "ตู้ A1", shelf: 1, shelf_name: "ชั้นที่ 1 (ล่างสุด)", name: "ห้อง EN6-101 · ตู้ A1 ชั้น 1" },
  { id: 4, room_id: 1, cabinet: "ตู้ B1", shelf: 2, shelf_name: "ชั้นที่ 2 (ชั้นกลาง)", name: "ห้อง EN6-101 · ตู้ B1 ชั้น 2" },
  { id: 8, room_id: 1, cabinet: "ตู้ B1", shelf: 1, shelf_name: "ชั้นที่ 1 (ล่างสุด)", name: "ห้อง EN6-101 · ตู้ B1 ชั้น 1" },
  { id: 9, room_id: 1, cabinet: "ตู้ A2", shelf: 1, shelf_name: "ชั้นที่ 1 (ล่างสุด)", name: "ห้อง EN6-101 · ตู้ A2 ชั้น 1" },

  // ห้อง EN6-205: แล็บไฟฟ้า
  { id: 5, room_id: 2, cabinet: "ตู้ E1", shelf: 2, shelf_name: "ชั้นที่ 2 (ชั้นกลาง)", name: "ห้อง EN6-205 · ตู้ E1 ชั้น 2" },
  { id: 10, room_id: 2, cabinet: "ตู้ E1", shelf: 1, shelf_name: "ชั้นที่ 1 (ล่างสุด)", name: "ห้อง EN6-205 · ตู้ E1 ชั้น 1" },
  { id: 11, room_id: 2, cabinet: "ตู้ E2", shelf: 2, shelf_name: "ชั้นที่ 2 (ชั้นกลาง)", name: "ห้อง EN6-205 · ตู้ E2 ชั้น 2" },

  // ห้อง EN6-302: สตูดิโอมีเดีย
  { id: 6, room_id: 3, cabinet: "ตู้ M1", shelf: 3, shelf_name: "ชั้นที่ 3 (บนสุด)", name: "ห้อง EN6-302 · ตู้ M1 ชั้น 3" },
  { id: 7, room_id: 3, cabinet: "ตู้ M1", shelf: 2, shelf_name: "ชั้นที่ 2 (ชั้นกลาง)", name: "ห้อง EN6-302 · ตู้ M1 ชั้น 2" },
  { id: 12, room_id: 3, cabinet: "ตู้ M2", shelf: 1, shelf_name: "ชั้นที่ 1 (ล่างสุด)", name: "ห้อง EN6-302 · ตู้ M2 ชั้น 1" },
];

const SEED_ITEM_STATUSES = ["พร้อมให้ยืม", "ชำรุด", "เลิกใช้งาน", "ปลดระวาง"]; // สถานะพื้นฐานของสิ่งของ (ตั้งค่าได้ที่ WarehouseSettings)

// type: "material" (วัสดุสิ้นเปลือง เบิกใช้แล้วหมดไป ไม่ต้องคืน) | "durable_material" (วัสดุคงทน ยืม-คืน นับจำนวนรวม) | "equipment" (ครุภัณฑ์ ยืม-คืน มีรหัสประจำชิ้น)
const SEED_ITEMS = [
  { id: 1, name: "โปรเจกเตอร์ Epson EB-X400", type: "equipment", category_id: 1, category: "โสตทัศนูปกรณ์", position_id: 1, location: "ห้อง EN6-101 · ตู้ A1 ชั้น 2", qty_total: 3, qty_available: 2, max_borrow_days: 7, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "📽️", price: 18500, unit: "เครื่อง" },
  { id: 2, name: "กล้อง DSLR Canon EOS 200D", type: "equipment", category_id: 1, category: "โสตทัศนูปกรณ์", position_id: 6, location: "ห้อง EN6-302 · ตู้ M1 ชั้น 3", qty_total: 2, qty_available: 1, max_borrow_days: 5, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "📷", price: 23900, unit: "เครื่อง" },
  { id: 3, name: "ขาตั้งกล้อง Tripod", type: "equipment", category_id: 1, category: "โสตทัศนูปกรณ์", position_id: 2, location: "ห้อง EN6-101 · ตู้ A2 ชั้น 2", qty_total: 5, qty_available: 4, max_borrow_days: 5, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "🎥", price: 2500, unit: "ตัว" },
  { id: 4, name: "สาย HDMI 5 เมตร", type: "durable_material", category_id: 4, category: "อุปกรณ์ไฟฟ้า", position_id: 3, location: "ห้อง EN6-101 · ตู้ A1 ชั้น 1", qty_total: 20, qty_available: 12, max_borrow_days: 7, fine_rate_per_day: 10, base_status: "พร้อมให้ยืม", image: "🔌", price: 350, unit: "เส้น" },
  { id: 5, name: "มัลติมิเตอร์", type: "equipment", category_id: 2, category: "เครื่องมือช่าง", position_id: 5, location: "ห้อง EN6-205 · ตู้ E1 ชั้น 2", qty_total: 4, qty_available: 3, max_borrow_days: 3, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "🔧", price: 1200, unit: "เครื่อง" },
  { id: 6, name: "หัวแร้งบัดกรี", type: "equipment", category_id: 2, category: "เครื่องมือช่าง", position_id: 5, location: "ห้อง EN6-205 · ตู้ E1 ชั้น 2", qty_total: 6, qty_available: 6, max_borrow_days: 3, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "🛠️", price: 450, unit: "ชุด" },
  { id: 7, name: "กระดาษ A4 80 แกรม", type: "material", category_id: 3, category: "เครื่องเขียน/วัสดุสิ้นเปลือง", position_id: 4, location: "ห้อง EN6-101 · ตู้ B1 ชั้น 2", qty_total: 100, qty_available: 45, max_borrow_days: null, fine_rate_per_day: null, base_status: "พร้อมให้ยืม", image: "📄", price: 135, unit: "รีม" },
  { id: 8, name: "ปากกาเคมี", type: "material", category_id: 3, category: "เครื่องเขียน/วัสดุสิ้นเปลือง", position_id: 4, location: "ห้อง EN6-101 · ตู้ B1 ชั้น 2", qty_total: 50, qty_available: 10, max_borrow_days: null, fine_rate_per_day: null, base_status: "พร้อมให้ยืม", image: "🖊️", price: 30, unit: "ด้าม" },
  { id: 9, name: "ไมโครโฟนไร้สาย", type: "equipment", category_id: 5, category: "เสียง/ไมโครโฟน", position_id: 7, location: "ห้อง EN6-302 · ตู้ M1 ชั้น 2", qty_total: 3, qty_available: 0, max_borrow_days: 3, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "🎤", price: 6500, unit: "ชุด" },
  { id: 10, name: "ลำโพงพกพา Bluetooth", type: "equipment", category_id: 5, category: "เสียง/ไมโครโฟน", position_id: 7, location: "ห้อง EN6-302 · ตู้ M1 ชั้น 2", qty_total: 4, qty_available: 2, max_borrow_days: 5, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "🔊", price: 3200, unit: "ตัว" },
  { id: 11, name: "ชุดเครื่องมือช่าง", type: "equipment", category_id: 2, category: "เครื่องมือช่าง", position_id: 5, location: "ห้อง EN6-205 · ตู้ E1 ชั้น 2", qty_total: 3, qty_available: 1, max_borrow_days: 5, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "🧰", price: 4500, unit: "ชุด" },
  { id: 12, name: "แบตเตอรี่ AA", type: "material", category_id: 4, category: "อุปกรณ์ไฟฟ้า", position_id: 4, location: "ห้อง EN6-101 · ตู้ B1 ชั้น 2", qty_total: 60, qty_available: 60, max_borrow_days: null, fine_rate_per_day: null, base_status: "พร้อมให้ยืม", image: "🔋", price: 120, unit: "แพ็ค" },
  { id: 13, name: "เครื่องฉายทึบแสง (Overhead)", type: "equipment", category_id: 1, category: "โสตทัศนูปกรณ์", position_id: 2, location: "ห้อง EN6-101 · ตู้ A2 ชั้น 2", qty_total: 1, qty_available: 0, max_borrow_days: 7, fine_rate_per_day: 20, base_status: "ไม่พร้อมใช้งาน", image: "📽️", price: 15000, unit: "เครื่อง" },
  { id: 14, name: "ปลั๊กพ่วงสายไฟ 10 เมตร", type: "durable_material", category_id: 4, category: "อุปกรณ์ไฟฟ้า", position_id: 3, location: "ห้อง EN6-101 · ตู้ A1 ชั้น 1", qty_total: 15, qty_available: 10, max_borrow_days: 7, fine_rate_per_day: 10, base_status: "พร้อมให้ยืม", image: "🔌", price: 490, unit: "ชุด" },
  { id: 15, name: "สายแปลงสัญญาณ Type-C to HDMI/VGA", type: "durable_material", category_id: 4, category: "อุปกรณ์ไฟฟ้า", position_id: 3, location: "ห้อง EN6-101 · ตู้ A1 ชั้น 1", qty_total: 10, qty_available: 8, max_borrow_days: 5, fine_rate_per_day: 10, base_status: "พร้อมให้ยืม", image: "💻", price: 590, unit: "อัน" },
  { id: 16, name: "จอคอมพิวเตอร์ Dell 24 นิ้ว (Full HD)", type: "equipment", category_id: 1, category: "โสตทัศนูปกรณ์", position_id: 1, location: "ห้อง EN6-101 · ตู้ A1 ชั้น 2", qty_total: 3, qty_available: 1, max_borrow_days: 14, fine_rate_per_day: 20, base_status: "พร้อมให้ยืม", image: "🖥️", price: 6900, unit: "เครื่อง" },
];

const SEED_STUDENTS = [
  { id: "S001", name: "สมชาย ใจดี", email: "s001@ubu.ac.th", phone: "0812345678", first_login: "2026-06-01 09:12", last_login: "2026-07-22 14:03", blocked: false, block_reason: "" },
  { id: "S002", name: "สมหญิง มีดี", email: "s002@ubu.ac.th", phone: "0898765432", first_login: "2026-06-03 10:00", last_login: "2026-07-20 08:40", blocked: true, block_reason: "ค้างคืนครุภัณฑ์เกินกำหนดหลายครั้ง" },
  { id: "S003", name: "วิชัย ตั้งใจ", email: "s003@ubu.ac.th", phone: "", first_login: "2026-07-01 11:20", last_login: "2026-07-21 16:10", blocked: false, block_reason: "" },
];

const SEED_STAFFS = [
  { id: "T001", name: "อ.สมหญิง ดูแลดี", email: "staff1@ubu.ac.th" },
];

const SEED_ADMINS = [
  { id: "A001", name: "ผู้ดูแลระบบ (Django Superuser)", username: "admin", email: "admin@localhost" },
];

const SEED_WHITELIST_STUDENT = ["s001@ubu.ac.th", "s002@ubu.ac.th", "s003@ubu.ac.th"];
const SEED_WHITELIST_STAFF = ["staff1@ubu.ac.th"];

const SEED_ADMIN_BLOCKED_EMAILS = []; // บัญชีที่ถูกแอดมินระงับสิทธิ์การเข้าสู่ระบบทั้งหมด (ต่างจาก student.blocked ที่จำกัดเฉพาะการยืม)

const SEED_ROLE_OVERRIDES = [
  { email: "s004@ubu.ac.th", role: "staff", active: true },
];

// สถานะคำขอ: PENDING (รอตรวจของหน้าเคาน์เตอร์), BORROWING (กำลังยืม), REJECTED,
// RETURNED (คืนสำเร็จ), ISSUED, CANCELLED
const SEED_REQUESTS = [
  {
    id: 105,
    student_id: "S001",
    items: [
      { item_id: 16, qty: 1, asset_tag: "UBU-EQ-016-01", current_location: "ตึก EN6 ชั้น 2 ห้องพักสาขา EN6-204 (โต๊ะโครงงาน 1)", moved_at: "2026-07-22 10:15" },
      { item_id: 16, qty: 1, asset_tag: "UBU-EQ-016-02", current_location: "หอพักนักศึกษาใน ม.อุบลฯ (ย้ายชั่วคราวหนีน้ำท่วม)", moved_at: "2026-07-23 08:20" },
      { item_id: 14, qty: 2, current_location: "ตึก EN6 ชั้น 2 ห้องพักสาขา EN6-204", moved_at: "2026-07-22 10:15" }
    ],
    use_date: "2026-07-22",
    status: "BORROWING",
    created_at: "2026-07-22 09:00",
    approved_at: "2026-07-22 09:30",
    due_date: "2026-08-05",
    reject_reason: ""
  },
  { id: 101, student_id: "S001", items: [{ item_id: 1, qty: 1, initial_photo: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300" }, { item_id: 4, qty: 2 }, { item_id: 3, qty: 1 }], use_date: "2026-07-30", status: "PENDING", created_at: "2026-07-23 08:30", approved_at: null, reject_reason: "", pickup_photo: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300" },
  { id: 103, student_id: "S002", items: [{ item_id: 2, qty: 1, asset_tag: "UBU-EQ-002-01", current_location: "ห้องสโมสรนักศึกษา ชั้น 1 ตึก EN6", moved_at: "2026-07-15 10:00" }], use_date: "2026-07-15", status: "BORROWING", created_at: "2026-07-12 09:00", approved_at: "2026-07-13 09:00", due_date: "2026-08-02", reject_reason: "" },
  {
    id: 104,
    student_id: "S001",
    items: [
      { item_id: 5, qty: 1, asset_tag: "UBU-EQ-005-01", initial_photo: "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=300", current_location: "ตึก EN6 ชั้น 2 ห้องพักสาขา EN6-204", moved_at: "2026-07-16 09:30", returned: false },
      { item_id: 6, qty: 1, asset_tag: "UBU-EQ-006-01", initial_photo: "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=300", current_location: "ตึก EN6 ชั้น 2 ห้องพักสาขา EN6-204", moved_at: "2026-07-16 09:30", returned: true, returned_qty: 1 },
      { item_id: 10, qty: 1, asset_tag: "UBU-EQ-010-01", initial_photo: "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=300", current_location: "หอพักสุขใจ ซ.2 ต.เมืองศรีไค (ย้ายหนีน้ำท่วม)", moved_at: "2026-07-22 18:45", returned: false }
    ],
    use_date: "2026-07-16",
    status: "BORROWING",
    created_at: "2026-07-15 09:00",
    approved_at: "2026-07-15 13:00",
    due_date: "2026-07-20",
    reject_reason: ""
  },
  { id: 107, student_id: "S001", items: [{ item_id: 3, qty: 1 }], use_date: "2026-06-10", status: "RETURNED", created_at: "2026-06-05 09:00", approved_at: "2026-06-05 13:00", due_date: "2026-06-13", returned_at: "2026-06-12 15:00", reject_reason: "" },
  { id: 108, student_id: "S001", items: [{ item_id: 7, qty: 5 }], use_date: null, status: "ISSUED", created_at: "2026-06-01 09:00", approved_at: "2026-06-01 13:00", reject_reason: "" },
  { id: 109, student_id: "S002", items: [{ item_id: 9, qty: 1 }], use_date: "2026-07-01", status: "REJECTED", created_at: "2026-06-28 09:00", approved_at: null, reject_reason: "อุปกรณ์ไม่เพียงพอในช่วงเวลาที่ขอ" },
  { id: 110, student_id: "S001", items: [{ item_id: 8, qty: 3 }], use_date: null, status: "CANCELLED", created_at: "2026-07-05 09:00", approved_at: null, reject_reason: "" },
];

const SEED_QUEUE = [
  { id: 1, item_id: 9, student_id: "S002", joined_at: "2026-07-18 10:00" },
  { id: 2, item_id: 9, student_id: "S003", joined_at: "2026-07-19 11:00" },
  { id: 3, item_id: 2, asset_tag: "UBU-EQ-002-01", equipment_id: 2, student_id: "S001", joined_at: "2026-07-20 09:00" },
];

const SEED_SUGGESTIONS = [
  { id: 1, student_id: "S001", name: "เก้าอี้เกมมิ่งสำหรับห้องซ้อม", detail: "อยากให้จัดซื้อเก้าอี้เกมมิ่งไว้ใช้ในห้องซ้อมกิจกรรม เพราะเก้าอี้เดิมชำรุด", status: "SUBMITTED", created_at: "2026-07-20 09:00" },
  { id: 2, student_id: "S002", name: "จอมอนิเตอร์เพิ่มเติม", detail: "ต้องการจอมอนิเตอร์เพิ่มสำหรับงานตัดต่อวิดีโอ", status: "ACKNOWLEDGED", created_at: "2026-07-10 09:00" },
  { id: 3, student_id: "S003", name: "โดรนถ่ายภาพมุมสูง", detail: "ใช้สำหรับถ่ายทำกิจกรรมของคณะ", status: "PURCHASE_PLAN", created_at: "2026-06-15 09:00" },
];

const SEED_PURCHASES = [
  { id: 1, name: "เครื่องพิมพ์ 3 มิติ", detail: "สำหรับสนับสนุนงานโครงงานนักศึกษาสายวิศวกรรม", created_by: "T001", created_at: "2026-07-05 09:00" },
];

const SEED_DAMAGE_REPORTS = [
  {
    id: 1,
    student_id: "S001",
    student_name: "สมชาย ใจดี",
    equipment_id: 16,
    durable_material_id: null,
    asset_tag: "UBU-EQ-016-01",
    item_name: "จอคอมพิวเตอร์ Dell 24 นิ้ว (Full HD)",
    origin_location: "ห้อง EN6-101 · ตู้ B2 ชั้น 2",
    location: "ห้องแล็บโปรเจกต์ EN6-304",
    symptom: "หน้าจอไม่แสดงผล / ภาพกระพริบ — สาย HDMI หลวม ภาพติดๆ ดับๆ",
    photo: "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=300",
    status: "PENDING",
    created_at: "2026-07-23 10:30"
  },
  {
    id: 2,
    student_id: "S003",
    student_name: "วิชัย ตั้งใจ",
    equipment_id: 1,
    durable_material_id: null,
    asset_tag: "UBU-EQ-001-03",
    item_name: "โปรเจกเตอร์ Epson EB-X400",
    origin_location: "ห้อง EN6-101 · ตู้ A1 ชั้น 1",
    location: "ห้อง EN6-101 · ตู้ A1 ชั้น 1",
    symptom: "เครื่องทำงานผิดปกติ / มีเสียงดัง / ร้อนจัด — หลอดภาพแสงดรอปและพัดลมดังผิดปกติ",
    photo: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300",
    status: "IN_PROGRESS",
    created_at: "2026-07-20 14:15"
  }
];

const SEED_EVAL_FORM = {
  published: true,
  questions: [
    { id: 1, text: "ความพึงพอใจต่อสภาพของสิ่งของที่ยืม", type: "rating" },
    { id: 2, text: "ความรวดเร็วในการยืม-คืน", type: "rating" },
    { id: 3, text: "ข้อเสนอแนะเพิ่มเติม", type: "text" },
  ],
};

const SEED_EVAL_RESPONSES = [];

const SEED_SETTINGS = {
  fine_rate_per_day: 10, // อัตราค่าปรับยืมเกินกำหนด (บาท/วัน)
};

const SEED_UNITS = [
  { 
    asset_tag: "UBU-EQ-001-01", item_id: 1, status: "AVAILABLE", note: "", rating: 5, 
    reviews: [
      { student_name: "สมชาย ใจดี", rating: 5, comment: "สภาพดีเยี่ยม จอสว่างชัดเจนมาก พัดลมระบายอากาศเงียบ ใช้งานนำเสนอผ่านราบรื่น", created_at: "2026-06-12" },
      { student_name: "กิตติศักดิ์ มั่นคง", rating: 5, comment: "สีสด คมชัดมากครับ ความสว่างสู้แสงห้องประชุมได้ดีเยี่ยม", created_at: "2026-07-05" }
    ] 
  },
  { 
    asset_tag: "UBU-EQ-001-02", item_id: 1, status: "AVAILABLE", note: "", rating: 3, 
    reviews: [
      { student_name: "วิชัย ตั้งใจ", rating: 3, comment: "พัดลมระบายอากาศเสียงดังนิดหน่อย และความสว่างดรอปลงเล็กน้อย แต่ยังพอนำเสนอได้", created_at: "2026-07-01" }
    ] 
  },
  { 
    asset_tag: "UBU-EQ-001-03", item_id: 1, status: "DAMAGED", note: "หลอดภาพเสื่อมสภาพจากการยืม", rating: 2, 
    reviews: [
      { student_name: "สมหญิง มีดี", rating: 2, comment: "จอภาพสีเพี้ยนออกโทนเหลือง และหลอดภาพติดๆ ดับๆ แสงดรอปมาก", created_at: "2026-07-15" }
    ] 
  },
  { 
    asset_tag: "UBU-EQ-002-01", item_id: 2, status: "BORROWED", current_request_id: 103, note: "ยืมโดย S002", rating: 5, 
    reviews: [
      { student_name: "สมชาย ใจดี", rating: 5, comment: "เลนส์สะอาด ไร้ฝุ่น แบตเตอรี่อึดมาก ถ่ายภาพงานกิจกรรมได้ทั้งวัน", created_at: "2026-06-20" }
    ] 
  },
  { 
    asset_tag: "UBU-EQ-002-02", item_id: 2, status: "AVAILABLE", note: "", rating: 4, 
    reviews: [
      { student_name: "วิชัย ตั้งใจ", rating: 4, comment: "บอดี้มีรอยขีดข่วนตามการใช้งานเล็กน้อย แต่ระบบโฟกัสและชัตเตอร์ทำงานปกติทุกอย่าง", created_at: "2026-07-05" }
    ] 
  },
  { 
    asset_tag: "UBU-EQ-003-01", item_id: 3, status: "AVAILABLE", note: "", rating: 5, 
    reviews: [
      { student_name: "สมชาย ใจดี", rating: 5, comment: "ขาตั้งมั่นคง ล็อกขาแน่นดีมาก หมุนหัวเพลทได้นุ่มลื่นไม่ติดขัด", created_at: "2026-06-10" }
    ] 
  },
  { 
    asset_tag: "UBU-EQ-003-02", item_id: 3, status: "AVAILABLE", note: "", rating: 3, 
    reviews: [
      { student_name: "กิตติศักดิ์ มั่นคง", rating: 3, comment: "ตัวล็อกขาด้านซ้ายหลวมนิดหน่อย ต้องกดล็อกแรงขึ้นหน่อยครับ", created_at: "2026-07-02" }
    ] 
  },
  { asset_tag: "UBU-EQ-003-03", item_id: 3, status: "AVAILABLE", note: "", rating: 4, reviews: [] },
  { asset_tag: "UBU-EQ-003-04", item_id: 3, status: "AVAILABLE", note: "", rating: 5, reviews: [] },
  { asset_tag: "UBU-EQ-003-05", item_id: 3, status: "MAINTENANCE", note: "น็อตล็อกขาหลวม ส่งซ่อมคลัง", rating: 3, reviews: [{ student_name: "สมหญิง มีดี", rating: 3, comment: "ตัวล็อกขาหลวมเล็กน้อย", created_at: "2026-06-30" }] },
  { 
    asset_tag: "UBU-EQ-005-01", item_id: 5, status: "BORROWED", current_request_id: 104, note: "ยืมโดย S001", rating: 5, 
    reviews: [
      { student_name: "กิตติศักดิ์ มั่นคง", rating: 5, comment: "ใช้งานได้ดีมาก วัดค่ากระแสและแรงดันได้เสถียร", created_at: "2026-06-28" }
    ] 
  },
  { asset_tag: "UBU-EQ-005-02", item_id: 5, status: "AVAILABLE", note: "", rating: 4, reviews: [{ student_name: "สมชาย ใจดี", rating: 4, comment: "วัดแรงดันไฟฟ้าแม่นยำ สายโพรบสภาพดี", created_at: "2026-06-15" }] },
  { 
    asset_tag: "UBU-EQ-005-03", item_id: 5, status: "AVAILABLE", note: "", rating: 5, 
    reviews: [
      { student_name: "ธนกฤต วิเศษ", rating: 5, comment: "เครื่องวัดไฟตอบสนองไวมาก หน้าจอแสดงผลชัดเจน อุปกรณ์สายโพรบใหม่เอี่ยม", created_at: "2026-07-10" },
      { student_name: "ปิยะดา สดใส", rating: 5, comment: "สภาพเครื่องสมบูรณ์ 100% แบตเตอรี่เต็ม นำไปใช้ในแลปวิศวกรรมไฟฟ้าได้ยอดเยี่ยม", created_at: "2026-07-18" }
    ] 
  },
  { asset_tag: "UBU-EQ-005-04", item_id: 5, status: "AVAILABLE", note: "", rating: 4, reviews: [] },
  { asset_tag: "UBU-EQ-006-01", item_id: 6, status: "AVAILABLE", note: "", rating: 4, reviews: [] },
  { asset_tag: "UBU-EQ-006-02", item_id: 6, status: "AVAILABLE", note: "", rating: 5, reviews: [{ student_name: "วิชัย ตั้งใจ", rating: 5, comment: "หัวแร้งร้อนเร็ว ทำความร้อนได้สม่ำเสมอดีมาก", created_at: "2026-07-08" }] },
  { asset_tag: "UBU-EQ-006-03", item_id: 6, status: "AVAILABLE", note: "", rating: 5, reviews: [] },
  { asset_tag: "UBU-EQ-006-04", item_id: 6, status: "AVAILABLE", note: "", rating: 4, reviews: [] },
  { asset_tag: "UBU-EQ-006-05", item_id: 6, status: "AVAILABLE", note: "", rating: 5, reviews: [] },
  { asset_tag: "UBU-EQ-006-06", item_id: 6, status: "AVAILABLE", note: "", rating: 4, reviews: [] },
  { asset_tag: "UBU-EQ-010-01", item_id: 10, status: "BORROWED", current_request_id: 104, note: "ยืมโดย S001", rating: 4, reviews: [] },
  { asset_tag: "UBU-EQ-010-02", item_id: 10, status: "AVAILABLE", note: "", rating: 5, reviews: [{ student_name: "สมชาย ใจดี", rating: 5, comment: "ลำโพงเสียงใส เบสแน่น เชื่อมต่อบลูทูธได้เร็วมาก", created_at: "2026-06-25" }] },
  { asset_tag: "UBU-EQ-010-03", item_id: 10, status: "AVAILABLE", note: "", rating: 4, reviews: [] },
  { asset_tag: "UBU-EQ-010-04", item_id: 10, status: "DAMAGED", note: "ดอกลำโพงแตก แจ้งคืนชำรุด", rating: 1, reviews: [{ student_name: "วิชัย ตั้งใจ", rating: 1, comment: "เสียงแตกพร่า ไม่สามารถเร่งเสียงได้", created_at: "2026-07-12" }] },
  { asset_tag: "UBU-EQ-011-01", item_id: 11, status: "AVAILABLE", note: "", rating: 5, reviews: [{ student_name: "กิตติศักดิ์ มั่นคง", rating: 5, comment: "ประแจและไขควงครบชุด เครื่องมือสะอาดเป็นระเบียบ", created_at: "2026-07-10" }] },
  { asset_tag: "UBU-EQ-011-02", item_id: 11, status: "AVAILABLE", note: "", rating: 4, reviews: [] },
  { asset_tag: "UBU-EQ-011-03", item_id: 11, status: "AVAILABLE", note: "", rating: 5, reviews: [] },
  { asset_tag: "UBU-EQ-013-01", item_id: 13, status: "DAMAGED", note: "หลอดไฟขาด รอดำเนินการซ่อม", rating: 1, reviews: [] },
  { asset_tag: "UBU-EQ-016-01", item_id: 16, status: "BORROWED", current_request_id: 105, note: "ยืมโดย S001", rating: 5, reviews: [{ student_name: "สมชาย ใจดี", rating: 5, comment: "จอภาพคมชัด สีตรง ใช้ทำโครงงานดีมาก", created_at: "2026-07-10" }] },
  { asset_tag: "UBU-EQ-016-02", item_id: 16, status: "BORROWED", current_request_id: 105, note: "ยืมโดย S001", rating: 5, reviews: [] },
  { asset_tag: "UBU-EQ-016-03", item_id: 16, status: "AVAILABLE", note: "", rating: 5, reviews: [] },
];

/* ------------------------------ localStorage ----------------------------- */

const DB_VERSION = "2026-11-12-queue-est-v2";

function checkDbVersion() {
  try {
    const currentVer = localStorage.getItem(LS_PREFIX + "db_version");
    if (currentVer !== DB_VERSION) {
      const keepKeys = [LS_PREFIX + "current_role", LS_PREFIX + "current_user"];
      Object.keys(localStorage)
        .filter(k => k.startsWith(LS_PREFIX) && !keepKeys.includes(k))
        .forEach(k => localStorage.removeItem(k));
      localStorage.setItem(LS_PREFIX + "db_version", DB_VERSION);
    }
  } catch (e) {}
}
checkDbVersion();

function loadData(key, fallback) {
  const raw = localStorage.getItem(LS_PREFIX + key);
  if (!raw) return JSON.parse(JSON.stringify(fallback));
  try { return JSON.parse(raw); } catch (e) { return JSON.parse(JSON.stringify(fallback)); }
}
function saveData(key, data) {
  localStorage.setItem(LS_PREFIX + key, JSON.stringify(data));
}
function db(key) {
  const map = {
    rooms: SEED_ROOMS,
    categories: SEED_CATEGORIES, positions: SEED_POSITIONS, items: SEED_ITEMS, units: SEED_UNITS,
    students: SEED_STUDENTS, staffs: SEED_STAFFS, admins: SEED_ADMINS,
    whitelist_student: SEED_WHITELIST_STUDENT, whitelist_staff: SEED_WHITELIST_STAFF,
    role_overrides: SEED_ROLE_OVERRIDES, requests: SEED_REQUESTS, queue: SEED_QUEUE,
    suggestions: SEED_SUGGESTIONS, purchases: SEED_PURCHASES,
    eval_form: SEED_EVAL_FORM, eval_responses: SEED_EVAL_RESPONSES,
    cart: [], item_statuses: SEED_ITEM_STATUSES, admin_blocked: SEED_ADMIN_BLOCKED_EMAILS,
    settings: SEED_SETTINGS,
    damage_reports: SEED_DAMAGE_REPORTS,
  };
  return loadData(key, map[key]);
}
function dbSave(key, data) { saveData(key, data); }

function addDamageReport(report) {
  const list = db("damage_reports") || [];
  const newId = nextId(list);
  const stu = currentStudent();
  const curUid = currentUserId() || "S001";
  const sym = report.symptom || report.damage_detail || "";
  const newReport = {
    id: newId,
    user_id: curUid,
    equipment_id: report.equipment_id !== undefined ? report.equipment_id : null,
    durable_material_id: report.durable_material_id !== undefined ? report.durable_material_id : null,
    item_name: report.item_name || "",
    location: report.location || "",
    symptom: sym,
    photo: report.photo || null,
    status: "PENDING",
    created_at: new Date().toISOString().replace('T', ' ').slice(0, 19),
    // Fallback for legacy mockup compatibility:
    student_id: curUid,
    student_name: stu ? stu.name : "นักศึกษา",
    damage_detail: sym,
    ...report
  };
  newReport.symptom = sym;
  list.unshift(newReport);
  dbSave("damage_reports", list);
  return newReport;
}

function resetAllData() {
  const keepKeys = [LS_PREFIX + "current_role", LS_PREFIX + "current_user"];
  Object.keys(localStorage).filter(k => k.startsWith(LS_PREFIX) && !keepKeys.includes(k))
    .forEach(k => localStorage.removeItem(k));
  localStorage.setItem(LS_PREFIX + "db_version", DB_VERSION);
  alert("รีเซ็ตข้อมูลตัวอย่างเรียบร้อยแล้ว");
  location.reload();
}

/* --------------------------------- Session -------------------------------- */

function getRole() { return localStorage.getItem(LS_PREFIX + "current_role"); }
function setRole(role, userId) {
  localStorage.setItem(LS_PREFIX + "current_role", role);
  localStorage.setItem(LS_PREFIX + "current_user", userId || (role === "student" ? "S001" : role === "staff" ? "T001" : "A001"));
}
function currentUserId() { return localStorage.getItem(LS_PREFIX + "current_user"); }
function currentStudent() { return db("students").find(s => s.id === currentUserId()); }
function currentStaff() { return db("staffs").find(s => s.id === currentUserId()) || SEED_STAFFS[0]; }

/* --------------------------------- Helpers -------------------------------- */

function notifyParentPage(stateKey) {
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: "yuemdee-page", page: stateKey }, "*");
    }
  } catch (e) { /* standalone open ไม่มี parent - เงียบไว้ */ }
}

function qparam(name) { return (window.currentParams && window.currentParams[name] !== undefined) ? window.currentParams[name] : new URLSearchParams(location.search).get(name); }

function fmtDate(d) {
  if (!d) return "-";
  return d;
}

function daysLeft(dueDateStr) {
  const due = new Date(dueDateStr + "T00:00:00");
  const today = new Date("2026-07-23T00:00:00"); // "วันนี้" จำลองของระบบ ให้ตรงกับ current date จริงของสภาพแวดล้อม
  return Math.round((due - today) / 86400000);
}

function getFineRatePerDay(req) {
  if (req && Array.isArray(req.items)) {
    const allItems = db("items");
    let totalRate = 0;
    req.items.forEach(it => {
      if (it.returned) return;
      const itemObj = allItems.find(x => x.id === Number(it.item_id));
      if (!itemObj || itemObj.type === "material") return;
      const rate = itemObj.fine_rate_per_day !== undefined && itemObj.fine_rate_per_day !== null
        ? Number(itemObj.fine_rate_per_day)
        : (itemObj.type === "equipment" ? 20 : 10);
      const unreturnedQty = Math.max(1, (Number(it.qty) || 1) - (Number(it.returned_qty) || 0));
      totalRate += rate * unreturnedQty;
    });
    if (totalRate > 0) return totalRate;
  }
  return 20;
}

function calculateOverdueFine(req) {
  if (!req) return 0;
  if (req.custom_fine !== undefined) return req.custom_fine;
  if (!req.due_date || req.status === "RETURNED" || req.status === "ISSUED" || req.status === "CANCELLED" || req.status === "REJECTED" || req.status === "EXPIRED") {
    return req.fine_amount ? req.fine_amount : 0;
  }
  const left = daysLeft(req.due_date);
  if (left < 0) {
    const overdueDays = Math.abs(left);
    return overdueDays * getFineRatePerDay(req);
  }
  return 0;
}

function getOverdueDays(req) {
  if (!req || !req.due_date) return 0;
  const left = daysLeft(req.due_date);
  return left < 0 ? Math.abs(left) : 0;
}

function getUnitsByItemId(itemId) {
  return db("units").filter(u => u.item_id === Number(itemId));
}

function getUnitByAssetTag(assetTag) {
  return db("units").find(u => u.asset_tag === assetTag);
}

function addUnitReview(assetTag, studentName, rating, comment) {
  const units = db("units");
  const unit = units.find(u => u.asset_tag === assetTag);
  if (unit) {
    unit.reviews = unit.reviews || [];
    unit.reviews.unshift({ student_name: studentName, rating: Number(rating), comment: comment, created_at: "2026-07-23" });
    // Recalculate average rating
    const total = unit.reviews.reduce((acc, r) => acc + r.rating, 0);
    unit.rating = Math.round(total / unit.reviews.length);
    dbSave("units", units);
  }
}

function isPieceEvaluated(requestId, origItemIdx, assetTag) {
  const evals = db("eval_responses") || [];
  return evals.some(e => {
    if (e.request_id !== Number(requestId)) return false;
    if (assetTag && e.asset_tag && e.asset_tag === assetTag) return true;
    if (origItemIdx !== undefined && origItemIdx !== null && e.orig_item_idx === Number(origItemIdx)) return true;
    return false;
  });
}

function getPieceEvaluation(requestId, origItemIdx, assetTag) {
  const evals = db("eval_responses") || [];
  return evals.find(e => {
    if (e.request_id !== Number(requestId)) return false;
    if (assetTag && e.asset_tag && e.asset_tag === assetTag) return true;
    if (origItemIdx !== undefined && origItemIdx !== null && e.orig_item_idx === Number(origItemIdx)) return true;
    return false;
  });
}

function getRequestEvaluationProgress(requestId) {
  const reqs = db("requests") || [];
  const r = reqs.find(x => x.id === Number(requestId));
  if (!r) return { evaluated: 0, total: 0, allDone: false };
  const items = r.items || [];
  const total = items.length;
  let evaluated = 0;
  items.forEach((it, idx) => {
    if (isPieceEvaluated(r.id, idx, it.asset_tag)) evaluated++;
  });
  return { evaluated, total, allDone: total > 0 && evaluated >= total };
}

const STATUS_LABEL = {
  PENDING: "รอเจ้าหน้าที่ตรวจของ", REJECTED: "ปฏิเสธแล้ว",
  EXPIRED: "หมดอายุ", BORROWING: "กำลังยืม", RETURN_PENDING: "รอเจ้าหน้าที่ตรวจรับคืน",
  RETURNED: "คืนสำเร็จ", ISSUED: "เบิกสำเร็จ", CANCELLED: "ยกเลิกแล้ว",
  APPROVED: "อนุมัติแล้ว",
  SUBMITTED: "ส่งข้อเสนอแนะแล้ว", ACKNOWLEDGED: "เจ้าหน้ารับทราบแล้ว", PURCHASE_PLAN: "เพิ่มในแผนจัดซื้อแล้ว",
  RETIRED: "ปลดระวาง",
};
const STATUS_COLOR = {
  PENDING: "amber", REJECTED: "red", EXPIRED: "gray",
  BORROWING: "yellow", RETURN_PENDING: "amber", RETURNED: "green", ISSUED: "green",
  CANCELLED: "gray", APPROVED: "green",
  SUBMITTED: "blue", ACKNOWLEDGED: "indigo", PURCHASE_PLAN: "green",
  RETIRED: "gray",
};
function badgeHtml(statusKey) {
  const label = STATUS_LABEL[statusKey] || statusKey;
  const color = STATUS_COLOR[statusKey] || "gray";
  return `<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold bg-${color}-100 text-${color}-700">${label}</span>`;
}

const TYPE_LABEL = {
  material: "วัสดุสิ้นเปลือง (เบิกใช้)",
  durable_material: "วัสดุคงทน (ยืม-คืน)",
  equipment: "ครุภัณฑ์ (ยืม-คืน)",
};
function typeBadgeHtml(type) {
  if (type === "durable_material") {
    return `<span class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold bg-sky-50 text-sky-800 border border-sky-200">วัสดุคงทน (ยืม-คืน)</span>`;
  }
  if (type === "equipment") {
    return `<span class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">ครุภัณฑ์ (ยืม-คืน)</span>`;
  }
  return `<span class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold bg-teal-50 text-teal-700 border border-teal-200">วัสดุสิ้นเปลือง (เบิกใช้)</span>`;
}

function roomById(id) { return db("rooms").find(r => r.id === Number(id)); }
function itemById(id) { return db("items").find(i => i.id === Number(id)); }
function categoryById(id) { return db("categories").find(c => c.id === Number(id)); }
function positionById(id) { return db("positions").find(p => p.id === Number(id)); }
function studentById(id) { return db("students").find(s => s.id === id); }

function toastBanner(msg, type) {
  type = type || "success";
  const colors = { success: "bg-green-50 border-green-300 text-green-800", error: "bg-red-50 border-red-300 text-red-800", info: "bg-blue-50 border-blue-300 text-blue-800" };
  let host = document.getElementById("toast-host");
  if (!host) {
    host = document.createElement("div");
    host.id = "toast-host";
    host.className = "fixed top-4 right-4 z-50 flex flex-col gap-2";
    document.body.appendChild(host);
  }
  const el = document.createElement("div");
  el.className = "border rounded-xl shadow-lg px-4 py-3 text-sm font-medium " + colors[type];
  el.textContent = msg;
  host.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

function nextId(arr) { return arr.length ? Math.max(...arr.map(x => x.id)) + 1 : 1; }

/* ------------------------- Config: เมนู/หน้าแรกต่อ role ------------------------- */

function getActiveBorrowItemLocation(assetTag, itemId) {
  const reqs = db("requests") || [];
  for (const r of reqs) {
    if (r.status === "BORROWING" || r.status === "RETURN_PENDING") {
      for (const it of (r.items || [])) {
        if (!it.returned && ((assetTag && it.asset_tag === assetTag) || (!assetTag && it.item_id === Number(itemId)))) {
          return {
            request_id: r.id,
            student_id: r.student_id,
            current_location: it.current_location || "",
            moved_at: it.moved_at || ""
          };
        }
      }
    }
  }
  return null;
}

/* -------------------- ระบบคำนวณวันประมาณการพร้อมยืมสำหรับคิว -------------------- */
function getQueueEstimate(itemId, assetTag, position = 1) {
  const requests = db("requests") || [];
  const items = db("items") || [];
  const units = db("units") || [];
  const item = items.find(i => i.id === Number(itemId));
  const maxDays = (item && item.max_borrow_days) ? item.max_borrow_days : 7;

  let activeReq = null;
  let unit = null;

  if (assetTag) {
    unit = units.find(u => u.asset_tag === assetTag);
    if (unit && unit.current_request_id) {
      activeReq = requests.find(r => r.id === unit.current_request_id);
    }
    if (!activeReq) {
      activeReq = requests.find(r => (r.status === "BORROWING" || r.status === "PENDING") && r.items && r.items.some(it => it.asset_tag === assetTag && !it.returned));
    }
  }

  if (!activeReq && itemId) {
    activeReq = requests.find(r => (r.status === "BORROWING" || r.status === "PENDING") && r.items && r.items.some(it => it.item_id === Number(itemId) && !it.returned));
  }

  let baseDueDateStr = "";
  let isSpecialLongBorrow = false;
  let borrowerDueDays = 0;

  if (activeReq && activeReq.due_date) {
    baseDueDateStr = activeReq.due_date;
    if (activeReq.use_date) {
      const d1 = new Date(activeReq.use_date);
      const d2 = new Date(activeReq.due_date);
      borrowerDueDays = Math.round((d2 - d1) / (1000 * 60 * 60 * 24));
      if (borrowerDueDays > maxDays) {
        isSpecialLongBorrow = true;
      }
    }
  } else {
    // Current simulated date is in late July 2026 (2026-07-23)
    const base = new Date("2026-07-23");
    base.setDate(base.getDate() + maxDays);
    baseDueDateStr = base.toISOString().slice(0, 10);
  }

  const baseDate = new Date(baseDueDateStr);
  const additionalDays = 1 + (Math.max(1, Number(position)) - 1) * maxDays;
  const estDate = new Date(baseDate);
  estDate.setDate(estDate.getDate() + additionalDays);

  const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
  const dateFormatted = `${estDate.getDate()} ${thaiMonths[estDate.getMonth()]} ${estDate.getFullYear()}`;
  const baseDueDateFormatted = `${baseDate.getDate()} ${thaiMonths[baseDate.getMonth()]} ${baseDate.getFullYear()}`;

  let reasonNote = "";
  if (isSpecialLongBorrow) {
    reasonNote = `ผู้ยืมปัจจุบันได้รับอนุมัติยืมนานพิเศษ (${borrowerDueDays} วัน · กำหนดคืน: ${baseDueDateFormatted})`;
  } else if (activeReq && activeReq.due_date) {
    reasonNote = `คำนวณจากกำหนดคืนของผู้ยืมปัจจุบัน (${baseDueDateFormatted})`;
  } else {
    reasonNote = `ประมาณการจากระยะเวลายืมปกติ (${maxDays} วัน)`;
  }

  if (position > 1) {
    reasonNote += ` + รอคิวก่อนหน้า ${position - 1} คน (คนละไม่เกิน ${maxDays} วัน)`;
  }

  return {
    estimatedDate: estDate.toISOString().slice(0, 10),
    dateFormatted,
    baseDueDate: baseDueDateStr,
    baseDueDateFormatted,
    isSpecialLongBorrow,
    borrowerDueDays,
    maxDays,
    position,
    activeReq,
    reasonNote
  };
}

function showQueueSuccessModal({ item, assetTag, position, estimate, onDone }) {
  let existingModal = document.getElementById("queue-success-modal");
  if (existingModal) existingModal.remove();

  const modal = document.createElement("div");
  modal.id = "queue-success-modal";
  modal.className = "fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4";
  modal.innerHTML = `
    <div class="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-gray-100 overflow-hidden transform transition-all p-6 space-y-4">
      <div class="text-center">
        <div class="w-14 h-14 bg-amber-100 text-amber-600 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-3 shadow-inner">
          ⏳
        </div>
        <h3 class="text-lg font-bold text-gray-900">จองคิวสำเร็จ!</h3>
        <p class="text-xs text-gray-500 mt-1">คุณได้เข้าสู่คิวการยืมเรียบร้อยแล้ว</p>
      </div>

      <div class="bg-gray-50 rounded-2xl p-4 border border-gray-200/80 space-y-3">
        <div class="flex items-center gap-3">
          <div class="text-3xl">${item?.image || '📦'}</div>
          <div class="flex-1 min-w-0">
            <h4 class="font-bold text-sm text-gray-900 truncate">${item?.name || 'สิ่งของ'}</h4>
            <div class="flex items-center gap-2 mt-0.5 flex-wrap">
              ${assetTag ? `<span class="bg-indigo-50 text-indigo-700 font-mono text-[11px] font-bold px-2 py-0.5 rounded border border-indigo-200">🏷️ ${assetTag}</span>` : ''}
              <span class="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                ลำดับคิวของคุณ: <span class="font-bold">ที่ ${position}</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Estimated Date Highlight -->
        <div class="bg-white rounded-xl p-3 border border-blue-200 shadow-2xs">
          <div class="flex items-center gap-2 text-xs text-blue-900 font-semibold mb-1">
            <span class="text-base">📅</span>
            <span>ประมาณการวันที่คาดว่าจะได้ยืม:</span>
          </div>
          <div class="text-xl font-extrabold text-blue-700 ml-6 tracking-wide">
            ${estimate.dateFormatted}
          </div>
          <div class="text-[11px] text-gray-600 mt-1.5 ml-6 leading-relaxed">
            ${estimate.isSpecialLongBorrow ? '<div class="inline-flex items-center gap-1 font-semibold text-amber-800 bg-amber-100 px-2 py-0.5 rounded-md mb-1 text-[11px]">⚠️ ผู้ยืมปัจจุบันขอยืมนานพิเศษ</div><br>' : ''}
            <span>${estimate.reasonNote}</span>
          </div>
        </div>

        <p class="text-[11px] text-gray-400 text-center leading-tight">
          * วันที่ดังกล่าวเป็นเพียงการประมาณการเบื้องต้น หากผู้ยืมส่งคืนก่อนหรือหลังกำหนด ระบบจะอัปเดตสถานะและแจ้งเตือนคุณทันทีที่ของพร้อมยืม
        </p>
      </div>

      <div class="flex flex-col sm:flex-row gap-2 pt-1">
        <button id="qsm-btn-view" class="flex-1 bg-blue-600 hover:bg-blue-700 active:scale-[0.98] text-white font-semibold text-xs py-3 px-4 rounded-xl shadow-sm transition-all cursor-pointer text-center">
          📋 ไปที่หน้ารายการคิวของฉัน
        </button>
        <button id="qsm-btn-close" class="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold text-xs py-3 px-4 rounded-xl transition-all cursor-pointer text-center">
          ตกลง / ปิด
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  document.getElementById("qsm-btn-view").onclick = () => {
    modal.remove();
    navigate("queue-list");
  };
  document.getElementById("qsm-btn-close").onclick = () => {
    modal.remove();
    if (typeof onDone === "function") onDone();
  };
}

const MENU = {
  student: [
    { key: "request-list", label: "หน้าหลัก", icon: "🏠" },
    { key: "profile", label: "โปรไฟล์ส่วนตัว", icon: "👤" },
    { key: "item-list", label: "รายการวัสดุ/ครุภัณฑ์", icon: "📋" },
    { key: "cart", label: "ตะกร้า", icon: "🛒" },
    { key: "queue-list", label: "คิวของฉัน", icon: "⏳" },
    { key: "history", label: "ประวัติการยืม", icon: "📜" },
    { key: "report-damage", label: "แจ้งอุปกรณ์ชำรุด", icon: "🛠️" },
    { key: "suggestion", label: "เสนอแนะสิ่งของ", icon: "💡" },
  ],
  staff: [
    { key: "staff-dashboard", label: "แดชบอร์ด", icon: "📊" },
    { key: "pending-requests", label: "คำขอรออนุมัติ", icon: "✅" },
    { key: "return-list", label: "รับคืนครุภัณฑ์", icon: "↩️" },
    { key: "damaged-equipment", label: "ครุภัณฑ์เสียหาย", icon: "⚠️" },
    { key: "all-history", label: "ประวัติทั้งระบบ", icon: "📜" },
    { key: "item-overview", label: "จัดการคลังสิ่งของ", icon: "📦" },
    { key: "student-list", label: "รายชื่อนักศึกษา", icon: "🎓" },
    { key: "suggestion-review", label: "คำเสนอแนะสิ่งของ", icon: "💡" },
    { key: "purchase-add", label: "รายการจัดซื้อ", icon: "🧾" },
    { key: "report-export", label: "ส่งออกรายงาน", icon: "📤" },
  ],
  admin: [
    { key: "user-list", label: "จัดการบัญชีและสิทธิ์ผู้ใช้", icon: "👥" },
    { key: "personnel-export", label: "ส่งออกรายชื่อผู้ใช้งาน (CSV)", icon: "📤" },
  ],
};
const ROLE_LABEL = { student: "นักศึกษา", staff: "เจ้าหน้าที่", admin: "ผู้ดูแลระบบ" };
const HOME_PAGE = { student: "request-list", staff: "staff-dashboard", admin: "user-list" };

window.currentPageKey = window.currentPageKey || null;
window.currentParams = window.currentParams || {};

/* ----------------------------------------------------------------------------
 * navigate() — ใช้เรียกจากภายในหน้า pages/*.html เท่านั้น
 * นำทางด้วย location.href เสมอ (เปลี่ยนเอกสารของตัวเอง) ไม่ว่าจะเปิดอยู่ใน
 * <iframe> ของ index.html หรือเปิดไฟล์ตรงจาก file:// แบบเดี่ยวก็ตาม
 *
 * ตั้งใจไม่เรียกข้าม frame ผ่าน window.parent.someFunction() เพราะ browser
 * (โดยเฉพาะ Chrome/Edge) ถือว่าแต่ละไฟล์ที่เปิดผ่าน file:// เป็นคนละ origin กัน
 * (unique opaque origin ต่อไฟล์) การเข้าถึง property/function ข้าม frame แบบนี้
 * จะโดน same-origin policy บล็อกเงียบ ๆ (ปุ่มกดแล้วไม่ไปไหนเลย ไม่มี error โชว์)
 * — ฝั่ง shell (index.html) รู้ว่าหน้าไหนกำลังแสดงอยู่ผ่าน notifyParentPage()
 * ที่ส่งด้วย postMessage() แทน ซึ่งข้าม origin ได้โดยไม่ติดข้อจำกัดนี้
 * (index.html มี navigate() เวอร์ชันของตัวเองที่ประกาศทับตัวนี้อีกที หลังจากโหลดไฟล์นี้
 * สำหรับใช้ในบริบทของ shell เอง เช่น คลิกเมนู sidebar)
 * ---------------------------------------------------------------------------- */
function navigate(pageKey, params = {}) {
  window.currentParams = params || {};
  const qs = params && Object.keys(params).length ? "?" + new URLSearchParams(params).toString() : "";
  const cacheBuster = (qs ? "&" : "?") + "v=" + Date.now();
  window.location.href = "page-" + pageKey + ".html" + qs + cacheBuster;
}

/* ----------------------------------------------------------------------------
 * Auth guard ระดับหน้า — ทำงานเฉพาะไฟล์ pages/page-<key>.html (ไม่ทำงานใน index.html)
 * ถ้ายังไม่ล็อกอินและพยายามเปิดหน้าที่ไม่ใช่ welcome/login โดยตรง → เด้งกลับ welcome
 * (ชดเชยส่วนที่ auth guard เดิมของ navigate() แบบไฟล์เดียวเคยทำ ก่อนแยกเป็นหลายไฟล์)
 * ---------------------------------------------------------------------------- */
(function enforcePageAuthGuard() {
  const m = location.pathname.match(/\/page-([a-zA-Z0-9_-]+)\.html$/);
  if (!m) return; // ไม่ใช่ pages/page-*.html (เช่น index.html) — ข้าม
  const pageKey = m[1];
  if (pageKey !== "welcome" && pageKey !== "login" && !getRole()) {
    window.location.href = "page-welcome.html";
  }
})();
