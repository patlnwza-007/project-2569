# ตัวอย่าง — Standalone Mockup ที่ทำตามกฎครบทุกข้อ (M3 · ข้อมูลอาจารย์)

> ตัวอย่างนี้ใช้ **M3 · Faculty App** เป็นโจทย์จริง (6 UC, 1 แอป, 4 หน้าจอ) — สร้างตาม [`mockup_generate_guide.md`](../guide/mockup_generate_guide.md) §2 (แยก panel + แยกไฟล์ตามหน้าใน state diagram) และใช้ design system จาก [`UI_django_frontend.md`](../guide/UI_django_frontend.md) ครบทุกข้อ (สีประจำแอป M3 = `orange`)
> อ้างอิงหน้าจอจาก [`m3/state/module_state_diagram.puml`](../../m3/state/module_state_diagram.puml) และ flow จาก [`m3/proposal/usecase_description.md`](../../m3/proposal/usecase_description.md)

จุดที่ตัวอย่างนี้สาธิตให้เห็น:
- **แยก panel** — `layout/topbar.js` และ `layout/sidebar.js` เป็นไฟล์เดี่ยว ใช้ร่วมทุกหน้า ไม่ปนกับเนื้อหาแต่ละหน้า
- **1 state = 1 ไฟล์ใน `pages/`** — FacultyList, Onboarding, AdjustStatus, OwnProfile ตรงกับ state diagram ครบ (UC-06 ไม่มีหน้าจอเพราะเป็น API ให้ M9 เรียก — ตรงตาม note ในไดอะแกรม)
- **`<script src>` ธรรมดา ไม่ใช้ fetch/import** — เปิดจาก `file://` ได้ตรง ๆ ตามเหตุผลใน guide §2
- **Role switcher** — สลับ HR ↔ Faculty แล้วเมนู/หน้าแรกเปลี่ยนตามสิทธิ์จริง
- **Alternative Flow ทำงานจริง** — ไม่เลือกบัญชี M0 → แจ้งเตือน (UC-01) · ปีจบเป็นอนาคต → ปฏิเสธ (UC-03) · ปรับเป็นเกษียณ/พ้นสภาพ → confirm ก่อน (UC-05)
- **localStorage** — เพิ่มอาจารย์/แก้โปรไฟล์แล้วเปลี่ยนหน้า ข้อมูลคงอยู่ + มีปุ่มรีเซ็ต
- **สีประจำโมดูล orange** ทุกจุด (โลโก้, ปุ่ม primary, active menu, focus ring) ส่วน badge สถานะใช้ semantic color แยกจากสีโมดูล

ตาราง Mapping (ตาม template §1):

| State | ไฟล์ | UC | Role | สถานะ |
|---|---|---|---|:---:|
| FacultyList | `pages/page-faculty-list.js` | UC-01(เข้า), UC-05(เข้า) | hr | ✅ |
| Onboarding | `pages/page-onboarding.js` | UC-01 | hr | ✅ |
| AdjustStatus | `pages/page-adjust-status.js` | UC-05 | hr | ✅ |
| OwnProfile | `pages/page-own-profile.js` | UC-02, UC-03, UC-04 | faculty | ✅ |

โครงไฟล์:

```
m3/mockup/
├── index.html
├── app.js
├── mock-data.js
├── layout/
│   ├── topbar.js
│   └── sidebar.js
└── pages/
    ├── page-login.js
    ├── page-faculty-list.js
    ├── page-onboarding.js
    ├── page-adjust-status.js
    └── page-own-profile.js
```

---

## `index.html`

```html
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>M3 · ข้อมูลอาจารย์ — Mockup</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style> body { font-family: 'Noto Sans Thai', sans-serif; } </style>
</head>
<body class="bg-gray-50 text-gray-800">

  <div id="topbar"></div>
  <div class="flex min-h-screen">
    <nav id="sidebar" class="w-56 bg-white border-r border-gray-200 p-3 shrink-0"></nav>
    <main id="main" class="flex-1 p-6 max-w-4xl"></main>
  </div>
  <footer class="text-center py-3">
    <button onclick="resetData()" class="text-xs text-gray-400 hover:text-red-600 underline">รีเซ็ตข้อมูลตัวอย่าง</button>
  </footer>

  <script src="mock-data.js"></script>
  <script src="layout/topbar.js"></script>
  <script src="layout/sidebar.js"></script>
  <script src="pages/page-login.js"></script>
  <script src="pages/page-faculty-list.js"></script>
  <script src="pages/page-onboarding.js"></script>
  <script src="pages/page-adjust-status.js"></script>
  <script src="pages/page-own-profile.js"></script>
  <script src="app.js"></script>
</body>
</html>
```

---

## `mock-data.js`

```js
// Mock data ตาม Data Entities ใน fn req/m3_faculty_management.md
const seedInstructors = [
  { id: 1, name: "ผศ.ดร.สมหญิง ใจดี", rank: "ผู้ช่วยศาสตราจารย์", dept: "วิศวกรรมคอมพิวเตอร์", status: "FULL_TIME",
    hired: "2015-06-01", quals: [{ level: "ป.เอก", field: "Computer Science", year: 2014 }], tags: ["AI/ML"] },
  { id: 2, name: "อ.ประยุทธ ขยันสอน", rank: "อาจารย์", dept: "วิศวกรรมคอมพิวเตอร์", status: "PART_TIME",
    hired: "2020-01-15", quals: [], tags: [] },
];
// ระบบจริง: ค้นหาบัญชีผ่าน M0 — GET /accounts?role=faculty (M0 UC-11) แล้ว consume event account.synced
const mockM0Accounts = [
  { id: "acc-101", name: "ดร.วิชัย รักเรียน", email: "wichai@ubu.ac.th" },
  { id: "acc-102", name: "อ.มานี มีวินัย", email: "manee@ubu.ac.th" },
];
const TAG_MASTER = ["AI/ML", "IoT", "Software Engineering", "Data Engineering", "Cybersecurity", "HCI"];
const STATUS_TH = { FULL_TIME: "ประจำ", PART_TIME: "พิเศษ", STUDY_LEAVE: "ลาศึกษาต่อ", RETIRED: "เกษียณ", TERMINATED: "พ้นสภาพ" };
// Badge ใช้ semantic color ไม่ใช่สีแอป (UI_django_frontend.md §2.1)
const STATUS_BADGE = {
  FULL_TIME: "bg-green-100 text-green-700", PART_TIME: "bg-amber-100 text-amber-700",
  STUDY_LEAVE: "bg-amber-100 text-amber-700", RETIRED: "bg-gray-100 text-gray-600", TERMINATED: "bg-red-100 text-red-700",
};

function loadData(key, fallback) { const s = localStorage.getItem(key); return s ? JSON.parse(s) : fallback; }
function saveData(key, data) { localStorage.setItem(key, JSON.stringify(data)); }
function resetData() { localStorage.clear(); location.reload(); }

let instructors = loadData("m3_instructors", seedInstructors);
```

---

## `layout/topbar.js`

```js
const Layout = window.Layout || (window.Layout = {});
Layout.topbar = {
  render() {
    const role = localStorage.getItem("current_role") || "hr";
    return `
      <header class="bg-white border-b border-gray-200 px-4 py-2.5 flex items-center justify-between sticky top-0 z-10">
        <div class="flex items-center gap-2">
          <span class="w-7 h-7 rounded-lg bg-orange-100 text-orange-700 flex items-center justify-center font-bold text-xs">M3</span>
          <span class="font-semibold text-sm">ERP บริหารหลักสูตร · ข้อมูลอาจารย์</span>
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500">บทบาท (จำลอง):</label>
          <select onchange="setRole(this.value)" class="border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="hr" ${role === "hr" ? "selected" : ""}>ฝ่ายบุคคล (HR/Admin)</option>
            <option value="faculty" ${role === "faculty" ? "selected" : ""}>อาจารย์ (Faculty)</option>
          </select>
        </div>
      </header>`;
  },
};
```

---

## `layout/sidebar.js`

```js
const Layout = window.Layout || (window.Layout = {});
// 1 รายการต่อ state ที่เป็น entry จากเมนู — ต้องตรงกับ roles ที่ประกาศใน pages/*.js
const MENU = [
  { key: "faculty-list", label: "รายการอาจารย์", roles: ["hr"] },
  { key: "own-profile", label: "โปรไฟล์ของฉัน", roles: ["faculty"] },
];
Layout.sidebar = {
  render(activeKey, role) {
    return `<p class="px-2 py-1 text-[11px] uppercase tracking-wide text-gray-400">เมนู</p>` +
      MENU.filter((m) => m.roles.includes(role)).map((m) => `
        <button onclick="go('${m.key}')"
          class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-left
            ${activeKey === m.key ? "bg-orange-50 text-orange-700 font-semibold" : "text-gray-600 hover:bg-gray-50"}">
          ${m.label}
        </button>`).join("");
  },
};
```

---

## `pages/page-login.js`

```js
const Pages = window.Pages || (window.Pages = {});
Pages["login"] = {
  render() {
    return `
      <div class="min-h-screen flex items-center justify-center">
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 max-w-sm w-full">
          <h2 class="text-lg font-semibold mb-4">เลือกบทบาทเพื่อทดลองใช้งาน</h2>
          <div class="space-y-2">
            <button onclick="loginAs('hr')" class="w-full bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-xl px-4 py-2">ฝ่ายบุคคล (HR/Admin)</button>
            <button onclick="loginAs('faculty')" class="w-full bg-white border border-gray-300 hover:bg-gray-50 text-sm rounded-xl px-4 py-2">อาจารย์ (Faculty)</button>
          </div>
        </div>
      </div>`;
  },
};
function loginAs(role) {
  localStorage.setItem("current_role", role);
  go(role === "hr" ? "faculty-list" : "own-profile");
}
```

---

## `pages/page-faculty-list.js` — UC-01(เข้า)/UC-05(เข้า)

```js
const Pages = window.Pages || (window.Pages = {});
Pages["faculty-list"] = {
  roles: ["hr"],
  render() {
    return `
      <div class="flex items-center justify-between mb-4">
        <div>
          <h1 class="text-2xl font-bold">รายการอาจารย์</h1>
          <p class="text-xs text-gray-500"><span id="count"></span> รายการ</p>
        </div>
        <button onclick="go('onboarding')"
          class="bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold rounded-xl px-4 py-2">＋ เพิ่มอาจารย์ใหม่</button>
      </div>
      <input id="q" oninput="Pages['faculty-list'].renderRows()" placeholder="ค้นหาชื่ออาจารย์..."
        class="w-full max-w-xs border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-orange-300">
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-xs uppercase tracking-wider text-gray-500">
            <tr>
              <th class="text-left px-4 py-3">ชื่อ-นามสกุล</th>
              <th class="text-left px-4 py-3">ตำแหน่ง/สังกัด</th>
              <th class="text-left px-4 py-3">สถานะ</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody id="rows"></tbody>
        </table>
      </div>`;
  },
  afterRender() { this.renderRows(); },
  renderRows() {
    const q = document.getElementById("q")?.value ?? "";
    const list = instructors.filter((i) => i.name.includes(q));
    document.getElementById("count").textContent = list.length;
    document.getElementById("rows").innerHTML = list.map((i) => `
      <tr class="border-t border-gray-100 hover:bg-gray-50">
        <td class="px-4 py-3">${i.name}</td>
        <td class="px-4 py-3 text-gray-500">${i.rank} · ${i.dept}</td>
        <td class="px-4 py-3"><span class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_BADGE[i.status]}">${STATUS_TH[i.status]}</span></td>
        <td class="px-4 py-3 text-right">
          <button onclick="localStorage.setItem('m3_status_target', ${i.id}); go('adjust-status')"
            class="text-orange-600 hover:bg-orange-50 rounded-lg px-3 py-1.5 text-sm">ปรับสถานะ</button>
        </td>
      </tr>`).join("") || `<tr><td colspan="4" class="px-4 py-10 text-center text-sm text-gray-400">ไม่พบข้อมูล</td></tr>`;
  },
};
```

---

## `pages/page-onboarding.js` — UC-01

```js
const Pages = window.Pages || (window.Pages = {});
Pages["onboarding"] = {
  roles: ["hr"],
  render() {
    return `
      <button onclick="go('faculty-list')" class="text-sm text-gray-500 hover:text-gray-700 mb-3">← กลับรายการอาจารย์</button>
      <h1 class="text-2xl font-bold mb-4">บันทึกอาจารย์ใหม่ (Onboarding)</h1>
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 max-w-lg space-y-4">
        <div>
          <label class="text-sm font-semibold text-gray-700">บัญชีผู้ใช้จาก M0</label>
          <select id="ob-account" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-orange-300">
            <option value="">— เลือกบัญชี —</option>
            ${mockM0Accounts.map((a) => `<option value="${a.id}">${a.name} (${a.email})</option>`).join("")}
          </select>
          <p class="text-xs text-gray-500 mt-1">ไม่พบบัญชี? ต้องสร้างที่ M0 ก่อนจึงเพิ่มอาจารย์ได้ (Alternative Flow UC-01)</p>
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">สังกัดภาควิชา</label>
          <input id="ob-dept" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-orange-300">
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">สถานะเริ่มต้น</label>
          <select id="ob-status" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mt-1">
            <option value="FULL_TIME">ประจำ</option><option value="PART_TIME">พิเศษ</option>
          </select>
        </div>
        <p id="ob-error" class="text-xs text-red-600 hidden"></p>
        <button onclick="Pages['onboarding'].save()"
          class="bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold rounded-xl px-4 py-2">บันทึก</button>
      </div>`;
  },
  save() {
    const acc = document.getElementById("ob-account").value;
    const err = document.getElementById("ob-error");
    if (!acc) { err.textContent = "ต้องเลือกบัญชีจาก M0 ก่อน — ถ้าไม่มีให้สร้างที่ M0 ก่อน"; err.classList.remove("hidden"); return; }
    err.classList.add("hidden");
    const account = mockM0Accounts.find((a) => a.id === acc);
    // ระบบจริง: POST แล้วผูก account_id — GET/PATCH /instructors/{id}
    instructors.push({ id: Date.now(), name: account.name, rank: "อาจารย์",
      dept: document.getElementById("ob-dept").value || "-", status: document.getElementById("ob-status").value,
      hired: "", quals: [], tags: [] });
    saveData("m3_instructors", instructors);
    alert("บันทึกอาจารย์ใหม่แล้ว (จำลอง audit log ผ่าน M10)");
    go("faculty-list");
  },
};
```

---

## `pages/page-adjust-status.js` — UC-05

```js
const Pages = window.Pages || (window.Pages = {});
Pages["adjust-status"] = {
  roles: ["hr"],
  render() {
    const target = instructors.find((i) => i.id === Number(localStorage.getItem("m3_status_target")));
    return `
      <button onclick="go('faculty-list')" class="text-sm text-gray-500 hover:text-gray-700 mb-3">← กลับรายการอาจารย์</button>
      <h1 class="text-2xl font-bold mb-4">ปรับสถานะอาจารย์</h1>
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 max-w-lg space-y-4">
        <p class="text-sm">อาจารย์: <span class="font-semibold">${target?.name ?? "-"}</span></p>
        <div>
          <label class="text-sm font-semibold text-gray-700">สถานะใหม่</label>
          <select id="st-status" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mt-1">
            <option value="FULL_TIME" ${target?.status === "FULL_TIME" ? "selected" : ""}>ประจำ</option>
            <option value="PART_TIME" ${target?.status === "PART_TIME" ? "selected" : ""}>พิเศษ</option>
            <option value="STUDY_LEAVE">ลาศึกษาต่อ</option>
            <option value="RETIRED">เกษียณ</option>
            <option value="TERMINATED">พ้นสภาพ</option>
          </select>
        </div>
        <button onclick="Pages['adjust-status'].save()"
          class="bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold rounded-xl px-4 py-2">บันทึก</button>
      </div>`;
  },
  save() {
    const target = instructors.find((i) => i.id === Number(localStorage.getItem("m3_status_target")));
    const v = document.getElementById("st-status").value;
    if (["RETIRED", "TERMINATED"].includes(v) &&
        !confirm("สถานะนี้มีผลต่อสิทธิ์การสอน/แต่งตั้ง — ยืนยันหรือไม่? (Alternative Flow UC-05)")) return;
    target.status = v;
    saveData("m3_instructors", instructors);
    alert("ปรับสถานะแล้ว");
    go("faculty-list");
  },
};
```

---

## `pages/page-own-profile.js` — UC-02/03/04 (3 แท็บในหน้าเดียว ตาม state diagram)

```js
const Pages = window.Pages || (window.Pages = {});
let curTab = "info"; // จำลอง login เป็นอาจารย์คนแรก
const me = () => instructors[0];

Pages["own-profile"] = {
  roles: ["faculty"],
  render() {
    return `
      <h1 class="text-2xl font-bold mb-4">โปรไฟล์วิชาชีพของฉัน</h1>
      <div class="flex gap-1 mb-4">
        <button onclick="Pages['own-profile'].setTab('info')" id="tabbtn-info" class="text-sm rounded-lg px-3 py-1.5">ข้อมูลวิชาชีพ</button>
        <button onclick="Pages['own-profile'].setTab('qual')" id="tabbtn-qual" class="text-sm rounded-lg px-3 py-1.5">คุณวุฒิการศึกษา</button>
        <button onclick="Pages['own-profile'].setTab('tags')" id="tabbtn-tags" class="text-sm rounded-lg px-3 py-1.5">Expertise Tags</button>
      </div>
      <div id="tab-content"></div>`;
  },
  afterRender() { this.renderTabs(); },
  setTab(t) { curTab = t; this.renderTabs(); },
  renderTabs() {
    ["info", "qual", "tags"].forEach((t) => {
      const btn = document.getElementById("tabbtn-" + t);
      btn.className = "text-sm rounded-lg px-3 py-1.5 " +
        (curTab === t ? "bg-orange-100 text-orange-700 font-semibold" : "text-gray-500 hover:bg-gray-100");
    });
    const el = document.getElementById("tab-content");
    if (curTab === "info") el.innerHTML = this.infoHtml();
    if (curTab === "qual") el.innerHTML = this.qualHtml();
    if (curTab === "tags") el.innerHTML = this.tagsHtml();
  },

  // ── UC-02 ─────────────────────────────────────────────
  infoHtml() {
    const m = me();
    return `
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 max-w-lg space-y-4">
        <div>
          <label class="text-sm font-semibold text-gray-700">ตำแหน่งทางวิชาการ</label>
          <select id="pf-rank" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mt-1">
            ${["อาจารย์", "ผู้ช่วยศาสตราจารย์", "รองศาสตราจารย์", "ศาสตราจารย์"]
              .map((r) => `<option ${m.rank === r ? "selected" : ""}>${r}</option>`).join("")}
          </select>
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">วันบรรจุ</label>
          <input id="pf-hired" type="date" value="${m.hired}" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mt-1">
        </div>
        <p id="pf-error" class="text-xs text-red-600 hidden">กรอกให้ครบทุกช่องก่อนบันทึก (Alternative Flow UC-02)</p>
        <button onclick="Pages['own-profile'].saveInfo()" class="bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold rounded-xl px-4 py-2">บันทึก</button>
      </div>`;
  },
  saveInfo() {
    const hired = document.getElementById("pf-hired").value;
    const err = document.getElementById("pf-error");
    if (!hired) { err.classList.remove("hidden"); return; }
    err.classList.add("hidden");
    me().rank = document.getElementById("pf-rank").value; me().hired = hired;
    saveData("m3_instructors", instructors); alert("บันทึกข้อมูลวิชาชีพแล้ว");
  },

  // ── UC-03 ─────────────────────────────────────────────
  qualHtml() {
    const rows = me().quals.map((q, i) => `
      <tr class="border-b border-gray-100"><td class="py-2">${q.level}</td><td class="py-2">${q.field}</td>
      <td class="py-2 font-mono">${q.year}</td>
      <td class="py-2 text-right"><button onclick="Pages['own-profile'].delQual(${i})" class="text-red-600 text-xs hover:underline">ลบ</button></td></tr>`)
      .join("") || `<tr><td class="py-4 text-center text-sm text-gray-400" colspan="4">ยังไม่มีคุณวุฒิ — เพิ่มรายการแรกด้านล่าง</td></tr>`;
    return `
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 max-w-lg">
        <table class="w-full text-sm mb-4"><tbody>${rows}</tbody></table>
        <div class="flex gap-2">
          <input id="q-level" placeholder="ระดับ เช่น ป.เอก" class="border border-gray-300 rounded-lg px-2 py-1.5 text-sm w-24">
          <input id="q-field" placeholder="สาขา" class="border border-gray-300 rounded-lg px-2 py-1.5 text-sm flex-1">
          <input id="q-year" placeholder="ปีจบ (ค.ศ.)" type="number" class="border border-gray-300 rounded-lg px-2 py-1.5 text-sm w-24">
          <button onclick="Pages['own-profile'].addQual()" class="bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-lg px-3">เพิ่ม</button>
        </div>
        <p id="q-error" class="text-xs text-red-600 hidden mt-2">ปีที่จบไม่ถูกต้อง — ต้องไม่เป็นปีอนาคต (Alternative Flow UC-03)</p>
      </div>`;
  },
  addQual() {
    const year = Number(document.getElementById("q-year").value);
    const err = document.getElementById("q-error");
    if (!year || year > new Date().getFullYear()) { err.classList.remove("hidden"); return; }
    err.classList.add("hidden");
    me().quals.push({ level: document.getElementById("q-level").value, field: document.getElementById("q-field").value, year });
    saveData("m3_instructors", instructors); this.renderTabs();
  },
  delQual(i) { me().quals.splice(i, 1); saveData("m3_instructors", instructors); this.renderTabs(); },

  // ── UC-04 ─────────────────────────────────────────────
  tagsHtml() {
    return `
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 max-w-lg">
        <p class="text-xs text-gray-500 mb-3">เลือกจาก tag master — ใช้ match กรรมการสอบ/ที่ปรึกษา (M9 เรียกผ่าน GET /instructors?expertise=)</p>
        <div class="flex flex-wrap gap-2">
          ${TAG_MASTER.map((t) => `
            <button onclick="Pages['own-profile'].toggleTag('${t}')"
              class="rounded-full px-3 py-1 text-xs font-semibold border
                ${me().tags.includes(t) ? "bg-orange-100 text-orange-700 border-orange-200" : "bg-white text-gray-500 border-gray-300 hover:bg-gray-50"}">
              ${t}
            </button>`).join("")}
        </div>
      </div>`;
  },
  toggleTag(t) {
    const m = me();
    m.tags = m.tags.includes(t) ? m.tags.filter((x) => x !== t) : [...m.tags, t];
    saveData("m3_instructors", instructors); this.renderTabs();
  },
};
```

---

## `app.js` — router กลาง

```js
function go(stateKey) {
  localStorage.setItem("current_page", stateKey);
  render();
}
function setRole(role) { localStorage.setItem("current_role", role); go(role === "hr" ? "faculty-list" : "own-profile"); }

function render() {
  const role = localStorage.getItem("current_role");
  const stateKey = localStorage.getItem("current_page") || "faculty-list";

  if (!role) {
    document.getElementById("topbar").innerHTML = "";
    document.getElementById("sidebar").innerHTML = "";
    document.getElementById("main").innerHTML = Pages["login"].render();
    return;
  }

  document.getElementById("topbar").innerHTML = Layout.topbar.render();
  document.getElementById("sidebar").innerHTML = Layout.sidebar.render(stateKey, role);
  document.getElementById("main").innerHTML = Pages[stateKey].render();
  Pages[stateKey].afterRender?.();
}

render();
```

---

## หมายเหตุการตรวจกลับ (Traceability)

| จุดในโค้ด | อ้างอิง |
|---|---|
| 4 ไฟล์ใน `pages/` (ไม่รวม login) = 4 state | `m3/state/module_state_diagram.puml` ครบ 1:1 |
| `layout/topbar.js` + `layout/sidebar.js` แยกจาก `pages/*.js` | `mockup_generate_guide.md` §2 |
| `mockM0Accounts` + comment | `fn req/m3` — Account Sync ผ่าน M0 (UC-01) · guide §7 |
| `confirm()` ตอนเกษียณ/พ้นสภาพ ใน `page-adjust-status.js` | Alternative Flow UC-05 ใน usecase_description |
| ตรวจปีจบไม่เป็นอนาคต ใน `page-own-profile.js` | Alternative Flow UC-03 |
| `roles` บนแต่ละ `Pages[...]` + filter ใน `Layout.sidebar` | ตาราง Actors ใน fn req (Faculty จัดการ profile · HR จัดการสถานะ) |
| สี orange ทุก accent + badge เป็น semantic | `UI_django_frontend.md` §2.1 |
