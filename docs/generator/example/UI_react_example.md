# ตัวอย่าง — UI React ที่ทำตามกฎครบทุกข้อ (Dashboard กลางของระบบ)

> ⚠️ **เวอร์ชัน React เดิม เก็บเป็น reference** — โครงงาน Django MVT monolith ดูตัวอย่างที่ [`UI_django_example.md`](UI_django_example.md) แทน


> ตัวอย่างนี้คือ **หน้า Dashboard หลัง login** — state `Dashboard` ใน [`architecture/overview_state_diagram.puml`](../../architecture/overview_state_diagram.puml) ซึ่งเป็นจุดแตกแขนงไปทุก app ของระบบ — เขียนตามกฎใน [`UI_react_frontend.md`](../guide/UI_react_frontend.md) ครบทุกข้อ ใช้เป็นตัวอย่างอ้างอิงตอนสร้างหน้าอื่นต่อ

จุดที่ตัวอย่างนี้สาธิตให้เห็น:
- **App shell** — top bar + sidebar 3 กลุ่ม (โปรไฟล์ / โมดูล / ผู้ดูแลระบบ) ตาม guide §4.1
- **สีประจำโมดูล** ผ่าน `MODULE_STYLES` map — ไม่ประกอบ class แบบ dynamic (guide §2.1)
- **1 การ์ดทางลัด = 1 app** ตรงกับเมนูใน overview_state_diagram (guide §4.2)
- **Conditional render ตาม role** — กลุ่มเมนูผู้ดูแลระบบและการ์ด Audit log เห็นเฉพาะ admin (guide §8)
- **Loading state** ของ KPI cards (guide §7)
- ตั้งค่าการแจ้งเตือนอยู่ใน dropdown กระดิ่ง ไม่ใช่ sidebar (guide §4.1)

---

## ตาราง Mapping (ตาม template §1)

| State (หน้าจอ) | Route | Component | อ้างอิง | Role ที่เห็น |
|---|---|---|---|---|
| Dashboard | `/` | `DashboardPage` | overview_state_diagram | ทุก role (การ์ดกรองตามสิทธิ์) |

---

## โค้ด

```jsx
// src/app/moduleColors.js — ตารางสีล็อกตาม guide §2.1
export const MODULE_STYLES = {
  m0:    { icon: "bg-blue-100 text-blue-700",     active: "bg-blue-50 text-blue-700" },
  m1c:   { icon: "bg-violet-100 text-violet-700", active: "bg-violet-50 text-violet-700" },
  m1p:   { icon: "bg-teal-100 text-teal-700",     active: "bg-teal-50 text-teal-700" },
  m3:    { icon: "bg-orange-100 text-orange-700", active: "bg-orange-50 text-orange-700" },
  m4:    { icon: "bg-green-100 text-green-700",   active: "bg-green-50 text-green-700" },
  m8:    { icon: "bg-amber-100 text-amber-700",   active: "bg-amber-50 text-amber-700" },
  m9:    { icon: "bg-pink-100 text-pink-700",     active: "bg-pink-50 text-pink-700" },
  admin: { icon: "bg-slate-100 text-slate-700",   active: "bg-slate-100 text-slate-700" },
};
```

```jsx
// src/modules/dashboard/DashboardPage.jsx
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  UserCircle, BookOpen, CalendarClock, Users, UserPlus,
  Briefcase, NotebookPen, Settings, ClipboardList,
} from "lucide-react";
import { MODULE_STYLES } from "../../app/moduleColors";
import { useAuth } from "../../lib/auth";
import { api } from "../../lib/api";

// 1 การ์ด = 1 app = 1 เมนูใน overview_state_diagram — ห้ามเพิ่มการ์ดที่ไม่มี app รองรับ
const APPS = [
  { to: "/account",        label: "บัญชีของฉัน",        desc: "โปรไฟล์และรูปประจำตัว",  icon: UserCircle,    style: "m0" },
  { to: "/curriculum",     label: "หลักสูตร",            desc: "PLO / CLO / มคอ.",       icon: BookOpen,      style: "m1c",  roles: ["curriculum_officer", "program_chair", "faculty"] },
  { to: "/planning",       label: "จัดตารางเรียน",       desc: "Section / ห้อง / เผยแพร่", icon: CalendarClock, style: "m1p",  roles: ["scheduler", "program_chair"] },
  { to: "/faculty",        label: "ข้อมูลอาจารย์",       desc: "Profile วิชาชีพ",         icon: Users,         style: "m3",   roles: ["faculty", "hr"] },
  { to: "/admission",      label: "รับสมัคร/นักศึกษา",   desc: "ใบสมัคร / สัมภาษณ์",     icon: UserPlus,      style: "m4",   roles: ["registrar", "interviewer"] },
  { to: "/coop",           label: "สหกิจศึกษา",          desc: "ฝึกงาน / ประเมินผล",     icon: Briefcase,     style: "m8",   roles: ["student", "faculty", "company"] },
  { to: "/thesis",         label: "โครงงาน/วิทยานิพนธ์", desc: "เสนอหัวข้อ / สอบ",        icon: NotebookPen,   style: "m9",   roles: ["student", "faculty", "program_chair"] },
  { to: "/admin/accounts", label: "จัดการผู้ใช้งาน",     desc: "บัญชี / role / สิทธิ์",   icon: Settings,      style: "admin", roles: ["admin"] },
  { to: "/admin/audit",    label: "Audit log",           desc: "เฉพาะผู้ดูแลระบบ",       icon: ClipboardList, style: "admin", roles: ["admin"] },
];

export default function DashboardPage() {
  const { user, roles } = useAuth();
  const [kpi, setKpi] = useState(null); // null = loading (guide §7)

  useEffect(() => {
    // fn req/m7_reports_analytics.md — GET /dashboards/overview
    // (M7 dev in next version — ตอนนี้ mock ฝั่ง client ไปก่อน)
    api("/dashboards/overview").then(setKpi).catch(() => setKpi({}));
  }, []);

  const visibleApps = APPS.filter(
    (a) => !a.roles || a.roles.some((r) => roles.includes(r))
  );

  return (
    <div>
      {/* คำทักทาย + role badge — guide §4.2 ข้อ 1 */}
      <div className="mb-1 flex items-center gap-2">
        <h1 className="text-2xl font-bold">สวัสดี, {user.name}</h1>
        <span className="inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold bg-blue-100 text-blue-700">
          {roles[0]}
        </span>
      </div>
      <p className="text-xs text-gray-500 mb-5">
        ภาคเรียนที่ 1/2569 — เลือกโมดูลที่ต้องการเข้าใช้งาน
      </p>

      {/* KPI cards — guide §4.2 ข้อ 2 · มี loading state ครบ */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        <KpiCard label="นักศึกษาทั้งหมด" value={kpi?.students} />
        <KpiCard label="กลุ่มเรียนเปิดสอน" value={kpi?.sections} />
        <KpiCard label="แจ้งเตือนใหม่" value={kpi?.alerts} danger />
      </div>

      {/* การ์ดทางลัด — 1 ใบ = 1 app · กรองตาม role — guide §4.2 ข้อ 3 + §8 */}
      <p className="text-xs text-gray-500 mb-2">ทางลัดเข้าโมดูล</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {visibleApps.map((a) => {
          const s = MODULE_STYLES[a.style];
          return (
            <Link key={a.to} to={a.to}
              className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4
                         hover:shadow-md transition-shadow">
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-2 ${s.icon}`}>
                <a.icon size={20} />
              </div>
              <p className="text-sm font-semibold">{a.label}</p>
              <p className="text-xs text-gray-500 mt-0.5">{a.desc}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function KpiCard({ label, value, danger = false }) {
  return (
    <div className="bg-gray-100/60 rounded-xl px-4 py-3">
      <p className="text-xs text-gray-500">{label}</p>
      {value === undefined ? (
        <p className="text-xl font-semibold text-gray-300 animate-pulse">—</p>
      ) : (
        <p className={`text-xl font-semibold ${danger && value > 0 ? "text-red-600" : ""}`}>
          {Number(value ?? 0).toLocaleString()}
        </p>
      )}
    </div>
  );
}
```

```jsx
// src/main.jsx — 1 state ใน state diagram = 1 <Route>
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppShell from "./app/AppShell";
import DashboardPage from "./modules/dashboard/DashboardPage";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        {/* เพิ่ม route ของแต่ละโมดูลตามตาราง mapping ใน UI_react_template.md §1 */}
      </Route>
    </Routes>
  </BrowserRouter>
);
```

---

## หมายเหตุการตรวจกลับ (Traceability)

| จุดในโค้ด | อ้างอิงกฎ/เอกสาร |
|---|---|
| `APPS` 9 ใบ | ตรง 1:1 กับเมนูใน `overview_state_diagram.puml` |
| `MODULE_STYLES` | ตารางสี guide §2.1 |
| `roles` filter | ตาราง Actors ใน fn req ของแต่ละโมดูล (guide §8) |
| KPI loading `—` + `animate-pulse` | guide §7 (loading state) |
| การ์ด `hover:shadow-md` | guide §5 (interactive card) |
