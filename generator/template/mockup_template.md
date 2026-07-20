# Template — Standalone Mockup (แยก panel + แยกไฟล์ตามหน้าใน state diagram)

> วิธีใช้: คัดลอกโครงไฟล์ด้านล่างไปที่ `<module>/mockup/` แล้วแทนที่ `{{...}}` ด้วยค่าจริงของโมดูล
> ต้องทำตามกฎใน [`mockup_generate_guide.md`](../guide/mockup_generate_guide.md) ทุกข้อ โดยเฉพาะ **§2 แยก panel (topbar/sidebar/body) + แยก 1 ไฟล์ต่อ 1 state** และหน้าตาต้องตรงกับ design system กลางใน [`UI_django_frontend.md`](../guide/UI_django_frontend.md) — โดยเฉพาะ**สีประจำแอป** (§2.1)
> ดูตัวอย่างที่กรอกครบแล้วได้ที่ [`mockup_example.md`](../example/mockup_example.md)

---

## 1. ตาราง Mapping — กรอกก่อนเริ่ม (กันหน้าจอตกหล่น)

| State (จาก module_state_diagram) | ไฟล์ | UC ที่รองรับ | Role ที่เห็น | สถานะ |
|---|---|---|---|:---:|
| {{FacultyList}} | `pages/page-{{faculty-list}}.js` | {{UC-01, UC-05}} | {{hr}} | ☐ |
| {{...}} | | | | ☐ |

---

## 2. โครงไฟล์

```
<module>/mockup/
├── index.html
├── app.js
├── mock-data.js
├── style.css              (ถ้ามีสไตล์นอกเหนือ Tailwind)
├── layout/
│   ├── topbar.js
│   └── sidebar.js
└── pages/
    ├── page-login.js       ← หน้าเลือก role (ดู guide §5)
    ├── page-{{state-1}}.js
    ├── page-{{state-2}}.js
    └── ...
```

### 2.1 `index.html` — shell เปล่า โหลดทุกไฟล์ด้วย `<script src>` ธรรมดา

```html
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{M_CODE}} · {{MODULE_NAME_TH}} — Mockup</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style> body { font-family: 'Noto Sans Thai', sans-serif; } </style>
</head>
<body class="bg-gray-50 text-gray-800">

  <div id="topbar"></div>
  <div class="flex min-h-screen">
    <nav id="sidebar" class="w-56 bg-white border-r border-gray-200 p-3 shrink-0"></nav>
    <main id="main" class="flex-1 p-6"></main>
  </div>
  <footer class="text-center py-3">
    <button onclick="resetData()" class="text-xs text-gray-400 hover:text-red-600 underline">รีเซ็ตข้อมูลตัวอย่าง</button>
  </footer>

  <!-- ข้อมูล -->
  <script src="mock-data.js"></script>
  <!-- panel ที่ใช้ร่วมทุกหน้า -->
  <script src="layout/topbar.js"></script>
  <script src="layout/sidebar.js"></script>
  <!-- 1 บรรทัดต่อ 1 state — เพิ่มตามตาราง mapping §1 -->
  <script src="pages/page-login.js"></script>
  <script src="pages/page-{{state-1}}.js"></script>
  <script src="pages/page-{{state-2}}.js"></script>
  <!-- router สุดท้ายเสมอ -->
  <script src="app.js"></script>
</body>
</html>
```

### 2.2 `mock-data.js` — ข้อมูลตัวอย่าง + localStorage helper (ตาม guide §3)

```js
// ดึง entity จาก fn req หัวข้อ "6. Data Entities"
const seed{{Entity}} = [
  { id: 1, {{field}}: "{{ค่าตัวอย่าง}}", status: "{{ACTIVE}}" },
];
// ระบบจริง: GET /{{endpoint}} (M{{X}} UC-{{XX}}) — mock ไว้ก่อนเพราะไม่มี network จริง
const mockM0Accounts = [{ id: "acc-101", name: "{{ชื่อ}}", email: "{{email}}" }];

function loadData(key, fallback) {
  const saved = localStorage.getItem(key);
  return saved ? JSON.parse(saved) : fallback;
}
function saveData(key, data) { localStorage.setItem(key, JSON.stringify(data)); }
function resetData() { localStorage.clear(); location.reload(); }

let {{entities}} = loadData("{{m_code}}_{{entities}}", seed{{Entity}});
```

### 2.3 `layout/topbar.js` — panel บนสุด ใช้ร่วมทุกหน้า

```js
const Layout = window.Layout || (window.Layout = {});
Layout.topbar = {
  render() {
    return `
      <header class="bg-white border-b border-gray-200 px-4 py-2.5 flex items-center justify-between sticky top-0 z-10">
        <div class="flex items-center gap-2">
          <span class="w-7 h-7 rounded-lg bg-{{module_color}}-100 text-{{module_color}}-700
                       flex items-center justify-center font-bold text-xs">{{M_CODE}}</span>
          <span class="font-semibold text-sm">ERP บริหารหลักสูตร · {{MODULE_NAME_TH}}</span>
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500">บทบาท (จำลอง):</label>
          <select onchange="setRole(this.value)" class="border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="{{role_1}}">{{ชื่อ role 1}}</option>
            <option value="{{role_2}}">{{ชื่อ role 2}}</option>
          </select>
        </div>
      </header>`;
  },
};
```

### 2.4 `layout/sidebar.js` — panel เมนูซ้าย กรองตาม role

```js
const Layout = window.Layout || (window.Layout = {});
// 1 รายการต่อ 1 state ที่เป็น entry จากเมนู — roles ต้องตรงกับที่ประกาศใน pages/*.js
const MENU = [
  { key: "{{state-1}}", label: "{{ชื่อเมนู 1}}", roles: ["{{role_1}}"] },
  { key: "{{state-2}}", label: "{{ชื่อเมนู 2}}", roles: ["{{role_2}}"] },
];
Layout.sidebar = {
  render(activeKey, role) {
    return MENU.filter((m) => m.roles.includes(role)).map((m) => `
      <button onclick="go('${m.key}')"
        class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-left
          ${activeKey === m.key ? "bg-{{module_color}}-50 text-{{module_color}}-700 font-semibold" : "text-gray-600 hover:bg-gray-50"}">
        ${m.label}
      </button>`).join("");
  },
};
```

### 2.5 `pages/page-{{state}}.js` — 1 ไฟล์ต่อ 1 state

```js
const Pages = window.Pages || (window.Pages = {});
Pages["{{state-key}}"] = {
  roles: ["{{role_1}}"],
  render() {
    return `
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-2xl font-bold">{{ชื่อหน้า}}</h1>
        <button onclick="go('{{other-state}}')"
          class="bg-{{module_color}}-600 hover:bg-{{module_color}}-700 text-white text-sm font-semibold rounded-xl px-4 py-2">
          {{ปุ่ม action หลัก}}
        </button>
      </div>
      <div id="content-{{state-key}}"></div>`;
  },
  afterRender() {
    // ดึงข้อมูลจาก mock-data มา render ตาราง/ฟอร์ม + bind event ที่ innerHTML ทำไม่ได้ตรง ๆ
  },
};
```

### 2.6 `pages/page-login.js` — หน้าเลือก role (ดู guide §5)

```js
const Pages = window.Pages || (window.Pages = {});
Pages["login"] = {
  render() {
    return `
      <div class="min-h-screen flex items-center justify-center">
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 max-w-sm w-full">
          <h2 class="text-lg font-semibold mb-4">เลือกบทบาทเพื่อทดลองใช้งาน</h2>
          <div class="space-y-2">
            <button onclick="loginAs('{{role_1}}')" class="w-full bg-{{module_color}}-600 hover:bg-{{module_color}}-700 text-white text-sm rounded-xl px-4 py-2">{{ชื่อ role 1}}</button>
            <button onclick="loginAs('{{role_2}}')" class="w-full bg-white border border-gray-300 hover:bg-gray-50 text-sm rounded-xl px-4 py-2">{{ชื่อ role 2}}</button>
          </div>
        </div>
      </div>`;
  },
};
function loginAs(role) {
  localStorage.setItem("current_role", role);
  go("{{หน้าแรกของ role นั้น}}");
}
```

### 2.7 `app.js` — router กลาง (โหลดหลังสุดใน `index.html`)

```js
function go(stateKey) {
  localStorage.setItem("current_page", stateKey);
  render();
}
function setRole(role) { localStorage.setItem("current_role", role); render(); }

function render() {
  const role = localStorage.getItem("current_role");
  const stateKey = localStorage.getItem("current_page") || Object.keys(Pages)[0];

  if (!role) {
    document.getElementById("topbar").innerHTML = "";
    document.getElementById("sidebar").innerHTML = "";
    document.getElementById("main").innerHTML = Pages["login"].render();
    return;
  }

  document.getElementById("topbar").innerHTML = Layout.topbar.render();
  Layout.topbar.afterRender?.();
  document.getElementById("sidebar").innerHTML = Layout.sidebar.render(stateKey, role);
  document.getElementById("main").innerHTML = Pages[stateKey].render();
  Pages[stateKey].afterRender?.();
}

render();
```

---

## 3. Checklist ย่อ (ฉบับเต็มดู guide §9)

- [ ] ตาราง §1 ครบทุก state และติ๊กครบ
- [ ] แยกไฟล์ตรงตามโครง §2 — `layout/topbar.js`, `layout/sidebar.js`, และ 1 ไฟล์ต่อ 1 state ใน `pages/`
- [ ] สีประจำแอปถูกต้องตาม `UI_django_frontend.md` §2.1 (แทนที่ `{{app_color}}` ให้ครบทุกไฟล์ ไม่ใช่แค่บางไฟล์)
- [ ] Role switcher ทำงาน — สลับแล้วเมนู/ปุ่มเปลี่ยนตามสิทธิ์จริง
- [ ] กรอกข้อมูล → เปลี่ยนหน้า → กลับมา ข้อมูลยังอยู่ (localStorage)
- [ ] มีปุ่มรีเซ็ตข้อมูลตัวอย่าง
- [ ] เปิด `index.html` ผ่าน `file://` ตรง ๆ ได้โดยไม่ error (ไม่มี fetch/import ข้ามไฟล์)
- [ ] จุดที่เรียกข้าม service มี comment ระบุ endpoint จริง
