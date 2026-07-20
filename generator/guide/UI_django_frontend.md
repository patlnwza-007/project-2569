# คู่มือการออกแบบและพัฒนา UI Django MVT Frontend (UI Design System & Frontend Guide)

> ใช้ [`UI_django_template.md`](../template/UI_django_template.md) เป็นจุดเริ่มก๊อปปี้ และดู [`UI_django_example.md`](../example/UI_django_example.md) เป็นตัวอย่างที่ทำตามกฎครบทุกข้อ
>
> ไฟล์นี้คือ **design system กลางของทั้งระบบ (Django monolith)** — ทั้งหน้าจริง (Django template + htmx + Alpine.js) และ mockup สาธิต ([`mockup_generate_guide.md`](mockup_generate_guide.md)) ต้องใช้สี/layout/component ชุดเดียวกันนี้ เพื่อให้หน้าตาพ้องกันทั้งระบบ และ screenshot จาก mockup ใช้แทน screenshot ของจริงได้
>
> **สถาปัตยกรรมเป้าหมาย: Django MVT monolith** — ไม่มี SPA แยก, ไม่มี API Gateway, ไม่มี JWT/microservice หน้าจอถูก render จากฝั่ง server (Template) โดยตรง เพิ่ม interactivity ด้วย htmx (โหลดบางส่วน) และ Alpine.js (state เล็ก ๆ ในหน้า) ยืนยันตัวตนด้วย django-allauth ผ่าน Google OAuth 2.0 (session-based)

---

## 0. แหล่งความจริงของหน้าจอ (อ่านก่อนเริ่ม — สำคัญที่สุด)

UI ไม่ได้ออกแบบจากจินตนาการ — ทุกหน้าจอต้อง trace กลับไปยังเอกสารที่มีอยู่แล้วของแอปนั้น:

| เอกสาร | กำหนดอะไรใน UI |
|---|---|
| `<app>/state/module_state_diagram*.puml` | **1 state = 1 หน้าจอ = 1 URL (`path`)** · เส้นในไดอะแกรม = action/ปุ่มนำทาง — ห้ามสร้างหน้าที่ไม่มี state รองรับ และห้ามขาดหน้าที่มี state |
| `<app>/proposal/usecase_description.md` | สิ่งที่หน้าจอต้องทำได้: Basic Flow = ลำดับปุ่ม/ฟอร์มบนหน้า · Alternative Flow = validation/error state ที่ต้อง trigger ได้จริง |
| `fn req/<app>.md` | ตาราง Functional Requirements = ฟังก์ชันที่หน้าต้องรองรับ · ตาราง Actors = role ที่มีสิทธิ์เห็นเมนู/ปุ่ม |
| `architecture/overview_state_diagram.puml` | เมนูใน Dashboard กลาง — 1 Django app = 1 เมนู/การ์ดทางลัด |

**คำว่า "โมดูล" ในเอกสารนี้ = 1 Django app** (เช่น `borrow`, `catalog`, `accounts`) — 1 app มีสีประจำ, ชุด URL, และเมนูของตัวเอง โครงงานเล็กที่มี app เดียวก็ยังใช้กฎนี้ได้ (แค่มีสีเดียว)

---

## 1. Tech Stack

| ส่วน | เครื่องมือ | หมายเหตุ |
|---|---|---|
| Framework | **Django 5 (MVT)** — server-rendered template | ไม่มี SPA แยก · 1 view คืน 1 template |
| Styling | **Tailwind CSS** | dev ใช้ `django-tailwind`/`django-browser-reload` หรือ Tailwind CLI · ห้ามเขียน CSS เองนอกระบบเว้นแต่จำเป็นจริง |
| Interactivity บางส่วน | **htmx** | โหลด/สลับเฉพาะบางส่วนของหน้า (`hx-get`/`hx-post` + `hx-target`) โดยไม่ reload ทั้งหน้า — view คืน template partial |
| Interactivity ในหน้า | **Alpine.js** | state เล็ก ๆ ฝั่ง client (dropdown, modal, tab, toggle) ที่ไม่ต้องยิง server |
| Routing | **Django URLconf** (`urls.py`) | ตั้งชื่อ URL (`name=`) ตามชื่อ state ใน state diagram · นำทางด้วย `{% url 'app:name' %}` |
| Data | **Django ORM** + template context | htmx ใช้สำหรับ partial reload · ไม่มี REST client ฝั่ง browser เว้นแต่จำเป็น |
| Auth | **django-allauth** ผ่าน **Google OAuth 2.0** (session) | ตรวจ Whitelist ก่อนอนุญาตเข้าใช้ · dev ใช้ user ทดสอบ/`createsuperuser` ได้ |
| สิทธิ์ (authorization) | Django auth: `Group`/`Permission` หรือฟิลด์ `role` | บังคับที่ view ด้วย `LoginRequiredMixin`/`UserPassesTestMixin` หรือ decorator |
| Icons | lucide ชุดเดียวทั้งระบบ | ฝัง SVG แบบ static (`{% include %}` partial) หรือ lucide ผ่าน CDN — ห้าม mix ชุด icon |
| Font | Noto Sans Thai (Google Fonts) | UI ใช้ฟอนต์นี้ — TH Sarabun New ใช้เฉพาะเอกสาร/ไดอะแกรม |

> **หลักคิด MVT:** ค่าเริ่มต้นคือ **full-page navigation** (คลิกลิงก์ → โหลดหน้าใหม่จาก server) ใช้ htmx เฉพาะจุดที่การ reload ทั้งหน้าให้ UX แย่ (เช่น อนุมัติทีละแถวในตาราง, ค้นหาแบบ live, เพิ่มของลงตะกร้า) — อย่าเปลี่ยนทั้งระบบให้เป็น SPA เทียมด้วย htmx โดยไม่จำเป็น

---

## 2. Color System

### 2.1 สีประจำโมดูล/แอป (App Color) — กฎที่สำคัญที่สุด

ผู้ใช้ต้องรู้ว่าตัวเองอยู่ส่วนไหนของระบบจาก "สี" โดยไม่ต้องอ่านชื่อ ทุก Django app จึงมีสีประจำที่ล็อกไว้ ห้ามสลับ ตัวอย่างการจับคู่ (ปรับตามแอปจริงของโครงงาน):

| โมดูล/แอป | สี (Tailwind) | ตัวอย่าง class |
|---|---|---|
| บัญชี/โปรไฟล์ (`accounts`) | `blue` | `bg-blue-600`, `bg-blue-100 text-blue-700` |
| แคตตาล็อก/คลังของ (`catalog`) | `violet` | `bg-violet-600`, `bg-violet-100 text-violet-700` |
| ยืม-คืน (`borrow`) | `teal` | `bg-teal-600`, `bg-teal-100 text-teal-700` |
| คิว/จอง (`queue`) | `orange` | `bg-orange-600`, `bg-orange-100 text-orange-700` |
| รายงาน/แดชบอร์ด (`reports`) | `green` | `bg-green-600`, `bg-green-100 text-green-700` |
| งานแอดมิน/จัดการผู้ใช้ (`admin`) | `slate` | `bg-slate-600`, `bg-slate-100 text-slate-700` |

จุดที่ใช้สีแอป: ไอคอนการ์ดทางลัดใน Dashboard · accent ของ header หน้า · primary button ภายในแอป · active state ของเมนู sidebar

**ห้ามเอาสีแอปไปปนกับ semantic color** — เขียว=สำเร็จ/อนุมัติ, amber=รอดำเนินการ/เตือน, แดง=ผิดพลาด/ลบ ใช้ความหมายเดียวกันทุกแอป ดังนั้น badge สถานะในแอปสีเขียว (`reports`) ก็ยังใช้เขียว/เหลือง/แดงตามความหมายของสถานะ ไม่ใช่สีแอป

### 2.2 กฎการใช้สี

- ต่อ 1 หน้า ใช้ไม่เกิน 3 hue: สีแอป + semantic + neutral (gray)
- Contrast ratio ≥ 4.5:1 สำหรับ body text (WCAG AA)
- Hover = สีเดิมเข้มขึ้น 1 ขั้น (`hover:bg-{color}-700`) · Focus = `focus:ring-2 focus:ring-{color}-300` · Disabled = `bg-gray-100 text-gray-400 cursor-not-allowed`
- Surface: การ์ด `bg-white border border-gray-200 shadow-sm` วางบนพื้นหลังหน้า `bg-gray-50`

### 2.3 ปัญหา Tailwind purge — ห้ามประกอบชื่อ class แบบ dynamic

Tailwind สแกนหา class ตอน build ถ้าเขียน `bg-{{ color }}-600` ใน template (ประกอบสตริงเอง) Tailwind จะ **มองไม่เห็นและ purge ทิ้ง** ทำให้สีหาย วิธีที่ถูกต้องคือ map สีเป็น **string เต็ม** ในฝั่ง Python แล้วส่งเข้า context:

```python
# <project>/ui/styles.py — ตารางสีตาม §2.1 (ห้ามสลับสีระหว่างแอป)
APP_STYLES = {
    "accounts": {"icon": "bg-blue-100 text-blue-700",   "btn": "bg-blue-600 hover:bg-blue-700",   "active": "bg-blue-50 text-blue-700",   "ring": "focus:ring-blue-300"},
    "catalog":  {"icon": "bg-violet-100 text-violet-700","btn": "bg-violet-600 hover:bg-violet-700","active": "bg-violet-50 text-violet-700","ring": "focus:ring-violet-300"},
    "borrow":   {"icon": "bg-teal-100 text-teal-700",    "btn": "bg-teal-600 hover:bg-teal-700",    "active": "bg-teal-50 text-teal-700",   "ring": "focus:ring-teal-300"},
    "queue":    {"icon": "bg-orange-100 text-orange-700","btn": "bg-orange-600 hover:bg-orange-700","active": "bg-orange-50 text-orange-700","ring": "focus:ring-orange-300"},
    "reports":  {"icon": "bg-green-100 text-green-700",  "btn": "bg-green-600 hover:bg-green-700",  "active": "bg-green-50 text-green-700", "ring": "focus:ring-green-300"},
    "admin":    {"icon": "bg-slate-100 text-slate-700",  "btn": "bg-slate-600 hover:bg-slate-700",  "active": "bg-slate-100 text-slate-700","ring": "focus:ring-slate-300"},
}
```

> ทางเลือก: ประกาศ `APP_STYLES` ไว้ใน context processor เพื่อให้ทุก template เข้าถึง `app_styles` ได้ หรือ safelist สีทั้งชุดใน `tailwind.config.js` (`safelist: [...]`) ถ้าจำเป็นต้องประกอบ class จริง ๆ — แต่ map เป็น string เต็มเป็นวิธีที่แนะนำ

---

## 3. Typography

| ระดับ | Class | ใช้กับ |
|---|---|---|
| Page title | `text-2xl font-bold` | h1 — ชื่อหน้า |
| Section title | `text-lg font-semibold` | หัวการ์ด/section |
| Label | `text-sm font-semibold` | label ฟอร์ม, หัวคอลัมน์ตาราง |
| Body | `text-sm` | เนื้อหา, cell ตาราง |
| Caption | `text-xs text-gray-500` | คำอธิบาย, วันที่, จำนวนรายการ |

รหัส/ตัวเลขที่ต้อง align กัน (รหัสนักศึกษา, รหัสครุภัณฑ์, เลขที่เอกสาร) ใช้ `font-mono` เสมอ

---

## 4. Layout & Page Anatomy

### 4.1 App Shell = `base.html` (ทุกหน้า extend โครงเดียวกัน)

```
┌────────────────────────────────────────────────────┐
│ Top bar: โลโก้+ชื่อระบบ · ค้นหา · กระดิ่งแจ้งเตือน · โปรไฟล์ │
├──────────┬─────────────────────────────────────────┤
│ Sidebar  │ {% block content %}                      │
│ (w-60)   │ (bg-gray-50, p-6)                        │
└──────────┴─────────────────────────────────────────┘
```

- topbar + sidebar อยู่ใน `templates/base.html` จุดเดียว ทุกหน้า `{% extends "base.html" %}` แล้วเติม `{% block content %}` — แก้ layout ที่เดียวมีผลทุกหน้า (สอดคล้องกับ AppShell แนวคิดเดียวกับ SPA แต่ทำฝั่ง server)
- Sidebar แบ่ง 3 กลุ่มตามลำดับ: **โปรไฟล์** (บัญชีของฉัน) → **โมดูล** (เฉพาะที่ role มีสิทธิ์) → **ผู้ดูแลระบบ** (เห็นเฉพาะ admin: จัดการผู้ใช้งาน, Audit log)
- **ตั้งค่าการแจ้งเตือน / ออกจากระบบ** อยู่ใต้ dropdown ของกระดิ่ง/โปรไฟล์ (Alpine.js toggle) — ไม่ใช่เมนู sidebar เพราะเป็นการตั้งค่าส่วนตัว
- Mobile: sidebar ยุบเป็น hamburger — คุมด้วย Alpine (`x-data="{ open: false }"`) + `hidden lg:block`

### 4.2 Dashboard กลาง (state `Dashboard` ใน overview_state_diagram)

ลำดับบน→ล่าง:
1. คำทักทาย + role badge ของผู้ใช้ (`{{ user.get_full_name }}` / `request.user`)
2. KPI cards 2-4 ใบ (grid, `bg-gray-100/50 rounded-lg`)
3. การ์ดทางลัดเข้าโมดูล — grid 3 คอลัมน์, **1 การ์ด = 1 app = 1 เมนูใน overview diagram** แต่ละใบมีไอคอนพื้นสีแอป + ชื่อ + คำอธิบายสั้น 1 บรรทัด

### 4.3 หน้า list/จัดการข้อมูล (โครงมาตรฐานทุกแอป)

1. **Top ของหน้า** — ชื่อหน้า + จำนวนรายการ + **primary action 1 ปุ่มเดียว** (มุมขวาบน)
2. **Filter bar** — ช่องค้นหา + ตัวกรอง (ค้นหา live ใช้ htmx `hx-get` + `hx-trigger="keyup changed delay:400ms"`)
3. **Content** — ตาราง/การ์ด (render จาก context หรือ partial ที่ htmx swap)
4. **Pagination** — ใต้ content (Django `Paginator` + `?page=`)

---

## 5. Component Patterns (Tailwind class จริง)

เขียน component ซ้ำ ๆ เป็น **template partial** แล้ว `{% include %}` (หรือใช้ `{% ... %}` custom tag / django-components) เพื่อไม่ให้ class กระจายจนแก้ทีเดียวไม่ครบ

### Buttons

```
Primary:   bg-{app}-600 hover:bg-{app}-700 text-white text-sm font-semibold rounded-xl px-4 py-2
Secondary: bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-xl px-4 py-2
Danger:    bg-red-600 hover:bg-red-700 text-white rounded-xl px-4 py-2
Ghost:     text-{app}-600 hover:bg-{app}-50 rounded-lg px-3 py-1.5
```

- ค่าสี `{app}` ดึงจาก `APP_STYLES` (§2.3) ไม่ประกอบสตริงเอง — เช่น `class="{{ app_styles.btn }} text-white ..."`
- Primary บน 1 หน้ามีได้ **1 ปุ่มเท่านั้น** (call-to-action หลักของหน้านั้น)
- Destructive action (ลบ/ยกเลิก/ระงับสิทธิ์) ต้องมี confirmation ก่อนเสมอ — ใช้ Alpine modal หรือ `hx-confirm="ยืนยันการลบ?"` ของ htmx
- ขนาดปุ่ม ≥ 44×44px สำหรับ touch

### Cards

```
bg-white rounded-2xl border border-gray-200 shadow-sm p-4
Interactive card เพิ่ม: hover:shadow-md transition-shadow cursor-pointer
```

### Form Fields

- ใช้ Django form + render เอง (ไม่ใช้ widget default ที่ไม่มี class) — Label อยู่ **บน** input เสมอ ห้ามใช้ placeholder แทน label
- แสดง error จาก `field.errors` (server-side validation) ใต้ field

```html
<label class="text-sm font-semibold text-gray-700" for="{{ form.name.id_for_label }}">ชื่อ-นามสกุล</label>
<input name="{{ form.name.html_name }}" id="{{ form.name.id_for_label }}" value="{{ form.name.value|default:'' }}"
       class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
              focus:outline-none focus:ring-2 {{ app_styles.ring }}
              {% if form.name.errors %}border-red-400 focus:ring-red-200{% endif %}">
{% if form.name.errors %}
  <p class="text-xs text-red-600 mt-1">{{ form.name.errors.0 }}</p>  {# ข้อความบอกวิธีแก้ ไม่ใช่แค่บอกว่าผิด #}
{% endif %}
```

> อย่าลืม `{% csrf_token %}` ในทุก `<form method="post">` และใส่ `hx-headers` CSRF ให้ htmx (ดู template §6)

### Badges (สถานะ)

```
inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold
bg-{semantic}-100 text-{semantic}-700
```

Mapping สถานะจริงของโครงการ → สี (ทำเป็น dict ใน Python หรือ template filter เพื่อไม่ประกอบ class dynamic):

| สถานะ | สี |
|---|---|
| `DRAFT` | gray |
| `PENDING` / `SUBMITTED` / รออนุมัติ | amber |
| `APPROVED` / `ACTIVE` / อนุมัติ / คืนแล้ว | green |
| `REJECTED` / ไม่อนุมัติ / `CANCELLED` | red |
| `PUBLISHED` / เผยแพร่ | สีแอป |

### Tables

- Header: `text-xs uppercase tracking-wider text-gray-500 bg-gray-50`
- Row hover: `hover:bg-gray-50`
- Empty state: icon + ข้อความ + ปุ่ม CTA อยู่กลาง colspan ทั้งหมด (ใช้ `{% empty %}` ใน `{% for %}` loop)

---

## 6. Icon

- lucide ชุดเดียวทั้งระบบ · ขนาด: 16px (inline), 20px (ปุ่ม/เมนู), 24px (การ์ด), 32px+ (empty state)
- ฝังเป็น static SVG partial (`{% include "icons/pencil.svg" %}`) หรือ lucide CDN — ห้าม mix กับชุดอื่น
- ความหมายตายตัว ห้ามสลับ: ดินสอ=แก้ไข · ถังขยะ=ลบ · ตา=ดู · เครื่องหมายบวก=สร้างใหม่ · แว่นขยาย=ค้นหา · เฟือง=ตั้งค่า
- ปุ่มที่มีแต่ icon (icon-only) ต้องมี `title` หรือ `aria-label` เสมอ

---

## 7. UX States (ทุก action ต้องมีครบ)

| State | ต้องแสดง | ทำอย่างไรใน Django/htmx |
|---|---|---|
| Loading | spinner + disable ปุ่ม + ข้อความ "กำลัง..." | htmx `hx-indicator` + class `htmx-request:opacity-50` · ปุ่ม `hx-disabled-elt="this"` |
| Success | toast แจ้งสำเร็จ (หายเองใน 4-5 วินาที) | **Django messages framework** (`messages.success(...)`) render เป็น toast ใน base.html (Alpine auto-dismiss) |
| Error | ข้อความ inline ใต้ field หรือ banner — ต้องบอกวิธีแก้ | `form.errors` (server validation) หรือ `messages.error(...)` |
| Empty | icon + ข้อความ + ปุ่มพาไปสร้างรายการแรก | `{% for %}...{% empty %}...{% endfor %}` |
| Disabled | เทา + `cursor-not-allowed` + tooltip บอกเหตุผล | เช่น ปุ่มยืม disabled พร้อม "กรอกเบอร์โทรก่อนจึงจะยืมได้" |

- Validation หลัก = **server-side** (Django form/model validation) เสมอ — เป็นแหล่งความจริง · client-side (Alpine) เป็นแค่ UX เสริม ห้ามพึ่งอย่างเดียว
- ช่องค้นหา live ใช้ htmx debounce `hx-trigger="keyup changed delay:400ms"`
- **Alternative Flow ทุกข้อใน usecase_description ต้องมี state บนหน้าจอรองรับ** — นี่คือจุดที่กรรมการใช้ตรวจว่าออกแบบครบ

---

## 8. สิทธิ์ตาม Role

- เมนู/ปุ่ม conditional render ตามตาราง **Actors** ใน fn req — role ที่ไม่มีสิทธิ์ต้อง "ไม่เห็น" ไม่ใช่แค่กดไม่ได้ ใช้ `{% if perms.app.change_x %}` หรือเช็ค group/role ใน template
- ตัวอย่าง: เมนู "จัดการผู้ใช้งาน" + "Audit log" เห็นเฉพาะ admin · ปุ่มอนุมัติแสดงเฉพาะ staff
- **Template ซ่อนเพื่อ UX เท่านั้น — การบังคับสิทธิ์จริงอยู่ที่ view** ด้วย `LoginRequiredMixin`, `PermissionRequiredMixin`, `UserPassesTestMixin` หรือ decorator `@login_required`/`@permission_required` เสมอ (ต่างจากสถาปัตยกรรม microservice ที่บังคับที่ Gateway — ที่นี่ view เป็นด่านบังคับสิทธิ์)
- django-allauth คุมเฉพาะ **authentication** (ล็อกอิน Google + Whitelist) ส่วน **authorization** (ทำอะไรได้) เป็นหน้าที่ของ Django permission/group ในแต่ละ view

---

## 9. Accessibility & Responsive

- สีอย่างเดียวห้ามเป็นตัวบอกความหมายเดียว — ต้องมี icon หรือ text กำกับด้วยเสมอ
- ทุก interactive element ต้องมี focus state ที่มองเห็นได้ (ห้าม `outline-none` โดยไม่มี focus style ทดแทน)
- Mobile-first: เขียน base สำหรับ mobile แล้ว override ด้วย `md:` `lg:` · touch target ≥ 44×44px
- ทุก `<img>` มี alt text · htmx partial ที่ swap เข้ามาต้องคง a11y (focus management) ไม่ทำ focus หลุด

---

## 10. Checklist ก่อนส่งงาน

- [ ] ทุก state ใน `module_state_diagram` มี URL/หน้าจอครบ 1:1 (ไม่ขาด ไม่เกิน) — 1 state = 1 `path()` + 1 view + 1 template
- [ ] ทุกหน้า `{% extends "base.html" %}` — topbar/sidebar ไม่ซ้ำในแต่ละไฟล์
- [ ] ใช้สีประจำแอปตามตาราง §2.1 ผ่าน `APP_STYLES` (ไม่ประกอบ class แบบ dynamic) และไม่ปนกับ semantic color
- [ ] Primary button มี 1 ปุ่มต่อหน้า · destructive action มี confirmation (`hx-confirm`/modal)
- [ ] ทุก `<form method="post">` มี `{% csrf_token %}` · htmx ส่ง CSRF header ครบ
- [ ] Validation ทำที่ server (Django form/model) เป็นหลัก · Alternative Flow ทุกข้อมี error/validation state จริงบนหน้าจอ
- [ ] เมนู/ปุ่มแสดงตาม role (ตรงตาราง Actors ใน fn req) และ view บังคับสิทธิ์จริงด้วย mixin/decorator
- [ ] Loading/Empty/Error/Disabled ครบทุกจุดที่มีการดึง/บันทึกข้อมูล (Django messages → toast, `hx-indicator`)
- [ ] Label อยู่บน input ทุกฟอร์ม ไม่มี placeholder แทน label
- [ ] Icon-only button มี title/aria-label ครบ
- [ ] htmx ใช้เฉพาะจุดที่จำเป็น (ตาราง/ค้นหา/ตะกร้า) — ไม่แปลงทั้งระบบเป็น SPA เทียมโดยไม่จำเป็น
