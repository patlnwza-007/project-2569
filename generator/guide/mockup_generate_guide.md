# คู่มือการสร้าง Standalone Mockup (Mockup Generation Guide)

> ใช้คู่กับ [`fn req/<module>.md`](fn%20req/) (functional requirements), `<module>/proposal/usecase_description.md` (use case), `<module>/activity/*.puml` (รายละเอียด step/decision/loop ของแต่ละหน้าจอ — ดู §4.1) และ [`architecture/overview_state_diagram.puml`](../../architecture/overview_state_diagram.puml) (จุดเชื่อมเข้า-ออกกับ Dashboard/โมดูลอื่น) — ไฟล์นี้บอกวิธี **แปลง FN + Use Case + Activity Diagram ให้เป็นหน้าจอที่กดใช้งานได้จริง** โดยไม่ต้องมี server/backend/database จริง
>
> ใช้ [`mockup_template.md`](../template/mockup_template.md) เป็นจุดเริ่มก๊อปปี้ และดู [`mockup_example.md`](../example/mockup_example.md) เป็นตัวอย่างที่ทำตามกฎครบทุกข้อ — **หน้าตาของ mockup ต้องพ้องกับหน้าจริง (Django template)** ตาม design system กลางใน [`UI_django_frontend.md`](UI_django_frontend.md) (สีประจำแอป, layout, component เดียวกัน)
>
> ผลลัพธ์ที่ได้ใช้เป็น **สไลด์ 10 · Demo Mockup** ใน [`template_slides.md`](../template/template_slides.md) ได้ทันที (screenshot จาก mockup จริง ดีกว่าภาพนิ่งจาก Figma เพราะพิสูจน์ flow การทำงานได้จริงระหว่างสอบ)

---

## 1. นิยาม Standalone Mockup

**Standalone** = เปิดไฟล์ `.html` ได้ตรงจาก `file://` (ดับเบิลคลิกเปิดในเบราว์เซอร์) หรือรันผ่าน static server ง่ายๆ โดย**ไม่มี**:
- Backend/view จริงของ Django (ไม่รัน `manage.py runserver`)
- ฐานข้อมูลจริง (PostgreSQL)
- Authentication จริง (django-allauth / Google OAuth)
- การเรียก network request ไปยังบริการภายนอกจริง

**แต่ต้องทำได้ครบ:**
- ทุกปุ่ม/ลิงก์ต้อง**กดแล้วมีผลจริง** (เปลี่ยนหน้า, เปลี่ยนสถานะ, แสดงข้อมูลใหม่) — ห้ามมี `href="#"` ที่กดแล้วไม่เกิดอะไรขึ้น
- ทุก use case ใน `usecase_description.md` ต้องมีหน้าจอรองรับและ**เดิน flow ได้ครบตาม Basic Flow / Alternative Flow**
- ข้อมูลที่กรอก/แก้ไขต้อง**คงอยู่** เมื่อเปลี่ยนหน้าไปมา (จำลอง state ของระบบจริงด้วย `localStorage`)

**และหน้าตาต้องพ้องกับหน้าจริง (Django template):**
- ใช้ design system เดียวกับ [`UI_django_frontend.md`](UI_django_frontend.md) ทุกข้อ — สีประจำแอป (§2.1), typography, page anatomy (top bar + sidebar + content), component pattern (ปุ่ม/การ์ด/ฟอร์ม/ตาราง/badge)
- โครงหน้าจอต้องตรงกับ `<app>/state/module_state_diagram*.puml` ของแอปนั้น — **1 state = 1 หน้าจอ, เส้น = ปุ่มนำทาง** — mockup คือ "ภาพที่กดได้" ของหน้าจริง ไม่ใช่ดีไซน์อีกชุดหนึ่ง
- เป้าหมาย: screenshot จาก mockup กับจากหน้า Django จริงต้องดูเป็นระบบเดียวกันจนแยกไม่ออก — mockup ไม่ใช่ที่ทดลองดีไซน์ใหม่

---

## 2. โครงสร้างไฟล์แนะนำ — Shell + iframe + ไฟล์ .html จริงแยกตามหน้าใน state diagram

**กฎ: topbar/sidebar อยู่ใน `index.html` (shell) ตัวเดียว ส่วนเนื้อหาแต่ละ state เป็น .html จริงแยกไฟล์ ไม่ใช่ JS fragment** — เปิด `pages/page-<state>.html` ตรง ๆ ก็ต้องดูรู้เรื่องได้ทันทีโดยไม่ต้องพึ่ง router ใด ๆ (นี่คือกฎที่เข้มกว่าฉบับก่อนหน้าที่ใช้ JS object ผ่าน `<script src>` — ตอนนี้ต้องเป็นไฟล์ `.html` จริงเท่านั้น เพื่อให้ตรวจสอบและรีวิวแต่ละหน้าได้ตรงไปตรงมาที่สุด) ห้ามยัดทุกหน้าจอไว้ในไฟล์เดียวอีกต่อไป (แนวทางเดิมที่รวมเป็นไฟล์เดียวย้ายไปเป็น "ทางเลือกสำรอง" ท้ายข้อนี้)

```
<module>/mockup/<app>/
├── index.html            ← shell: topbar (โลโก้+ปุ่มกลับหน้าหลัก, role switcher ถ้ามี) + sidebar (ลิงก์จริงไปแต่ละ state) + <iframe>
├── shared.js              ← mock data (seed arrays ตาม Data Entities ใน fn req) + localStorage helpers + notifyParentPage() ร่วมทุกหน้า
└── pages/                  ← 1 ไฟล์ .html สมบูรณ์ต่อ 1 state ใน module_state_diagram (ตั้งชื่อตาม state, ไม่ใช่ตาม UC)
    ├── page-<state-1>.html   ← เช่น page-faculty-list.html สำหรับ state "FacultyList" — เปิดตรงจาก file:// ได้เองแม้ไม่ผ่าน iframe
    ├── page-<state-2>.html
    └── ...
```

**ทำไมใช้ `<iframe>` + ไฟล์ .html จริง แทนที่จะเป็น `fetch()`/`<script type="module">`:** `fetch()` และ ES module import ถูกเบราว์เซอร์ (โดยเฉพาะ Chrome) บล็อกด้วย CORS เมื่อเปิดผ่าน `file://` ตรง ๆ — แต่การนำทางเอกสาร (`<a href>`, `<iframe src>`) ไม่ติด CORS แบบเดียวกัน จึงใช้ `<iframe>` เป็น "ช่องแสดงเนื้อหา" ที่สลับ `src` ไปมาระหว่างไฟล์ `.html` จริงในโฟลเดอร์ `pages/` ได้ตรง ๆ โดยไม่ต้องมี local server — topbar/sidebar อยู่ใน parent frame (`index.html`) จุดเดียว ไม่ต้องซ้ำโค้ด layout ในทุกไฟล์

```html
<!-- index.html — shell: topbar/sidebar ของจริง + iframe แสดงเนื้อหา -->
<header>...โลโก้ + ปุ่ม "← กลับหน้าหลัก" (href="../../main%20page/index.html") + role switcher ถ้าแอปนี้มีหลาย role...</header>
<nav>
  <a data-page="faculty-list" href="pages/page-faculty-list.html" target="main-frame" data-roles="hr">รายการอาจารย์</a>
  <!-- data-roles คุมว่า role ไหนเห็นเมนูนี้ — ใช้คู่กับ role switcher ด้านล่าง -->
</nav>
<iframe id="main-frame" name="main-frame" src="pages/page-faculty-list.html"></iframe>

<script src="shared.js"></script>
<script>
  // ไฮไลต์เมนูที่ active ตาม postMessage จากหน้าลูกใน iframe
  window.addEventListener("message", (ev) => {
    if (ev.data?.type === "<module>-<app>-page") setActiveMenu(ev.data.page);
  });
  // role switcher (ถ้ามี): เปลี่ยน localStorage + กรองเมนู + reload iframe ไปหน้าแรกของ role นั้น
  function setRole(role) {
    localStorage.setItem("<key>_role", role);
    document.querySelectorAll("[data-roles]").forEach(el =>
      el.classList.toggle("hidden", !el.dataset.roles.split(",").includes(role)));
    document.getElementById("main-frame").src = "pages/" + ({ hr: "page-faculty-list.html", faculty: "page-profile.html" })[role];
  }
</script>
```

```html
<!-- pages/page-faculty-list.html — 1 ไฟล์ .html สมบูรณ์ต่อ 1 state, เปิดเองได้โดยไม่ต้องพึ่ง iframe -->
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body onload="init()">
  <!-- เนื้อหาของ state นี้ล้วน ๆ ไม่มี topbar/sidebar (อยู่ใน shell แล้ว) -->
  <h1>รายการอาจารย์</h1>
  <div id="rows"></div>

  <script src="../shared.js"></script>
  <script>
    function init() { render(); notifyParentPage("faculty-list"); }
    function render() { /* ดึงจาก seed data ใน shared.js มา render ตาราง */ }
  </script>
</body>
</html>
```

**การส่งข้อมูล "รายการที่กำลังแก้ไข" ข้ามหน้า:** เดิมที่รวมไฟล์เดียวใช้ตัวแปร JS (เช่น `let target = ...`) เก็บไว้ก่อนเรียก `go('somepage')` — ตอนนี้แต่ละหน้าเป็นเอกสารแยกกัน ตัวแปรแบบนี้ไม่รอดข้ามการนำทาง **ต้องส่งผ่าน URL query param แทน** เช่น `pages/page-assign.html?tid=3`, อ่านด้วย `new URLSearchParams(location.search).get("tid")` — ปุ่ม/ลิงก์ที่เคย `onclick="go('assign')"` (มีการตั้งตัวแปรก่อนหน้า) เปลี่ยนเป็น `<a href="page-assign.html?tid=${id}">` ตรง ๆ

**สรุปกฎการนำทาง:**
- เมนูใน sidebar ที่เข้าถึงได้จาก state diagram โดยตรง → `<a href="pages/page-X.html" target="main-frame">` ใน shell
- ปุ่ม/ลิงก์ที่นำทางระหว่าง sub-state ภายใน flow เดียวกัน (ไม่ผ่านเมนู) → `<a href="page-X.html">` ธรรมดา หรือ `window.location.href = "page-X.html"` หลัง validate ผ่าน (อยู่ในไฟล์ page เอง ไม่ใช่ shell)
- ทุกหน้าใน `pages/` เรียก `notifyParentPage("<state-key>")` ตอนโหลด (ฟังก์ชันอยู่ใน `shared.js`) เพื่อให้ shell ไฮไลต์เมนูถูกต้อง

ข้อดีของโครงนี้: 1) ตรวจ traceability ง่ายที่สุด — เปิดโฟลเดอร์ `pages/` แล้วนับไฟล์ `.html` เทียบกับจำนวน state ใน diagram ได้ทันที ไม่ต้องเปิดโค้ดอ่าน (ดู §4.2) 2) แต่ละไฟล์เปิดเองตรงจาก `file://` ได้จริง ไม่ต้องพึ่ง shell/iframe เพื่อดูเนื้อหา ทำให้รีวิว/แชร์ทีละหน้าได้ง่ายที่สุด ไม่ต้องอ่าน JS router 3) `index.html` แก้ topbar/sidebar จุดเดียว มีผลทุกหน้าอัตโนมัติ (สอดคล้องกับ `base.html` app shell ใน `UI_django_frontend.md` §4.1) 4) ยังเปิดจาก `file://` ได้ตรง ๆ เพราะ `<iframe src>`/`<a href>` ไม่ติด CORS แบบ `fetch()`

**ทางเลือกสำรอง (ใช้เฉพาะกรณีต้องส่งไฟล์เดียวจริง ๆ เช่น แนบอีเมลข้อสอบ):** รวมทุกอย่างเป็น **ไฟล์ `.html` เดียว** (CSS/JS inline, ทุกหน้าจอเป็น `<section>` ที่ show/hide ด้วย JavaScript) — ใช้เมื่อจำเป็นเท่านั้น ไม่ใช่ค่าเริ่มต้นอีกต่อไป เพราะเสียข้อดีเรื่องแยกไฟล์/ตรวจ traceability ในข้อ 1)-2) ข้างต้น

---

## 3. Data Layer จำลอง (Mock Data + State)

### 3.1 สร้างข้อมูลตัวอย่างจาก Data Entities

ดึง entity ตรงจาก fn req หัวข้อ **"6. Data Entities"** มาเป็น array ของ object ใน `mock-data.js`:

```js
// ตัวอย่างจาก fn req/m9_project_thesis.md — entity: thesis
const mockTheses = [
  { id: 1, student_id: "S001", title_th: "ระบบ...", status: "APPROVED", advisor_id: 12 },
  { id: 2, student_id: "S002", title_th: "การพัฒนา...", status: "DRAFT", advisor_id: null },
];
```

### 3.2 ใช้ localStorage แทนฐานข้อมูลจริง

```js
function loadData(key, fallback) {
  const saved = localStorage.getItem(key);
  return saved ? JSON.parse(saved) : fallback;
}
function saveData(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}
// โหลดครั้งแรกจาก mock-data.js แล้วเซฟกลับทุกครั้งที่มีการแก้ไข
let theses = loadData("theses", mockTheses);
```

### 3.3 ปุ่ม "รีเซ็ตข้อมูลตัวอย่าง"

ต้องมีปุ่มซ่อนไว้มุมจอ (เช่น footer) เพื่อล้าง `localStorage` กลับสู่ข้อมูลตั้งต้น — จำเป็นเพราะกรรมการอาจกดทดลองจนข้อมูลเพี้ยน ต้องรีเซ็ตก่อนสอบรอบถัดไปได้

---

## 4. Mapping จาก Use Case → หน้าจอ (Traceability)

**กฎ: 1 use case ใน `usecase_description.md` = อย่างน้อย 1 หน้าจอ/1 ส่วนใน mockup**

### 4.1 แหล่งข้อมูลที่ต้องอ่านก่อน map ทีละหน้า (เรียงลำดับการอ่าน)

`usecase_description.md` บอกแค่ว่า "มี use case อะไรบ้าง" ในระดับ goal — ไม่พอสำหรับ map เป็นหน้าจอที่กดได้จริงทีละปุ่ม ต้องอ่านเพิ่มอีก 2 แหล่งตามลำดับนี้ **ก่อนเริ่มลงมือเขียนแต่ละหน้า**:

1. **`<module>/activity/*.puml`** — อ่าน**ทุกไฟล์**ของโมดูลที่กำลังทำ ก่อน map แต่ละหน้าจอ เพราะ activity diagram มีรายละเอียดที่ usecase_description ไม่มี:
   - **partition (swimlane)** บอกว่าขั้นตอนไหนเกิดที่ฝั่ง actor (= ต้องมี UI จริง) และขั้นตอนไหนเกิดที่ฝั่ง service อื่น (= ต้อง mock ตาม §7 ไม่ใช่วาดหน้าจอ)
   - **decision node (`if/else`)** บอกจุดที่ mockup ต้อง trigger error/แจ้งเตือนจริงตาม Alternative Flow — แปลงตรงเป็นเงื่อนไข `if` ใน JS
   - **fork/end fork** (audit log, notification) บอกว่าไม่ต้องรอผลลัพธ์ก่อนไปหน้าถัดไป — mockup จำลองเป็น toast แล้วนำทางต่อได้ทันที ไม่ต้องรอ
   - **repeat/repeat while** บอกจุดที่ต้อง loop ใน UI จริง (เช่น retry, แก้ไขแล้วส่งใหม่) — ต้องกดวนได้จริงในหน้าเดียวกัน ไม่ใช่จบ flow แค่รอบเดียว
   - ไฟล์ 1 ไฟล์อาจครอบคลุมหลาย UC (ดู mapping table ท้ายไฟล์ `*_description.md` ของ M8/M9 ถ้ามี) — ให้เดิน flow ตามไฟล์ activity ไม่ใช่แยกทำทีละ UC เดี่ยว ๆ เพราะ UI จริงมักรวมหลาย UC ไว้หน้าเดียวกันตามที่ activity diagram แสดง

2. **`architecture/overview_state_diagram.puml`** — ใช้กำหนด**จุดเข้า-ออกของ mockup โมดูลนี้กับส่วนที่เหลือของระบบ**:
   - หา state ที่ตรงกับโมดูลนี้ในไดอะแกรม (เช่น `CurriculumApp`, `CoopApp`) แล้วดูว่า Dashboard เชื่อมเข้ามาด้วย action ว่าอะไร (เช่น `กดเมนู "หลักสูตร"`) — ปุ่ม/ลิงก์ "กลับหน้าหลัก" ใน mockup ต้องใช้คำเดียวกับ label บนเส้นนั้น เพื่อให้ demo ข้ามโมดูลแล้วเรื่องราวต่อเนื่องกัน
   - ถ้า mockup ทำแยกทีละโมดูล (คนละไฟล์/คนละโฟลเดอร์) ให้ใส่ปุ่ม/ลิงก์ "กลับหน้าหลัก" ที่จุดเดิมเสมอ แม้จะไม่มี Dashboard จริงให้กลับไป (ลิงก์ไปหน้าเปล่า/alert "กลับสู่ Dashboard (จำลอง)" ก็ได้ — สำคัญที่ตำแหน่ง/คำที่ใช้ต้องตรงกับ diagram)
   - ถ้าโมดูลมีหลายแอปในไดอะแกรม (เช่น M4 มี Applicant/Registrar/Online-Onsite Interview) แต่ละแอปต้องมี entry point แยกกันใน mockup ตรงกับที่ overview ระบุ ไม่ใช่ยำรวมเป็นเมนูเดียว

3. **`<module>/state/module_state_diagram*.puml`** — ตัวกำหนดจำนวนหน้าจอสุดท้าย (1 state = 1 `<section>`/1 ไฟล์) ตามที่ระบุใน §1 อยู่แล้ว — ใช้เป็นตัวเช็คสุดท้ายว่าหน้าจอที่ได้จาก activity diagram (ข้อ 1) ครบตรงกับจำนวน state ที่นี่พอดี ไม่ขาดไม่เกิน

สรุปลำดับอ่าน: **usecase_description.md** (รู้ว่ามี UC อะไร) → **activity/*.puml** (รู้ step/decision/loop ละเอียดของแต่ละ UC เพื่อ map เป็นปุ่ม/ฟอร์มทีละหน้า) → **module_state_diagram*.puml** (ยืนยันจำนวน/ขอบเขตหน้าจอ) → **overview_state_diagram.puml** (ยืนยันจุดเชื่อมเข้า-ออกกับ Dashboard/โมดูลอื่น)

### 4.2 ตาราง Mapping (Traceability)

ทำตารางcheck รายการก่อนเริ่มสร้าง (ป้องกันหลุด) — เพิ่มคอลัมน์ไฟล์ activity ที่ใช้อ้างอิงด้วย:

| UC | ชื่อ Use Case | ไฟล์ activity ที่ใช้ map | State ใน module_state_diagram | ไฟล์ที่รองรับ | สถานะ |
|----|--------------|--------------------------|-------------------------------|----------------|:---:|
| UC-01 | {{ชื่อ}} | `activity/activity_uc01_....puml` | `{{StateName}}` | `pages/page-{{state-name}}.js` | ☐ |
| UC-02 | {{ชื่อ}} | `activity/activity_uc02_....puml` | `{{StateName}}` | `pages/page-{{state-name}}.js` | ☐ |
| ... | ... | ... | ... | ... | ☐ |

หลาย UC ที่อยู่ state เดียวกัน (เช่น UC-02/03/04 ของ M3 ที่รวมเป็นแท็บในหน้า OwnProfile เดียว) จะมีแถวชี้ไปไฟล์ `pages/page-....js` เดียวกันซ้ำได้ — ไม่ใช่ข้อผิดพลาด

แต่ละหน้าจอต้องมีองค์ประกอบตรงกับตารางในไฟล์ use case description:

| คอลัมน์ใน usecase_description.md | แปลงเป็นอะไรใน mockup |
|-----------------------------------|------------------------|
| Actor หลัก | เมนู/หน้าจอนี้ต้องแสดงเฉพาะตอน login เป็น role นั้น (ดู §5) |
| Basic Flow (ลำดับเหตุการณ์หลัก) | ลำดับปุ่ม/ฟอร์มบนหน้าจอ — **ยึดลำดับ partition/activity ใน `.puml` ตาม §4.1 ข้อ 1 เป็นหลัก** ไม่ใช่แค่ข้อความสั้นใน Basic Flow |
| Alternative Flow | ต้อง trigger error/แจ้งเตือนได้จริงเมื่อทำตามเงื่อนไขนั้น — **เอา decision node ใน activity diagram มาแปลงเป็น `if` ตรง ๆ** |
| Post-condition | หลังกดปุ่ม action หลัก ต้องเห็นการเปลี่ยนแปลงจริง (สถานะเปลี่ยน, มีข้อมูลใหม่ในตาราง) |
| เกี่ยวข้องกับ Service/Endpoint อื่น | ดู §7 วิธี simulate การเรียกข้าม service — **ดู partition ของ service อื่นใน activity diagram ประกอบว่าเรียกตอนไหน ส่งอะไรไปให้** |

---

## 5. Role-based Navigation (จำลอง Login)

**หน้าเลือก role ก็เป็น "page" 1 ไฟล์เหมือนกัน** (เช่น `pages/page-login.js`) แต่ต่างจาก page อื่นตรงที่ `render()` ของมันไม่ต้องพึ่ง `Layout.topbar`/`Layout.sidebar` — `app.js` เช็คว่ายังไม่มี `current_role` ให้ข้าม topbar/sidebar แล้วโชว์แค่หน้านี้เต็มจอ:

```js
// pages/page-login.js
const Pages = window.Pages || (window.Pages = {});
Pages["login"] = {
  render() {
    return `
      <h2>เลือกบทบาทเพื่อทดลองใช้งาน</h2>
      <button onclick="loginAs('student')">นักศึกษา</button>
      <button onclick="loginAs('advisor')">อาจารย์ที่ปรึกษา</button>
      <button onclick="loginAs('dept_head')">หัวหน้าภาควิชา</button>`;
  },
};
function loginAs(role) {
  localStorage.setItem("current_role", role);
  go(Object.keys(Pages).find((k) => k !== "login")); // ไปหน้าแรกของแอป
}
```

```js
// app.js — เพิ่มเงื่อนไขก่อนเรียก Layout ถ้ายังไม่ login
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
  document.getElementById("sidebar").innerHTML = Layout.sidebar.render(stateKey, role);
  document.getElementById("main").innerHTML = Pages[stateKey].render();
  Pages[stateKey].afterRender?.();
}
```

ทุก page (`render()`) ต้องเช็ค `roles` ของตัวเองเทียบกับ `current_role` ผ่าน `Layout.sidebar` เป็นตัวกรองเมนู (ตรงกับตาราง **Actors** ใน fn req) — ห้ามแสดงปุ่ม/เมนูที่ role นั้นไม่มีสิทธิ์ แม้จะเป็น mockup ก็ตาม เพราะเป็นส่วนหนึ่งของการพิสูจน์ว่าออกแบบสิทธิ์ถูกต้อง

**ปุ่ม "สลับบทบาท"** อยู่ใน `Layout.topbar.render()` เสมอ (ไม่ใช่ของจริง แต่ช่วย demo ครบทุก role จากไฟล์เดียวกันโดยไม่ต้อง logout/login ใหม่)

---

## 6. ทำให้ทุกปุ่ม/ลิงก์ทำงานได้จริง

**กฎเหล็ก:** ทุก `<button>`/`<a>` ต้องมี `onclick` หรือ event listener ที่ทำสิ่งใดสิ่งหนึ่งจริง:

| ประเภทปุ่ม | ต้องเกิดอะไรขึ้นจริง |
|-----------|----------------------|
| ปุ่ม "บันทึก/ส่ง" | เขียนข้อมูลใหม่ลง array + `saveData()` + แสดงข้อความยืนยัน + เปลี่ยนหน้า/สถานะ |
| ปุ่ม "อนุมัติ/ปฏิเสธ" | เปลี่ยน `status` field ของ record + refresh หน้าให้เห็นผลทันที |
| ปุ่ม "ค้นหา/กรอง" | filter array จริงด้วย JS แล้ว render ผลใหม่ (ไม่ใช่ตารางนิ่ง) |
| ปุ่ม "ยกเลิก" | เปลี่ยน status เป็น CANCELLED จริง ไม่ใช่แค่กลับหน้าเดิม |
| ลิงก์เมนู | นำทางไปหน้าจริง ต้องไม่ใช่ `href="#"` ค้างที่หน้าเดิม |

**Validation ต้องทำงานจริง** ตาม Alternative Flow เช่น "กรอกไม่ครบ → ระบบแจ้งเตือน" — ต้องเขียน JS ตรวจ field จริงและ `alert()`/แสดงข้อความ error จริง ไม่ใช่แค่ปุ่มกดผ่านตลอด

---

## 7. สิ่งที่ Standalone ทำไม่ได้จริง — และวิธี Simulate แทน

| ฟังก์ชันในระบบจริง | ทำไมทำจริงไม่ได้แบบ standalone | วิธี Simulate |
|---------------------|-------------------------------|----------------|
| **ดึงข้อมูลจาก app อื่น** (เช่น `borrow` ดึงรายการของจาก `catalog`) | ไม่มี view/ORM จริง | เขียน mock function คืนค่าจาก `mock-data.js` ทันที พร้อม comment `// ระบบจริง: Item.objects.filter(...)` |
| **Authentication (allauth/Google OAuth)** | ไม่มี allauth/Google จริง | ใช้ role switcher ใน §5 แทน ไม่ต้องล็อกอิน Google จริง |
| **อัปโหลดไฟล์/รูปภาพ** | ไม่มี server/`MEDIA_ROOT` จริง | ใช้ `FileReader` API อ่านไฟล์ที่เลือกแล้วแสดง preview ในเบราว์เซอร์ ("อัปโหลดสำเร็จ (จำลอง)") โดยไม่ต้องส่งไปไหนจริง |
| **ส่งอีเมล/แจ้งเตือน** | ไม่มี mail server จริง | แสดง toast/banner "ส่งอีเมลแจ้งเตือนแล้ว (จำลอง)" |
| **สร้างเอกสาร PDF/CSV** (เช่น รายงาน, ทะเบียนพัสดุ) | ไม่มี backend generate ไฟล์จริง | ใช้ library ฝั่ง client ที่ทำงานได้แบบ standalone จริง เช่น **jsPDF** (CDN) สร้าง PDF จริงจากข้อมูลใน mockup ได้ทันที หรืออย่างน้อยใช้ `window.print()` เปิด print-preview |
| **QR Code / real-time conflict check** | ไม่มี backend/scheduler จริง | สร้าง QR ด้วย library ฝั่ง client (เช่น qrcode.js CDN) · ตรวจ overlap ของจำนวน/เวลาจาก array ใน memory ตรง ๆ (logic เดียวกัน ผลลัพธ์เหมือนกัน) |
| **คำนวณ/ธุรกิจซับซ้อน** (GPA, weighted score, attainment) | — ทำได้จริง ไม่ต้อง simulate | เขียนสูตรคำนวณจริงด้วย JavaScript ตรงๆ ได้เลย เพราะเป็น pure computation ไม่พึ่ง server |

> **หลักการ:** ฟังก์ชันที่เป็น **pure logic/computation** (คำนวณเกรด, ตรวจ validation, กรอง/ค้นหา) ให้เขียน**จริง**เสมอ อย่า mock เฉยๆ เพราะทำได้ไม่ยากและแสดงความเข้าใจ business logic — ที่ต้อง mock คือเฉพาะส่วนที่ต้องพึ่ง **infrastructure ภายนอก** เท่านั้น (network, storage, auth, mail)

---

## 8. เครื่องมือ/Library แนะนำ (ไม่ต้อง build step)

| งาน | เครื่องมือ | เหตุผล |
|-----|-----------|--------|
| โครงสร้างหน้า | HTML + Vanilla JS | ไม่ต้อง build, เปิด `file://` ได้ตรงๆ |
| Styling เร็ว | Tailwind CSS ผ่าน CDN (`<script src="https://cdn.tailwindcss.com">`) | ไม่ต้อง build, ได้ผลลัพธ์สวยเร็ว |
| Interactivity ที่ซับซ้อนขึ้น (ถ้าต้องการ) | Alpine.js ผ่าน CDN | เบา ไม่ต้อง build, syntax คล้าย Vue |
| สร้าง PDF จริงฝั่ง client | jsPDF ผ่าน CDN | ทำงาน standalone ได้จริง ไม่ต้องมี backend |
| ไอคอน | Lucide/Heroicons (SVG inline หรือ CDN) | เบา ไม่ต้อง build |
| **หลีกเลี่ยง** | React/Vue/Angular ที่ต้อง `npm run build` | ขัดหลัก standalone เว้นแต่จะ bundle เป็น 1 ไฟล์ static จริงจบ |

---

## 9. Checklist ความครบถ้วนก่อนส่งงาน

- [ ] ทุก use case ใน `usecase_description.md` มีหน้าจอรองรับ (เทียบตาราง §4.2 ครบ ☐ → ✅ ทุกแถว)
- [ ] อ่าน `<module>/activity/*.puml` ครบทุกไฟล์ก่อน map แล้วนำ decision/loop/fork มาแปลงเป็น validation/error/loop จริงในหน้าจอ (§4.1 ข้อ 1)
- [ ] ปุ่ม/ลิงก์ "กลับหน้าหลัก" ของแต่ละแอปใช้คำตรงกับ action label ใน `architecture/overview_state_diagram.puml` (§4.1 ข้อ 2)
- [ ] ทุกหน้าจอตรงกับ state ใน `module_state_diagram` ของโมดูล (1 state = 1 หน้าจอ ไม่ขาด ไม่เกิน)
- [ ] แยกไฟล์ตามโครง §2: `layout/topbar.js` + `layout/sidebar.js` แยกจาก `pages/*.js` และมี **1 ไฟล์ต่อ 1 state** ในโฟลเดอร์ `pages/` (นับไฟล์เทียบ state diagram ได้ตรง ๆ) — ไม่ยัดรวมเป็นไฟล์เดียวเว้นแต่เข้าเงื่อนไขทางเลือกสำรอง
- [ ] ใช้สีประจำแอป + component pattern ตาม [`UI_django_frontend.md`](UI_django_frontend.md) — ไม่มีดีไซน์ที่หลุดจาก design system กลาง
- [ ] เปิดไฟล์จาก `file://` ตรงๆ ได้โดยไม่ error (ทดสอบโดยไม่มี internet ยกเว้น CDN ที่ใช้)
- [ ] ไม่มี `href="#"` หรือปุ่มที่กดแล้วไม่เกิดอะไรขึ้นเลยแม้แต่จุดเดียว
- [ ] ข้อมูลที่กรอกคงอยู่หลังเปลี่ยนหน้า (ทดสอบ: กรอกฟอร์ม → ไปหน้าอื่น → กลับมา ต้องเห็นข้อมูลเดิม)
- [ ] สลับ role ได้ และแต่ละ role เห็นเฉพาะเมนู/ปุ่มตามสิทธิ์จริงใน fn req
- [ ] Validation/Alternative Flow ทำงานจริง (ทดสอบ: กรอกผิด/ไม่ครบ ต้องเห็น error จริง)
- [ ] มีปุ่มรีเซ็ตข้อมูลตัวอย่างกลับสู่สถานะเริ่มต้น
- [ ] ฟังก์ชันคำนวณ (ถ้ามีใน module นั้น เช่น GPA, weighted score) คำนวณถูกต้องจริง ไม่ใช่ค่า hardcode
- [ ] จุดที่ควรเรียก service อื่น มี comment ระบุ endpoint จริงกำกับไว้ (เผื่อกรรมการถามว่า "ของจริงเรียกอะไร")
- [ ] ทุก path (CSS/JS/รูป/ลิงก์ระหว่างหน้า) เป็น **relative path** ไม่มี absolute path ขึ้นต้นด้วย `/` เลย (จำเป็นสำหรับ GitHub Pages §11.3)
- [ ] ทดสอบผ่าน local static server (ไม่ใช่แค่ `file://`) อย่างน้อย 1 ครั้งก่อน deploy ขึ้น GitHub Pages

---

## 10. เชื่อมกับสไลด์นำเสนอ

Mockup ที่ทำเสร็จตามคู่มือนี้ใช้ต่อกับ [`template_slides.md`](../template/template_slides.md) **Slide 10 · Demo Mockup** ได้โดยตรง:
- ถ่าย screenshot จากหน้าจอที่ทำงานจริงแทนภาพนิ่งจาก Figma
- หรือ**สาธิตสด** (live demo) แทนสไลด์ในช่วง Slide 10 ได้เลย เพราะไฟล์เปิดได้ทันทีไม่ต้องพึ่ง internet/server ตอนสอบ — ลดความเสี่ยงเรื่อง WiFi ห้องสอบล่ม

---

## 11. Deploy ขึ้น GitHub Pages

Mockup ตามคู่มือนี้เป็น static HTML/CSS/JS ล้วน — ตรงกับสิ่งที่ **GitHub Pages** รองรับพอดี ไม่ต้องแก้โค้ดเพิ่ม

### 11.1 ขั้นตอน
1. Push โฟลเดอร์ mockup ขึ้น GitHub repo (จะ push ทั้ง repo หรือแยก repo เฉพาะ mockup ก็ได้)
2. ไปที่ **Settings → Pages** ของ repo เลือก branch (เช่น `main`) และโฟลเดอร์ (เช่น `/` หรือ `/docs`)
3. ได้ URL รูปแบบ `https://<username>.github.io/<repo-name>/` พร้อมแชร์ให้กรรมการเปิดดูเองได้ทันที

### 11.2 ทำไมควร deploy ขึ้น GitHub Pages แทนเปิด `file://` อย่างเดียว

| ประเด็น | `file://` (เปิดในเครื่อง) | GitHub Pages |
|---------|---------------------------|----------------|
| localStorage | บางเบราว์เซอร์ (โดยเฉพาะ Chrome) จำกัด/บล็อก localStorage ภายใต้ origin แบบ `file://` | ทำงานเสถียรเพราะมี origin จริง (`https://...github.io`) |
| แชร์ให้กรรมการดู | ต้องส่งไฟล์ให้โหลดเอง | ส่งแค่ URL เดียว เปิดจากมือถือ/เครื่องไหนก็ได้ |
| CDN (Tailwind/Alpine/jsPDF) | ทำงานได้ถ้ามี internet ตอนเปิด | เหมือนกัน (ต้องมี internet ทั้งคู่) |

### 11.3 ข้อควรระวัง — ต้องใช้ Relative Path เท่านั้น

GitHub Pages เสิร์ฟจาก **subpath** (`https://<username>.github.io/<repo-name>/...`) ไม่ใช่ root domain — ถ้าใช้ absolute path เช่น `/style.css` หรือ `/pages/page-list.js` จะเปิดไม่เจอ (404) เพราะเบราว์เซอร์จะไปมองหาที่ root ของ `github.io` แทน

- ✅ ใช้: `./style.css`, `pages/page-list.js`, `layout/sidebar.js`
- ❌ ห้ามใช้: `/style.css`, `/pages/page-list.js`

ทดสอบก่อน push เสมอโดยรันผ่าน local static server (เช่น VS Code Live Server) แทนการเปิด `file://` ตรงๆ เพื่อจับ path ที่พังได้ก่อนขึ้นจริง
