/* ============================================================================
 * YuemDee · shared.js
 * มัสาก data + localStorage helpers + session/role helpers ใช้ร่วมกันทุกหน้า
 * ระบบจริง: Django ORM + django-allauth (Google OAuth) + session (UBU Single Sign-On)
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

const SEED_POSITIONS = [
  { id: 1, name: "ตู้ A1 ชั้น 1" },
  { id: 2, name: "ตู้ A1 ชั้น 2" },
  { id: 3, name: "ตู้ A2 ชั้น 1" },
  { id: 4, name: "ตู้ B1 ชั้น 1" },
  { id: 5, name: "ตู้ B2 ชั้น 1" },
];

const SEED_ITEM_STATUSES = ["พร้อมให้ยืม", "ชำรุด", "เลิกใช้งาน", "ปลดระวาง"]; // สถานะพื้นฐานของสิ่งของ (ตั้งค่าได้ที่ WarehouseSettings)

// type: "material" (วัสดุ/เบิก ไม่มีคืน) | "equipment" (ครุภัณฑ์ ต้องคืน)
const SEED_ITEMS = [
  { id: 1, name: "โปรเจกเตอร์ Epson EB-X400", type: "equipment", category_id: 1, position_id: 1, qty_total: 3, qty_available: 1, max_borrow_days: 7, base_status: "พร้อมให้ยืม", image: "📽️" },
  { id: 2, name: "กล้อง DSLR Canon EOS 200D", type: "equipment", category_id: 1, position_id: 1, qty_total: 2, qty_available: 1, max_borrow_days: 5, base_status: "พร้อมให้ยืม", image: "📷" },
  { id: 3, name: "ขาตั้งกล้อง Tripod", type: "equipment", category_id: 1, position_id: 2, qty_total: 5, qty_available: 2, max_borrow_days: 5, base_status: "พร้อมให้ยืม", image: "🎥" },
  { id: 4, name: "สาย HDMI 5 เมตร", type: "material", category_id: 4, position_id: 3, qty_total: 20, qty_available: 12, max_borrow_days: null, base_status: "พร้อมให้ยืม", image: "🔌" },
  { id: 5, name: "มัลติมิเตอร์", type: "equipment", category_id: 2, position_id: 3, qty_total: 4, qty_available: 4, max_borrow_days: 3, base_status: "พร้อมให้ยืม", image: "🔧" },
  { id: 6, name: "หัวแร้งบัดกรี", type: "equipment", category_id: 2, position_id: 3, qty_total: 6, qty_available: 3, max_borrow_days: 3, base_status: "พร้อมให้ยืม", image: "🛠️" },
  { id: 7, name: "กระดาษ A4 80 แกรม", type: "material", category_id: 3, position_id: 4, qty_total: 100, qty_available: 45, max_borrow_days: null, base_status: "พร้อมให้ยืม", image: "📄" },
  { id: 8, name: "ปากกาเคมี", type: "material", category_id: 3, position_id: 4, qty_total: 50, qty_available: 10, max_borrow_days: null, base_status: "พร้อมให้ยืม", image: "🖊️" },
  { id: 9, name: "ไมโครโฟนไร้สาย", type: "equipment", category_id: 5, position_id: 5, qty_total: 3, qty_available: 0, max_borrow_days: 3, base_status: "พร้อมให้ยืม", image: "🎤" },
  { id: 10, name: "ลำโพงพกพา Bluetooth", type: "equipment", category_id: 5, position_id: 5, qty_total: 4, qty_available: 2, max_borrow_days: 5, base_status: "พร้อมให้ยืม", image: "🔊" },
  { id: 11, name: "ชุดเครื่องมือช่าง", type: "equipment", category_id: 2, position_id: 3, qty_total: 3, qty_available: 1, max_borrow_days: 5, base_status: "พร้อมให้ยืม", image: "🧰" },
  { id: 12, name: "แบตเตอรี่ AA", type: "material", category_id: 4, position_id: 4, qty_total: 60, qty_available: 60, max_borrow_days: null, base_status: "พร้อมให้ยืม", image: "🔋" },
  { id: 13, name: "เครื่องฉายทึบแสง (Overhead)", type: "equipment", category_id: 1, position_id: 2, qty_total: 1, qty_available: 0, max_borrow_days: 7, base_status: "ไม่พร้อมใช้งาน", image: "📽️" },
];

const SEED_STUDENTS = [
  { id: "S001", name: "สมชาย ใจดี", email: "s001@ubu.ac.th", phone: "0812345678", first_login: "2026-06-01 09:12", last_login: "2026-07-22 14:03", blocked: false, block_reason: "", deadline_override: null },
  { id: "S002", name: "สมหญิง มีดี", email: "s002@ubu.ac.th", phone: "0898765432", first_login: "2026-06-03 10:00", last_login: "2026-07-20 08:40", blocked: true, block_reason: "ค้างคืนครุภัณฑ์เกินกำหนดหลายครั้ง", deadline_override: null },
  { id: "S003", name: "วิชัย ตั้งใจ", email: "s003@ubu.ac.th", phone: "", first_login: "2026-07-01 11:20", last_login: "2026-07-21 16:10", blocked: false, block_reason: "", deadline_override: null },
];

const SEED_STAFFS = [
  { id: "T001", name: "อ.สมหญิง ดูแลดี", email: "staff1@ubu.ac.th" },
];

const SEED_ADMINS = [
  { id: "A001", name: "ผู้ดูแลระบบ", email: "admin1@ubu.ac.th" },
];

const SEED_WHITELIST_STUDENT = ["s001@ubu.ac.th", "s002@ubu.ac.th", "s003@ubu.ac.th"];
const SEED_WHITELIST_STAFF = ["staff1@ubu.ac.th"];

const SEED_ADMIN_BLOCKED_EMAILS = []; // บัญชีที่ถูกแอดมินระงับสิทธิ์การเข้าสู่ระบบทั้งหมด (ต่างจาก student.blocked ที่จำกัดเฉพาะการยืม)

const SEED_ROLE_OVERRIDES = [
  { email: "s004@ubu.ac.th", role: "staff", reason: "หัวหน้าห้อง ได้รับมอบหมายช่วยงานคลัง", active: true },
];

// สถานะคำขอ: PENDING, APPROVED_WAIT_PICKUP, REJECTED, EXPIRED, BORROWING,
// RETURN_PENDING, RETURNED, ISSUED, CANCELLED
const SEED_REQUESTS = [
  { id: 101, student_id: "S001", items: [{ item_id: 1, qty: 1 }, { item_id: 4, qty: 2 }], reason: "นำเสนองานกลุ่มวิชาโครงงาน", use_date: "2026-07-30", status: "PENDING", created_at: "2026-07-23 08:30", approved_at: null, reject_reason: "" },
  { id: 102, student_id: "S001", items: [{ item_id: 3, qty: 1 }], reason: "ถ่ายวิดีโอสัมมนา", use_date: "2026-07-25", status: "APPROVED_WAIT_PICKUP", created_at: "2026-07-21 09:00", approved_at: "2026-07-22 10:00", reject_reason: "" },
  { id: 103, student_id: "S002", items: [{ item_id: 2, qty: 1 }], reason: "ถ่ายภาพกิจกรรมชมรม", use_date: "2026-07-10", status: "EXPIRED", created_at: "2026-07-01 09:00", approved_at: "2026-07-02 09:00", reject_reason: "" },
  { id: 104, student_id: "S001", items: [{ item_id: 5, qty: 1 }], reason: "ตรวจวงจรไฟฟ้าโครงงานจบ", use_date: "2026-07-18", status: "BORROWING", created_at: "2026-07-15 09:00", approved_at: "2026-07-15 13:00", picked_up_at: "2026-07-16 09:00", due_date: "2026-07-31", reject_reason: "" },
  { id: 105, student_id: "S001", items: [{ item_id: 6, qty: 1 }], reason: "ซ่อมอุปกรณ์ชมรมอิเล็กทรอนิกส์", use_date: "2026-07-05", status: "BORROWING", created_at: "2026-07-04 09:00", approved_at: "2026-07-04 13:00", picked_up_at: "2026-07-05 09:00", due_date: "2026-07-08", reject_reason: "" },
  { id: 106, student_id: "S001", items: [{ item_id: 10, qty: 1 }], reason: "จัดกิจกรรมเสียงตามสาย", use_date: "2026-07-10", status: "RETURN_PENDING", created_at: "2026-07-08 09:00", approved_at: "2026-07-08 13:00", picked_up_at: "2026-07-09 09:00", due_date: "2026-07-20", reject_reason: "" },
  { id: 107, student_id: "S001", items: [{ item_id: 3, qty: 1 }], reason: "ถ่ายรูปรับปริญญา", use_date: "2026-06-10", status: "RETURNED", created_at: "2026-06-05 09:00", approved_at: "2026-06-05 13:00", picked_up_at: "2026-06-06 09:00", due_date: "2026-06-13", returned_at: "2026-06-12 15:00", reject_reason: "" },
  { id: 108, student_id: "S001", items: [{ item_id: 7, qty: 5 }], reason: "พิมพ์รายงาน", use_date: null, status: "ISSUED", created_at: "2026-06-01 09:00", approved_at: "2026-06-01 13:00", picked_up_at: "2026-06-01 15:00", reject_reason: "" },
  { id: 109, student_id: "S002", items: [{ item_id: 9, qty: 1 }], reason: "อัดเสียงพากย์", use_date: "2026-07-01", status: "REJECTED", created_at: "2026-06-28 09:00", approved_at: null, reject_reason: "อุปกรณ์ไม่เพียงพอในช่วงเวลาที่ขอ" },
  { id: 110, student_id: "S001", items: [{ item_id: 8, qty: 3 }], reason: "งานประดิษฐ์ป้ายชมรม", use_date: null, status: "CANCELLED", created_at: "2026-07-05 09:00", approved_at: null, reject_reason: "" },
];

const SEED_QUEUE = [
  { id: 1, item_id: 9, student_id: "S002", joined_at: "2026-07-18 10:00" },
  { id: 2, item_id: 9, student_id: "S003", joined_at: "2026-07-19 11:00" },
  { id: 3, item_id: 2, student_id: "S001", joined_at: "2026-07-20 09:00" },
];

const SEED_SUGGESTIONS = [
  { id: 1, student_id: "S001", name: "เก้าอี้เกมมิ่งสำหรับห้องซ้อม", detail: "อยากให้จัดซื้อเก้าอี้เกมมิ่งไว้ใช้ในห้องซ้อมกิจกรรม เพราะเก้าอี้เดิมชำรุด", status: "SUBMITTED", created_at: "2026-07-20 09:00" },
  { id: 2, student_id: "S002", name: "จอมอนิเตอร์เพิ่มเติม", detail: "ต้องการจอมอนิเตอร์เพิ่มสำหรับงานตัดต่อวิดีโอ", status: "ACKNOWLEDGED", created_at: "2026-07-10 09:00" },
  { id: 3, student_id: "S003", name: "โดรนถ่ายภาพมุมสูง", detail: "ใช้สำหรับถ่ายทำกิจกรรมของคณะ", status: "PURCHASE_PLAN", created_at: "2026-06-15 09:00" },
];

const SEED_PURCHASES = [
  { id: 1, name: "เครื่องพิมพ์ 3 มิติ", detail: "สำหรับสนับสนุนงานโครงงานนักศึกษาสายวิศวกรรม", created_by: "T001", created_at: "2026-07-05 09:00" },
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

const SEED_UNITS = [
  { asset_tag: "UBU-EQ-001-01", item_id: 1, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-001-02", item_id: 1, status: "BORROWED", current_request_id: 104, note: "ยืมโดย S001" },
  { asset_tag: "UBU-EQ-001-03", item_id: 1, status: "DAMAGED", note: "หลอดภาพเสื่อมสภาพจากการยืม" },
  { asset_tag: "UBU-EQ-002-01", item_id: 2, status: "BORROWED", current_request_id: 103, note: "ยืมโดย S002" },
  { asset_tag: "UBU-EQ-002-02", item_id: 2, status: "BORROWED", current_request_id: 106, note: "ยืมโดย S001" },
  { asset_tag: "UBU-EQ-003-01", item_id: 3, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-003-02", item_id: 3, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-003-03", item_id: 3, status: "BORROWED", current_request_id: 102, note: "ยืมโดย S001" },
  { asset_tag: "UBU-EQ-003-04", item_id: 3, status: "BORROWED", current_request_id: 107, note: "ยืมโดย S001" },
  { asset_tag: "UBU-EQ-003-05", item_id: 3, status: "MAINTENANCE", note: "น็อตล็อกขาหลวม ส่งซ่อมคลัง" },
  { asset_tag: "UBU-EQ-005-01", item_id: 5, status: "BORROWED", current_request_id: 104, note: "" },
  { asset_tag: "UBU-EQ-005-02", item_id: 5, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-005-03", item_id: 5, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-005-04", item_id: 5, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-006-01", item_id: 6, status: "BORROWED", current_request_id: 105, note: "" },
  { asset_tag: "UBU-EQ-006-02", item_id: 6, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-006-03", item_id: 6, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-006-04", item_id: 6, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-006-05", item_id: 6, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-006-06", item_id: 6, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-010-01", item_id: 10, status: "BORROWED", current_request_id: 106, note: "" },
  { asset_tag: "UBU-EQ-010-02", item_id: 10, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-010-03", item_id: 10, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-010-04", item_id: 10, status: "DAMAGED", note: "ดอกลำโพงแตก แจ้งคืนชำรุด" },
  { asset_tag: "UBU-EQ-011-01", item_id: 11, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-011-02", item_id: 11, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-011-03", item_id: 11, status: "AVAILABLE", note: "" },
  { asset_tag: "UBU-EQ-013-01", item_id: 13, status: "DAMAGED", note: "หลอดไฟขาด รอดำเนินการซ่อม" },
];

/* ------------------------------ localStorage ----------------------------- */

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
    categories: SEED_CATEGORIES, positions: SEED_POSITIONS, items: SEED_ITEMS, units: SEED_UNITS,
    students: SEED_STUDENTS, staffs: SEED_STAFFS, admins: SEED_ADMINS,
    whitelist_student: SEED_WHITELIST_STUDENT, whitelist_staff: SEED_WHITELIST_STAFF,
    role_overrides: SEED_ROLE_OVERRIDES, requests: SEED_REQUESTS, queue: SEED_QUEUE,
    suggestions: SEED_SUGGESTIONS, purchases: SEED_PURCHASES,
    eval_form: SEED_EVAL_FORM, eval_responses: SEED_EVAL_RESPONSES,
    cart: [], item_statuses: SEED_ITEM_STATUSES, admin_blocked: SEED_ADMIN_BLOCKED_EMAILS,
  };
  return loadData(key, map[key]);
}
function dbSave(key, data) { saveData(key, data); }

function resetAllData() {
  const keepKeys = [LS_PREFIX + "current_role", LS_PREFIX + "current_user"];
  Object.keys(localStorage).filter(k => k.startsWith(LS_PREFIX) && !keepKeys.includes(k))
    .forEach(k => localStorage.removeItem(k));
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

const STATUS_LABEL = {
  PENDING: "รออนุมัติ", APPROVED_WAIT_PICKUP: "อนุมัติแล้ว/รอรับของ", REJECTED: "ปฏิเสธแล้ว",
  EXPIRED: "หมดอายุ", BORROWING: "กำลังยืม", RETURN_PENDING: "รอยืนยันการคืน",
  RETURNED: "คืนสำเร็จ", ISSUED: "เบิกสำเร็จ", CANCELLED: "ยกเลิกแล้ว",
  APPROVED: "อนุมัติแล้ว",
  SUBMITTED: "ส่งข้อเสนอแนะแล้ว", ACKNOWLEDGED: "เจ้าหน้ารับทราบแล้ว", PURCHASE_PLAN: "เพิ่มในแผนจัดซื้อแล้ว",
};
const STATUS_COLOR = {
  PENDING: "amber", APPROVED_WAIT_PICKUP: "blue", REJECTED: "red", EXPIRED: "gray",
  BORROWING: "yellow", RETURN_PENDING: "amber", RETURNED: "green", ISSUED: "green",
  CANCELLED: "gray", APPROVED: "green",
  SUBMITTED: "blue", ACKNOWLEDGED: "indigo", PURCHASE_PLAN: "green",
};
function badgeHtml(statusKey) {
  const label = STATUS_LABEL[statusKey] || statusKey;
  const color = STATUS_COLOR[statusKey] || "gray";
  return `<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold bg-${color}-100 text-${color}-700">${label}</span>`;
}

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

const MENU = {
  student: [
    { key: "request-list", label: "หน้าหลัก", icon: "🏠" },
    { key: "profile", label: "โปรไฟล์ส่วนตัว", icon: "👤" },
    { key: "item-list", label: "รายการวัสดุ/ครุภัณฑ์", icon: "📋" },
    { key: "position-map", label: "แผนผังตำแหน่งชั้นวาง", icon: "🗺️" },
    { key: "cart", label: "ตะกร้า", icon: "🛒" },
    { key: "queue-list", label: "คิวของฉัน", icon: "⏳" },
    { key: "history", label: "ประวัติการยืม", icon: "📜" },
    { key: "suggestion", label: "เสนอแนะสิ่งของ", icon: "💡" },
  ],
  staff: [
    { key: "staff-dashboard", label: "แดชบอร์ด", icon: "📊" },
    { key: "pending-requests", label: "คำขอรออนุมัติ", icon: "✅" },
    { key: "return-list", label: "รับคืนครุภัณฑ์", icon: "↩️" },
    { key: "all-history", label: "ประวัติทั้งระบบ", icon: "📜" },
    { key: "item-overview", label: "จัดการคลังสิ่งของ", icon: "📦" },
    { key: "warehouse-settings", label: "ตั้งค่าคลัง", icon: "⚙️" },
    { key: "student-list", label: "จัดการนักศึกษา", icon: "🎓" },
    { key: "suggestion-review", label: "คำเสนอแนะสิ่งของ", icon: "💡" },
    { key: "purchase-add", label: "รายการจัดซื้อ", icon: "🧾" },
    { key: "evaluation-form", label: "แบบประเมินความพึงพอใจ", icon: "⭐" },
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
  window.location.href = "page-" + pageKey + ".html" + qs;
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
