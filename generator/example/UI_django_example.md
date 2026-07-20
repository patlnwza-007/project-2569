# ตัวอย่าง — UI Django MVT ที่ทำตามกฎครบทุกข้อ (Dashboard กลางของระบบ)

> ตัวอย่างนี้คือ **หน้า Dashboard หลัง login** — state `Dashboard` ใน [`architecture/overview_state_diagram.puml`](../../architecture/overview_state_diagram.puml) ซึ่งเป็นจุดแตกแขนงไปทุก app ของระบบ — เขียนตามกฎใน [`UI_django_frontend.md`](../guide/UI_django_frontend.md) ครบทุกข้อ ใช้เป็นตัวอย่างอ้างอิงตอนสร้างหน้าอื่นต่อ
>
> ใช้ระบบตัวอย่าง **UBORROWU** (ยืม-คืนพัสดุ) 3 role: นักศึกษา (Student) / เจ้าหน้าที่ (Staff) / ผู้ดูแลระบบ (Admin)

จุดที่ตัวอย่างนี้สาธิตให้เห็น:
- **App shell = `base.html`** — top bar + sidebar 3 กลุ่ม (โปรไฟล์ / โมดูล / ผู้ดูแลระบบ) render ฝั่ง server (guide §4.1)
- **สีประจำแอป** ผ่าน `APP_STYLES` map ในฝั่ง Python — ไม่ประกอบ class แบบ dynamic (guide §2.3)
- **1 การ์ดทางลัด = 1 app** ตรงกับเมนูใน overview_state_diagram (guide §4.2)
- **Conditional render ตาม role** — การ์ด/เมนูผู้ดูแลระบบเห็นเฉพาะ admin ผ่าน `{% if perms %}` และ view บังคับสิทธิ์จริง (guide §8)
- **Toast จาก Django messages** + **KPI จาก ORM** (guide §7)

---

## ตาราง Mapping (ตาม template §1)

| State (หน้าจอ) | URL + name | View | Template | อ้างอิง | Role ที่เห็น |
|---|---|---|---|---|---|
| Dashboard | `/` · `core:dashboard` | `DashboardView` | `core/dashboard.html` | overview_state_diagram | ทุก role (การ์ดกรองตามสิทธิ์) |

---

## โค้ด

```python
# ui/styles.py — ตารางสีล็อกตาม guide §2.1 (string เต็ม กัน Tailwind purge)
APP_STYLES = {
    "accounts": {"icon": "bg-blue-100 text-blue-700",   "btn": "bg-blue-600 hover:bg-blue-700",   "active": "bg-blue-50 text-blue-700"},
    "catalog":  {"icon": "bg-violet-100 text-violet-700","btn": "bg-violet-600 hover:bg-violet-700","active": "bg-violet-50 text-violet-700"},
    "borrow":   {"icon": "bg-teal-100 text-teal-700",    "btn": "bg-teal-600 hover:bg-teal-700",    "active": "bg-teal-50 text-teal-700"},
    "queue":    {"icon": "bg-orange-100 text-orange-700","btn": "bg-orange-600 hover:bg-orange-700","active": "bg-orange-50 text-orange-700"},
    "reports":  {"icon": "bg-green-100 text-green-700",  "btn": "bg-green-600 hover:bg-green-700",  "active": "bg-green-50 text-green-700"},
    "admin":    {"icon": "bg-slate-100 text-slate-700",  "btn": "bg-slate-600 hover:bg-slate-700",  "active": "bg-slate-100 text-slate-700"},
}
```

```python
# core/views.py — Dashboard: KPI จาก ORM + การ์ดทางลัดกรองตามสิทธิ์
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from catalog.models import Item
from borrow.models import BorrowRequest

# 1 การ์ด = 1 app = 1 เมนูใน overview_state_diagram — ห้ามเพิ่มการ์ดที่ไม่มี app รองรับ
# perm = None คือทุกคนเห็น · ระบุ perm string เพื่อจำกัดเฉพาะ role ที่มีสิทธิ์
APPS = [
    {"url": "accounts:me",        "label": "บัญชีของฉัน",      "desc": "โปรไฟล์และเบอร์ติดต่อ",   "icon": "user",     "style": "accounts", "perm": None},
    {"url": "catalog:item_list",  "label": "คลังพัสดุ",         "desc": "วัสดุ / ครุภัณฑ์",         "icon": "book",     "style": "catalog",  "perm": None},
    {"url": "borrow:my_requests", "label": "การยืมของฉัน",     "desc": "คำขอ / สถานะ / คืน",       "icon": "clipboard","style": "borrow",   "perm": None},
    {"url": "borrow:approvals",   "label": "อนุมัติคำขอ",       "desc": "รายการรออนุมัติ",         "icon": "check",    "style": "borrow",   "perm": "borrow.change_borrowrequest"},
    {"url": "reports:dashboard",  "label": "รายงาน",            "desc": "สรุป / กราฟ / ส่งออก",     "icon": "chart",    "style": "reports",  "perm": "borrow.view_borrowrequest"},
    {"url": "admin_console:users","label": "จัดการผู้ใช้งาน",   "desc": "บัญชี / Whitelist / สิทธิ์","icon": "settings", "style": "admin",    "perm": "auth.view_user"},
]

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        # การ์ดทางลัด: กรองตาม permission ของ user (guide §8)
        ctx["apps"] = [a for a in APPS if a["perm"] is None or user.has_perm(a["perm"])]
        # KPI จาก ORM จริง
        ctx["kpi"] = {
            "items": Item.objects.count(),
            "borrowing": BorrowRequest.objects.filter(status="ACTIVE").count(),
            "pending": BorrowRequest.objects.filter(status="PENDING").count(),
        }
        return ctx
```

```django
{# core/templates/core/dashboard.html #}
{% extends "base.html" %}
{% block title %}หน้าหลัก · UBORROWU{% endblock %}

{% block content %}
  {# คำทักทาย + role badge — guide §4.2 ข้อ 1 #}
  <div class="mb-1 flex items-center gap-2">
    <h1 class="text-2xl font-bold">สวัสดี, {{ user.get_full_name|default:user.email }}</h1>
    <span class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold bg-blue-100 text-blue-700">
      {{ user.groups.first.name|default:"นักศึกษา" }}
    </span>
  </div>
  <p class="text-xs text-gray-500 mb-5">ภาคเรียนที่ 1/2569 — เลือกโมดูลที่ต้องการเข้าใช้งาน</p>

  {# KPI cards — guide §4.2 ข้อ 2 — ค่าจริงจาก ORM #}
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
    <div class="bg-gray-100/60 rounded-xl px-4 py-3">
      <p class="text-xs text-gray-500">พัสดุทั้งหมด</p>
      <p class="text-xl font-semibold">{{ kpi.items }}</p>
    </div>
    <div class="bg-gray-100/60 rounded-xl px-4 py-3">
      <p class="text-xs text-gray-500">กำลังถูกยืม</p>
      <p class="text-xl font-semibold">{{ kpi.borrowing }}</p>
    </div>
    <div class="bg-gray-100/60 rounded-xl px-4 py-3">
      <p class="text-xs text-gray-500">รออนุมัติ</p>
      <p class="text-xl font-semibold {% if kpi.pending %}text-red-600{% endif %}">{{ kpi.pending }}</p>
    </div>
  </div>

  {# การ์ดทางลัด — 1 ใบ = 1 app · กรองตาม role แล้วใน view — guide §4.2 ข้อ 3 + §8 #}
  <p class="text-xs text-gray-500 mb-2">ทางลัดเข้าโมดูล</p>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
    {% for a in apps %}
      <a href="{% url a.url %}"
         class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
        <div class="w-9 h-9 rounded-lg flex items-center justify-center mb-2 {% app_icon_class a.style %}">
          {% include "icons/"|add:a.icon|add:".svg" %}
        </div>
        <p class="text-sm font-semibold">{{ a.label }}</p>
        <p class="text-xs text-gray-500 mt-0.5">{{ a.desc }}</p>
      </a>
    {% endfor %}
  </div>
{% endblock %}
```

```python
# core/templatetags/ui_tags.py — คืน string class เต็มจาก APP_STYLES (ไม่ประกอบ dynamic ใน template)
from django import template
from ui.styles import APP_STYLES
register = template.Library()

@register.simple_tag
def app_icon_class(style):
    return APP_STYLES.get(style, APP_STYLES["accounts"])["icon"]
```

```python
# config/urls.py — 1 state ใน state diagram = 1 path
from django.urls import path, include
from core.views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),         # state Dashboard
    path("accounts/", include("allauth.urls")),                   # allauth: Google OAuth login/logout
    path("catalog/", include("catalog.urls")),
    path("borrow/", include("borrow.urls")),
    # เพิ่ม include ของแต่ละ app ตามตาราง mapping ใน UI_django_template.md §1
]
```

---

## หมายเหตุการตรวจกลับ (Traceability)

| จุดในโค้ด | อ้างอิงกฎ/เอกสาร |
|---|---|
| `APPS` (การ์ดทางลัด) | ตรง 1:1 กับเมนูใน `overview_state_diagram.puml` |
| `APP_STYLES` + `app_icon_class` tag | ตารางสี guide §2.1 + วิธีกัน purge §2.3 |
| `has_perm(...)` filter ใน view | ตาราง Actors ใน fn req ของแต่ละแอป (guide §8) |
| `LoginRequiredMixin` | บังคับ auth ที่ view ไม่ใช่แค่ซ่อนเมนู (guide §8) |
| KPI จาก `Item.objects.count()` ฯลฯ | ข้อมูลจริงจาก ORM (guide §7) |
| การ์ด `hover:shadow-md` | guide §5 (interactive card) |
| `{% include "base.html" %}` extend | app shell จุดเดียว guide §4.1 |
