# Template — UI React Frontend

> ⚠️ **เวอร์ชัน React เดิม เก็บเป็น reference** — โครงงาน Django MVT monolith ใช้ [`UI_django_template.md`](UI_django_template.md) แทน
>
> วิธีใช้: ใช้เป็นจุดเริ่มของ frontend แต่ละโมดูล — คัดลอกโครงไปที่ `<module>/frontend/` (หรือ repo frontend รวม) แล้วแทนที่ `{{...}}` ด้วยค่าจริงของโมดูล
> ต้องทำตามกฎใน [`UI_react_frontend.md`](../guide/UI_react_frontend.md) ทุกข้อ โดยเฉพาะ **1 state = 1 route**, **สีประจำโมดูล**, และ **conditional render ตาม role**
> ดูตัวอย่างที่กรอกครบแล้วได้ที่ [`UI_react_example.md`](../example/UI_react_example.md)

---

## 1. ตาราง Mapping — กรอกให้ครบก่อนเขียนโค้ด (กัน state ตกหล่น)

ดึง state จาก `{{module}}/state/module_state_diagram*.puml` มาใส่ทีละแถว — **1 state = 1 แถว = 1 route = 1 page component**:

| State (หน้าจอ) | Route | Component | UC ที่รองรับ | Endpoint ที่เรียก | Role ที่เห็น | สถานะ |
|---|---|---|---|---|---|:---:|
| {{FacultyList}} | {{/m3/instructors}} | {{FacultyListPage}} | {{UC-01, UC-05}} | {{GET /instructors}} | {{HR/Admin}} | ☐ |
| {{...}} | | | | | | ☐ |

> โมดูลที่มีหลายแอป (M4 มี 4, M8 มี 3, M9 มี 2) ให้ทำตารางแยกต่อแอป และแยก route prefix เช่น `/m4/applicant/...`, `/m4/registrar/...`

---

## 2. โครงสร้างโฟลเดอร์

```
frontend/
├── index.html
├── package.json          react, react-dom, react-router-dom, lucide-react, tailwindcss
├── tailwind.config.js
└── src/
    ├── main.jsx           ← router: 1 state = 1 <Route>
    ├── app/
    │   ├── AppShell.jsx   ← top bar + sidebar ใช้ร่วมทุกหน้า (§4.1 ใน guide)
    │   └── moduleColors.js
    ├── modules/{{module}}/
    │   ├── pages/{{PageName}}.jsx   ← 1 ไฟล์ต่อ 1 state
    │   └── api.js                   ← endpoint ของโมดูลนี้ (comment อ้าง fn req)
    ├── components/ui/     ← Button, Card, Badge, EmptyState (ใช้ร่วมทุกโมดูล)
    └── lib/
        ├── api.js         ← fetch helper + แนบ JWT
        └── auth.js        ← อ่าน role จาก token (dev: mock ได้)
```

---

## 3. สีประจำโมดูล (`src/app/moduleColors.js`)

Tailwind สแกน class ตอน build — **ห้ามประกอบชื่อ class แบบ dynamic** (`bg-${color}-600` จะไม่ถูก build) ต้อง map เป็น string เต็มเท่านั้น:

```js
// ตารางสีตาม UI_react_frontend.md §2.1 — ห้ามสลับสีระหว่างโมดูล
export const MODULE_STYLES = {
  m0:    { icon: "bg-blue-100 text-blue-700",     btn: "bg-blue-600 hover:bg-blue-700",     active: "bg-blue-50 text-blue-700" },
  m1c:   { icon: "bg-violet-100 text-violet-700", btn: "bg-violet-600 hover:bg-violet-700", active: "bg-violet-50 text-violet-700" },
  m1p:   { icon: "bg-teal-100 text-teal-700",     btn: "bg-teal-600 hover:bg-teal-700",     active: "bg-teal-50 text-teal-700" },
  m3:    { icon: "bg-orange-100 text-orange-700", btn: "bg-orange-600 hover:bg-orange-700", active: "bg-orange-50 text-orange-700" },
  m4:    { icon: "bg-green-100 text-green-700",   btn: "bg-green-600 hover:bg-green-700",   active: "bg-green-50 text-green-700" },
  m8:    { icon: "bg-amber-100 text-amber-700",   btn: "bg-amber-600 hover:bg-amber-700",   active: "bg-amber-50 text-amber-700" },
  m9:    { icon: "bg-pink-100 text-pink-700",     btn: "bg-pink-600 hover:bg-pink-700",     active: "bg-pink-50 text-pink-700" },
  admin: { icon: "bg-slate-100 text-slate-700",   btn: "bg-slate-600 hover:bg-slate-700",   active: "bg-slate-100 text-slate-700" },
};
```

---

## 4. AppShell (top bar + sidebar)

```jsx
// src/app/AppShell.jsx
import { NavLink, Outlet } from "react-router-dom";
import { Bell, Search } from "lucide-react";
import { useAuth } from "../lib/auth";

// เมนู sidebar 3 กลุ่มตาม guide §4.1 — items กรองตาม role เสมอ
const MENU = [
  { group: "โปรไฟล์", items: [
    { to: "/account", label: "บัญชีของฉัน", icon: {{UserCircle}}, style: "m0" },
  ]},
  { group: "โมดูล", items: [
    { to: "{{/m1/curriculum}}", label: "{{หลักสูตร}}", icon: {{BookOpen}}, style: "{{m1c}}", roles: ["{{curriculum_officer}}", "{{program_chair}}"] },
    // ... เพิ่ม 1 แถวต่อ 1 app ตาม overview_state_diagram
  ]},
  { group: "ผู้ดูแลระบบ", roles: ["admin"], items: [
    { to: "/admin/accounts", label: "จัดการผู้ใช้งาน", icon: {{Settings}}, style: "admin" },
    { to: "/admin/audit", label: "Audit log", icon: {{ClipboardList}}, style: "admin" },
  ]},
];

export default function AppShell() {
  const { user, roles } = useAuth();
  const canSee = (item) => !item.roles || item.roles.some((r) => roles.includes(r));

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 py-2.5 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm">ERP บริหารหลักสูตร</span>
        </div>
        <div className="flex items-center gap-4">
          <Search size={18} className="text-gray-500" />
          {/* กระดิ่ง: dropdown มี "ตั้งค่าการแจ้งเตือน" (M10 UC-11) — ไม่ใช่เมนู sidebar */}
          <Bell size={18} className="text-gray-500" />
          <span className="text-sm">{user.name}</span>
        </div>
      </header>
      <div className="flex">
        <nav className="w-60 bg-white border-r border-gray-200 p-3 hidden lg:block">
          {MENU.filter(canSee).map((g) => (
            <div key={g.group} className="mb-3">
              <p className="px-2 py-1 text-[11px] uppercase tracking-wide text-gray-400">{g.group}</p>
              {g.items.filter(canSee).map((it) => (
                <NavLink key={it.to} to={it.to}
                  className={({ isActive }) =>
                    `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm ` +
                    (isActive ? "{{MODULE_STYLES ของ item นั้น}}.active font-semibold" : "text-gray-600 hover:bg-gray-50")
                  }>
                  <it.icon size={18} /> {it.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <main className="flex-1 p-6"><Outlet /></main>
      </div>
    </div>
  );
}
```

---

## 5. Page skeleton — หน้า list ตาม anatomy (guide §4.3)

```jsx
// src/modules/{{module}}/pages/{{Entity}}ListPage.jsx
import { useState, useEffect } from "react";
import { Plus, Search } from "lucide-react";
import { MODULE_STYLES } from "../../../app/moduleColors";
import { fetch{{Entities}} } from "../api";

const S = MODULE_STYLES["{{module_key}}"];

export default function {{Entity}}ListPage() {
  const [rows, setRows] = useState(null);   // null = loading
  const [q, setQ] = useState("");

  useEffect(() => { fetch{{Entities}}().then(setRows); }, []);

  const filtered = (rows ?? []).filter((r) => r.{{name_field}}.includes(q));

  return (
    <div>
      {/* 1. Top: ชื่อหน้า + จำนวน + primary action 1 ปุ่มเดียว */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">{{ชื่อหน้า}}</h1>
          <p className="text-xs text-gray-500">{filtered.length} รายการ</p>
        </div>
        <button className={`${S.btn} text-white text-sm font-semibold rounded-xl px-4 py-2 flex items-center gap-1.5`}>
          <Plus size={16} /> {{เพิ่ม...}}
        </button>
      </div>

      {/* 2. Filter bar */}
      <div className="flex items-center gap-2 mb-4">
        <div className="relative flex-1 max-w-xs">
          <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="{{ค้นหา...}}"
            className="w-full border border-gray-300 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-{{module_color}}-300" />
        </div>
      </div>

      {/* 3. Content: loading / empty / ตาราง — ครบ 3 state ตาม guide §7 */}
      {rows === null ? (
        <p className="text-sm text-gray-400 py-10 text-center">กำลังโหลด...</p>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-2xl border border-gray-200">
          <p className="text-sm text-gray-500 mb-3">{{ยังไม่มีข้อมูล}}</p>
          <button className={`${S.btn} text-white text-sm rounded-xl px-4 py-2`}>{{สร้างรายการแรก}}</button>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-xs uppercase tracking-wider text-gray-500">
              <tr><th className="text-left px-4 py-3">{{คอลัมน์}}</th></tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3">{r.{{name_field}}}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {/* 4. Pagination ใต้ตาราง (เพิ่มเมื่อข้อมูลเกิน 1 หน้า) */}
    </div>
  );
}
```

---

## 6. API helper (`src/lib/api.js`)

```js
// แนบ JWT ทุก request — token มาจาก Keycloak (ผ่าน Traefik) · dev mode ใช้ mock token ได้
const BASE = import.meta.env.VITE_API_BASE ?? "/api";

export async function api(path, options = {}) {
  const token = localStorage.getItem("access_token"); // จริง: จาก keycloak-js
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}
```

```js
// src/modules/{{module}}/api.js — 1 ฟังก์ชันต่อ endpoint, comment อ้าง fn req เสมอ
import { api } from "../../lib/api";

// fn req/{{module}}.md — {{GET /instructors?expertise=&available=}}
export const fetch{{Entities}} = (params) => api(`{{/instructors}}?${new URLSearchParams(params)}`);
```

---

## 7. Checklist ย่อก่อน commit

- [ ] ตาราง §1 กรอกครบทุก state และติ๊ก ☐ → ✅ ครบ
- [ ] ทุกหน้าใช้ `MODULE_STYLES` ไม่ hardcode สี / ไม่ประกอบ class แบบ dynamic
- [ ] loading / empty / error ครบทุกหน้า list
- [ ] เมนูและปุ่มกรองตาม role แล้ว

ฉบับเต็มดู [`UI_react_frontend.md`](../guide/UI_react_frontend.md) §10
