# คู่มือการออกแบบและพัฒนา UI React Frontend (UI Design System & Frontend Guide)

> ⚠️ **ไฟล์นี้เป็นเวอร์ชัน React/microservice เดิม เก็บไว้เป็น reference เท่านั้น** — โครงงานที่ใช้ **Django MVT monolith** (htmx/Alpine/Tailwind, PostgreSQL, allauth) ให้ใช้ [`UI_django_frontend.md`](UI_django_frontend.md) + [`UI_django_template.md`](../template/UI_django_template.md) + [`UI_django_example.md`](../example/UI_django_example.md) แทน ซึ่งเป็น design system กลางที่ mockup และ slide อ้างอิง
>
> ใช้ [`UI_react_template.md`](../template/UI_react_template.md) เป็นจุดเริ่มก๊อปปี้ และดู [`UI_react_example.md`](../example/UI_react_example.md) เป็นตัวอย่างที่ทำตามกฎครบทุกข้อ
>
> ไฟล์นี้คือ **design system กลางของทั้งระบบ ERP บริหารหลักสูตร** — ทั้ง frontend จริง (React) และ mockup สาธิต ([`mockup_generate_guide.md`](mockup_generate_guide.md)) ต้องใช้สี/layout/component ชุดเดียวกันนี้ เพื่อให้หน้าตาพ้องกันทั้งระบบ และ screenshot จาก mockup ใช้แทน screenshot ของจริงได้

---

## 0. แหล่งความจริงของหน้าจอ (อ่านก่อนเริ่ม — สำคัญที่สุด)

UI ไม่ได้ออกแบบจากจินตนาการ — ทุกหน้าจอต้อง trace กลับไปยังเอกสารที่มีอยู่แล้วของโมดูลนั้น:

| เอกสาร | กำหนดอะไรใน UI |
|---|---|
| `<module>/state/module_state_diagram*.puml` | **1 state = 1 หน้าจอ = 1 route** · เส้นในไดอะแกรม = action/ปุ่มนำทาง — ห้ามสร้างหน้าที่ไม่มี state รองรับ และห้ามขาดหน้าที่มี state |
| `<module>/proposal/usecase_description.md` | สิ่งที่หน้าจอต้องทำได้: Basic Flow = ลำดับปุ่ม/ฟอร์มบนหน้า · Alternative Flow = validation/error state ที่ต้อง trigger ได้จริง |
| `fn req/<module>.md` | ตาราง API Endpoints = endpoint ที่หน้าเรียก · ตาราง Actors = role ที่มีสิทธิ์เห็นเมนู/ปุ่ม |
| `architecture/overview_state_diagram.puml` | เมนูใน Dashboard กลาง — 1 app = 1 เมนู/การ์ดทางลัด |

โมดูลที่แยกหลายแอปใน state diagram ให้แยกกลุ่ม route ตามนั้น: M0 (Account Center + Admin Console), M1 (Curriculum + Planning), M4 (Applicant / Online Interview / Onsite Interview / Registrar Back-office), M8 (Student / Teacher / Company Portal), M9 (Student / Staff-Committee)

---

## 1. Tech Stack

| ส่วน | เครื่องมือ | หมายเหตุ |
|---|---|---|
| Framework | React 18 + Vite (SPA) | ตาม tech stack กลางของโครงการ (`summary.md`) |
| Styling | Tailwind CSS | ห้ามเขียน CSS เองนอกระบบ เว้นแต่จำเป็นจริง |
| Routing | react-router-dom | path ตั้งตามชื่อ state ใน state diagram |
| Data | fetch/axios (+ React Query แนะนำ) | แนบ JWT อัตโนมัติผ่าน interceptor |
| Auth | Keycloak ผ่าน Traefik (JWT) | dev mode ใช้ mock role switcher ได้ |
| Icons | lucide ชุดเดียวทั้งระบบ | React ใช้แพ็กเกจ `lucide-react` · mockup ใช้ CDN ของ lucide — ห้าม mix ชุด icon |
| Font | Noto Sans Thai (Google Fonts) | UI ใช้ฟอนต์นี้ — TH Sarabun New ใช้เฉพาะเอกสาร/ไดอะแกรม |

---

## 2. Color System

### 2.1 สีประจำโมดูล (Module Color) — กฎที่สำคัญที่สุด

ผู้ใช้ต้องรู้ว่าตัวเองอยู่โมดูลไหนจาก "สี" โดยไม่ต้องอ่านชื่อ ทุกโมดูลจึงมีสีประจำที่ล็อกไว้ ห้ามสลับ:

| โมดูล/แอป | สี (Tailwind) | ตัวอย่าง class |
|---|---|---|
| M0 · บัญชี/โปรไฟล์ | `blue` | `bg-blue-600`, `bg-blue-100 text-blue-700` |
| M1 · หลักสูตร (Curriculum) | `violet` | `bg-violet-600`, `bg-violet-100 text-violet-700` |
| M1 · จัดตารางเรียน (Planning) | `teal` | `bg-teal-600`, `bg-teal-100 text-teal-700` |
| M3 · ข้อมูลอาจารย์ | `orange` | `bg-orange-600`, `bg-orange-100 text-orange-700` |
| M4 · รับสมัคร/นักศึกษา | `green` | `bg-green-600`, `bg-green-100 text-green-700` |
| M8 · สหกิจศึกษา | `amber` | `bg-amber-600`, `bg-amber-100 text-amber-700` |
| M9 · โครงงาน/วิทยานิพนธ์ | `pink` | `bg-pink-600`, `bg-pink-100 text-pink-700` |
| งานแอดมิน (M0 Admin Console, M10 Audit Log) | `slate` | `bg-slate-600`, `bg-slate-100 text-slate-700` |

จุดที่ใช้สีโมดูล: ไอคอนการ์ดทางลัดใน Dashboard · accent ของ header หน้า · primary button ภายในโมดูล · active state ของเมนู sidebar

**ห้ามเอาสีโมดูลไปปนกับ semantic color** — เขียว=สำเร็จ/ผ่าน, amber=รอดำเนินการ/เตือน, แดง=ผิดพลาด/ลบ ใช้ความหมายเดียวกันทุกโมดูล ดังนั้น badge สถานะใน M4 (โมดูลสีเขียว) ก็ยังใช้เขียว/เหลือง/แดงตามความหมายของสถานะ ไม่ใช่สีโมดูล

### 2.2 กฎการใช้สี

- ต่อ 1 หน้า ใช้ไม่เกิน 3 hue: สีโมดูล + semantic + neutral (gray)
- Contrast ratio ≥ 4.5:1 สำหรับ body text (WCAG AA)
- Hover = สีเดิมเข้มขึ้น 1 ขั้น (`hover:bg-{color}-700`) · Focus = `focus:ring-2 focus:ring-{color}-300` · Disabled = `bg-gray-100 text-gray-400 cursor-not-allowed`
- Surface: การ์ด `bg-white border border-gray-200 shadow-sm` วางบนพื้นหลังหน้า `bg-gray-50`

---

## 3. Typography

| ระดับ | Class | ใช้กับ |
|---|---|---|
| Page title | `text-2xl font-bold` | h1 — ชื่อหน้า |
| Section title | `text-lg font-semibold` | หัวการ์ด/section |
| Label | `text-sm font-semibold` | label ฟอร์ม, หัวคอลัมน์ตาราง |
| Body | `text-sm` | เนื้อหา, cell ตาราง |
| Caption | `text-xs text-gray-500` | คำอธิบาย, วันที่, จำนวนรายการ |

รหัส/ตัวเลขที่ต้อง align กัน (รหัสนักศึกษา, รหัสวิชา, เลขที่เอกสาร) ใช้ `font-mono` เสมอ

---

## 4. Layout & Page Anatomy

### 4.1 App Shell (ทุกหน้าใช้โครงเดียวกัน)

```
┌────────────────────────────────────────────────────┐
│ Top bar: โลโก้+ชื่อระบบ · ค้นหา · กระดิ่งแจ้งเตือน · โปรไฟล์ │
├──────────┬─────────────────────────────────────────┤
│ Sidebar  │ Content                                  │
│ (w-60)   │ (bg-gray-50, p-6)                        │
└──────────┴─────────────────────────────────────────┘
```

- Sidebar แบ่ง 3 กลุ่มตามลำดับ: **โปรไฟล์** (บัญชีของฉัน) → **โมดูล** (เฉพาะที่ role มีสิทธิ์) → **ผู้ดูแลระบบ** (เห็นเฉพาะ admin: จัดการผู้ใช้งาน, Audit log)
- **ตั้งค่าการแจ้งเตือน** (M10 UC-11) อยู่ใต้ dropdown ของกระดิ่ง/โปรไฟล์ — ไม่ใช่เมนู sidebar เพราะเป็นการตั้งค่าส่วนตัว ไม่ใช่โมดูลงาน
- Mobile: sidebar ยุบเป็น hamburger (`hidden lg:block` + drawer)

### 4.2 Dashboard กลาง (state `Dashboard` ใน overview_state_diagram)

ลำดับบน→ล่าง:
1. คำทักทาย + role badge ของผู้ใช้
2. KPI cards 2-4 ใบ (grid, `bg-gray-100/50 rounded-lg`)
3. การ์ดทางลัดเข้าโมดูล — grid 3 คอลัมน์, **1 การ์ด = 1 app = 1 เมนูใน overview diagram** แต่ละใบมีไอคอนพื้นสีโมดูล + ชื่อ + คำอธิบายสั้น 1 บรรทัด

### 4.3 หน้า list/จัดการข้อมูล (โครงมาตรฐานทุกโมดูล)

1. **Top ของหน้า** — ชื่อหน้า + จำนวนรายการ + **primary action 1 ปุ่มเดียว** (มุมขวาบน)
2. **Filter bar** — ช่องค้นหา + ตัวกรอง
3. **Content** — ตาราง/การ์ด
4. **Pagination** — ใต้ content

---

## 5. Component Patterns (Tailwind class จริง)

### Buttons

```
Primary:   bg-{module}-600 hover:bg-{module}-700 text-white text-sm font-semibold rounded-xl px-4 py-2
Secondary: bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-xl px-4 py-2
Danger:    bg-red-600 hover:bg-red-700 text-white rounded-xl px-4 py-2
Ghost:     text-{module}-600 hover:bg-{module}-50 rounded-lg px-3 py-1.5
```

- Primary บน 1 หน้ามีได้ **1 ปุ่มเท่านั้น** (call-to-action หลักของหน้านั้น)
- Destructive action (ลบ/ยกเลิก/พ้นสภาพ) ต้องมี confirmation dialog ก่อนเสมอ
- ขนาดปุ่ม ≥ 44×44px สำหรับ touch

### Cards

```
bg-white rounded-2xl border border-gray-200 shadow-sm p-4
Interactive card เพิ่ม: hover:shadow-md transition-shadow cursor-pointer
```

### Form Fields

- Label อยู่ **บน** input เสมอ — ห้ามใช้ placeholder แทน label

```html
<label class="text-sm font-semibold text-gray-700">ชื่อ-นามสกุล</label>
<input class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
              focus:outline-none focus:ring-2 focus:ring-{module}-300">
<!-- error state -->
<input class="... border-red-400 focus:ring-red-200">
<p class="text-xs text-red-600 mt-1">ข้อความบอกวิธีแก้ ไม่ใช่แค่บอกว่าผิด</p>
```

### Badges (สถานะ)

```
inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold
bg-{semantic}-100 text-{semantic}-700
```

Mapping สถานะจริงของโครงการ → สี:

| สถานะ | สี |
|---|---|
| `DRAFT` | gray |
| `PENDING` / `SUBMITTED` / รอพิจารณา | amber |
| `APPROVED` / `ACTIVE` / ผ่าน / ชำระแล้ว | green |
| `REJECTED` / ไม่ผ่าน / `CANCELLED` | red |
| `PUBLISHED` | สีโมดูล |

### Tables

- Header: `text-xs uppercase tracking-wider text-gray-500 bg-gray-50`
- Row hover: `hover:bg-gray-50`
- Empty state: icon + ข้อความ + ปุ่ม CTA อยู่กลาง colspan ทั้งหมด

---

## 6. Icon

- lucide ชุดเดียวทั้งระบบ · ขนาด: 16px (inline), 20px (ปุ่ม/เมนู), 24px (การ์ด), 32px+ (empty state)
- ความหมายตายตัว ห้ามสลับ: ดินสอ=แก้ไข · ถังขยะ=ลบ · ตา=ดู · เครื่องหมายบวก=สร้างใหม่ · แว่นขยาย=ค้นหา · เฟือง=ตั้งค่า
- ปุ่มที่มีแต่ icon (icon-only) ต้องมี `title` หรือ `aria-label` เสมอ

---

## 7. UX States (ทุก action ต้องมีครบ)

| State | ต้องแสดง |
|---|---|
| Loading | spinner + disable ปุ่ม + ข้อความ "กำลัง..." |
| Success | toast แจ้งสำเร็จ (หายเองใน 4-5 วินาที) |
| Error | ข้อความ inline ใต้ field หรือ banner — ต้องบอกวิธีแก้ ไม่ใช่แค่ "เกิดข้อผิดพลาด" |
| Empty | icon + ข้อความ + ปุ่มพาไปสร้างรายการแรก |
| Disabled | เทา + `cursor-not-allowed` + tooltip บอกเหตุผล เช่น ปุ่มสมัครสหกิจ disabled พร้อม "ชั่วโมงอบรมยังไม่ครบ 30 ชม." (M8 UC-06) |

- Validation แสดงหลัง blur ไม่ใช่ระหว่างพิมพ์ (ยกเว้นช่องค้นหา)
- ช่องค้นหา debounce 300–500ms
- **Alternative Flow ทุกข้อใน usecase_description ต้องมี state บนหน้าจอรองรับ** — นี่คือจุดที่กรรมการใช้ตรวจว่าออกแบบครบ

---

## 8. สิทธิ์ตาม Role

- เมนู/ปุ่ม conditional render ตามตาราง **Actors** ใน fn req — role ที่ไม่มีสิทธิ์ต้อง "ไม่เห็น" ไม่ใช่แค่กดไม่ได้
- ตัวอย่างจริงในโครงการ: เมนู "จัดการผู้ใช้งาน" + "Audit log" เห็นเฉพาะ admin · ปุ่ม "แก้ไขผลประเมิน" ใน M8 Company Portal แสดงเฉพาะ `can_edit=true` (UC-18)
- Frontend ซ่อนเพื่อ UX เท่านั้น — การบังคับสิทธิ์จริงอยู่ที่ backend (JWT ผ่าน Traefik/M0) เสมอ

---

## 9. Accessibility & Responsive

- สีอย่างเดียวห้ามเป็นตัวบอกความหมายเดียว — ต้องมี icon หรือ text กำกับด้วยเสมอ
- ทุก interactive element ต้องมี focus state ที่มองเห็นได้ (ห้าม `outline-none` โดยไม่มี focus style ทดแทน)
- Mobile-first: เขียน base สำหรับ mobile แล้ว override ด้วย `md:` `lg:` · touch target ≥ 44×44px
- ทุก `<img>` มี alt text

---

## 10. Checklist ก่อนส่งงาน

- [ ] ทุก state ใน `module_state_diagram` มี route/หน้าจอครบ 1:1 (ไม่ขาด ไม่เกิน)
- [ ] ใช้สีประจำโมดูลตามตาราง §2.1 และไม่ปนกับ semantic color
- [ ] Primary button มี 1 ปุ่มต่อหน้า · destructive action มี confirmation
- [ ] Alternative Flow ทุกข้อใน usecase_description มี error/validation state จริงบนหน้าจอ
- [ ] เมนู/ปุ่มแสดงตาม role (ตรงตาราง Actors ใน fn req)
- [ ] Loading/Empty/Error/Disabled ครบทุกจุดที่มีการดึงข้อมูล
- [ ] Endpoint ที่เรียกตรงกับตาราง API ใน fn req (ใส่ comment กำกับใน api layer)
- [ ] Label อยู่บน input ทุกฟอร์ม ไม่มี placeholder แทน label
- [ ] Icon-only button มี title/aria-label ครบ
