# Template — UI Django MVT Frontend

> วิธีใช้: ใช้เป็นจุดเริ่มของ frontend แต่ละแอป — คัดลอกโครงไปที่ Django project ของคุณ แล้วแทนที่ `{{...}}` ด้วยค่าจริงของแอป
> ต้องทำตามกฎใน [`UI_django_frontend.md`](../guide/UI_django_frontend.md) ทุกข้อ โดยเฉพาะ **1 state = 1 URL**, **สีประจำแอป (`APP_STYLES`)**, และ **conditional render + บังคับสิทธิ์ที่ view ตาม role**
> ดูตัวอย่างที่กรอกครบแล้วได้ที่ [`UI_django_example.md`](../example/UI_django_example.md)

---

## 1. ตาราง Mapping — กรอกให้ครบก่อนเขียนโค้ด (กัน state ตกหล่น)

ดึง state จาก `{{app}}/state/module_state_diagram*.puml` มาใส่ทีละแถว — **1 state = 1 แถว = 1 URL = 1 view = 1 template**:

| State (หน้าจอ) | URL path + name | View | Template | UC ที่รองรับ | Model/ORM ที่ใช้ | Role ที่เห็น | สถานะ |
|---|---|---|---|---|---|---|:---:|
| {{ItemList}} | {{`items/` · `catalog:item_list`}} | {{ItemListView}} | {{catalog/item_list.html}} | {{UC-01, UC-05}} | {{Item}} | {{Student/Staff}} | ☐ |
| {{...}} | | | | | | | ☐ |

> โปรเจกต์ที่มีหลายแอปให้ทำตารางแยกต่อแอป และตั้ง URL namespace ต่อแอป (`app_name = "catalog"` ใน `urls.py`) เช่น `catalog:item_list`, `borrow:request_create`

---

## 2. โครงสร้างโปรเจกต์

```
<project>/
├── manage.py
├── config/                      ← โปรเจกต์ Django
│   ├── settings.py              ← INSTALLED_APPS: allauth, tailwind, apps ของเรา
│   └── urls.py                  ← include ทุก app urls + allauth ('accounts/')
├── templates/
│   ├── base.html                ← app shell: topbar + sidebar (§4) — ทุกหน้า extend ไฟล์นี้
│   ├── partials/                ← component ใช้ร่วม: _button, _badge, _empty_state, _toast
│   └── icons/                   ← lucide SVG partial (pencil.svg, trash.svg, ...)
├── ui/
│   ├── styles.py                ← APP_STYLES map (§2.3 ใน guide) — ห้ามประกอบ class dynamic
│   └── context_processors.py    ← ส่ง app_styles / เมนู sidebar เข้า template ทุกหน้า
├── {{app}}/                     ← 1 Django app ต่อ 1 โมดูล
│   ├── models.py
│   ├── views.py                 ← 1 state = 1 view (ClassBased แนะนำ)
│   ├── urls.py                  ← app_name + path() 1 บรรทัดต่อ 1 state
│   ├── forms.py
│   └── templates/{{app}}/       ← 1 ไฟล์ต่อ 1 state + โฟลเดอร์ partials/ สำหรับ htmx fragment
└── static/
    └── css/                     ← output ของ Tailwind build
```

---

## 3. สีประจำแอป (`ui/styles.py` + context processor)

Tailwind สแกน class ตอน build — **ห้ามประกอบชื่อ class แบบ dynamic** (`bg-{{ color }}-600` จะถูก purge) ต้อง map เป็น string เต็ม:

```python
# ui/styles.py — ตารางสีตาม UI_django_frontend.md §2.1 (ห้ามสลับสีระหว่างแอป)
APP_STYLES = {
    "accounts": {"icon": "bg-blue-100 text-blue-700",   "btn": "bg-blue-600 hover:bg-blue-700",   "active": "bg-blue-50 text-blue-700",   "ring": "focus:ring-blue-300"},
    "catalog":  {"icon": "bg-violet-100 text-violet-700","btn": "bg-violet-600 hover:bg-violet-700","active": "bg-violet-50 text-violet-700","ring": "focus:ring-violet-300"},
    "borrow":   {"icon": "bg-teal-100 text-teal-700",    "btn": "bg-teal-600 hover:bg-teal-700",    "active": "bg-teal-50 text-teal-700",   "ring": "focus:ring-teal-300"},
    "admin":    {"icon": "bg-slate-100 text-slate-700",  "btn": "bg-slate-600 hover:bg-slate-700",  "active": "bg-slate-100 text-slate-700","ring": "focus:ring-slate-300"},
    # ... เพิ่ม 1 แถวต่อ 1 app ตาม overview_state_diagram
}
```

```python
# ui/context_processors.py — ให้ทุก template เข้าถึง app_styles ของแอปปัจจุบัน
from .styles import APP_STYLES

def ui(request):
    app = getattr(request.resolver_match, "app_name", None) or "accounts"
    return {"app_styles": APP_STYLES.get(app, APP_STYLES["accounts"]), "APP_STYLES": APP_STYLES}
```

> ลงทะเบียนใน `settings.py` → `TEMPLATES[0]["OPTIONS"]["context_processors"]` เพิ่ม `"ui.context_processors.ui"`

---

## 4. App Shell (`templates/base.html`)

```django
{% load static %}
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{{ ชื่อระบบ }}{% endblock %}</title>
  <link href="{% static 'css/site.css' %}" rel="stylesheet">           {# Tailwind build #}
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/htmx.org@2"></script>
  <script defer src="https://unpkg.com/alpinejs@3" ></script>
  {# htmx แนบ CSRF ให้ทุก request อัตโนมัติ #}
  <script>document.body?.addEventListener('htmx:configRequest', e => e.detail.headers['X-CSRFToken'] = '{{ csrf_token }}');</script>
</head>
<body class="min-h-screen bg-gray-50 font-[Noto_Sans_Thai]" hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>

  {# ===== Top bar ===== #}
  <header class="bg-white border-b border-gray-200 px-4 py-2.5 flex items-center justify-between sticky top-0 z-10">
    <span class="font-semibold text-sm">{{ ชื่อระบบ }}</span>
    <div class="flex items-center gap-4" x-data="{ menu: false }">
      {% include "icons/search.svg" %}
      {# กระดิ่ง: dropdown มี "ตั้งค่าการแจ้งเตือน" + ออกจากระบบ — ไม่ใช่เมนู sidebar #}
      <button @click="menu = !menu" aria-label="เมนูผู้ใช้">{% include "icons/bell.svg" %}</button>
      <span class="text-sm">{{ user.get_full_name|default:user.email }}</span>
      <div x-show="menu" @click.outside="menu=false" class="absolute right-4 top-12 bg-white border rounded-xl shadow-md p-2 text-sm">
        <a href="{% url 'account_logout' %}" class="block px-3 py-1.5 hover:bg-gray-50 rounded-lg">ออกจากระบบ</a>
      </div>
    </div>
  </header>

  <div class="flex">
    {# ===== Sidebar 3 กลุ่ม — กรองตาม role เสมอ (§4.1, §8) ===== #}
    <nav class="w-60 bg-white border-r border-gray-200 p-3 hidden lg:block">
      {% include "partials/_sidebar.html" %}
    </nav>
    <main class="flex-1 p-6">
      {# toast จาก Django messages (§7) #}
      {% if messages %}
        <div class="fixed top-4 right-4 z-50 space-y-2">
          {% for m in messages %}
            <div x-data="{ show: true }" x-show="show" x-init="setTimeout(() => show=false, 4500)"
                 class="rounded-xl px-4 py-2 text-sm text-white shadow-md
                        {% if m.tags == 'success' %}bg-green-600{% elif m.tags == 'error' %}bg-red-600{% else %}bg-gray-700{% endif %}">
              {{ m }}
            </div>
          {% endfor %}
        </div>
      {% endif %}
      {% block content %}{% endblock %}
    </main>
  </div>
</body>
</html>
```

```django
{# templates/partials/_sidebar.html — เมนูกรองตาม role/permission #}
<p class="px-2 py-1 text-[11px] uppercase tracking-wide text-gray-400">โปรไฟล์</p>
<a href="{% url 'accounts:me' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
  {% include "icons/user.svg" %} บัญชีของฉัน
</a>

<p class="px-2 py-1 text-[11px] uppercase tracking-wide text-gray-400 mt-3">โมดูล</p>
{# 1 บรรทัดต่อ 1 app ตาม overview_state_diagram — แสดงเฉพาะ role ที่มีสิทธิ์ #}
<a href="{% url 'catalog:item_list' %}"
   class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm
          {% if request.resolver_match.app_name == 'catalog' %}{{ APP_STYLES.catalog.active }} font-semibold{% else %}text-gray-600 hover:bg-gray-50{% endif %}">
  {% include "icons/book.svg" %} {{ ชื่อโมดูล }}
</a>

{% if perms.auth.view_user %}   {# ผู้ดูแลระบบเท่านั้น #}
  <p class="px-2 py-1 text-[11px] uppercase tracking-wide text-gray-400 mt-3">ผู้ดูแลระบบ</p>
  <a href="{% url 'admin_console:users' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
    {% include "icons/settings.svg" %} จัดการผู้ใช้งาน
  </a>
{% endif %}
```

---

## 5. View + URL + Template — หน้า list ตาม anatomy (guide §4.3)

```python
# {{app}}/urls.py — 1 state = 1 path (name ตรงกับ state ใน diagram)
from django.urls import path
from . import views

app_name = "{{app}}"
urlpatterns = [
    path("", views.{{Entity}}ListView.as_view(), name="{{entity}}_list"),
    # ... 1 บรรทัดต่อ 1 state
]
```

```python
# {{app}}/views.py — บังคับสิทธิ์ที่ view (§8) ไม่ใช่แค่ซ่อนเมนู
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import {{Entity}}

class {{Entity}}ListView(LoginRequiredMixin, ListView):
    model = {{Entity}}
    paginate_by = 20
    template_name = "{{app}}/{{entity}}_list.html"
    context_object_name = "rows"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        return qs.filter({{name_field}}__icontains=q) if q else qs

    def get(self, request, *args, **kwargs):
        # ค้นหาแบบ live → คืนเฉพาะ partial ตาราง (htmx) ไม่ reload ทั้งหน้า
        if request.headers.get("HX-Request"):
            self.object_list = self.get_queryset()
            ctx = self.get_context_data()
            return self.render_to_response(ctx, template_name="{{app}}/partials/_{{entity}}_rows.html")
        return super().get(request, *args, **kwargs)
```

```django
{# {{app}}/templates/{{app}}/{{entity}}_list.html #}
{% extends "base.html" %}
{% block content %}
  {# 1. Top: ชื่อหน้า + จำนวน + primary action 1 ปุ่มเดียว #}
  <div class="flex items-center justify-between mb-4">
    <div>
      <h1 class="text-2xl font-bold">{{ ชื่อหน้า }}</h1>
      <p class="text-xs text-gray-500">{{ page_obj.paginator.count }} รายการ</p>
    </div>
    <a href="{% url '{{app}}:{{entity}}_create' %}"
       class="{{ app_styles.btn }} text-white text-sm font-semibold rounded-xl px-4 py-2 flex items-center gap-1.5">
      {% include "icons/plus.svg" %} {{ เพิ่ม... }}
    </a>
  </div>

  {# 2. Filter bar — ค้นหา live ด้วย htmx #}
  <div class="flex items-center gap-2 mb-4">
    <div class="relative flex-1 max-w-xs">
      {% include "icons/search.svg" %}
      <input type="search" name="q" placeholder="{{ ค้นหา... }}"
             hx-get="{% url '{{app}}:{{entity}}_list' %}" hx-target="#rows" hx-trigger="keyup changed delay:400ms, search"
             class="w-full border border-gray-300 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 {{ app_styles.ring }}">
    </div>
  </div>

  {# 3. Content: empty / ตาราง — ครบ state ตาม guide §7 #}
  <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 text-xs uppercase tracking-wider text-gray-500">
        <tr><th class="text-left px-4 py-3">{{ คอลัมน์ }}</th></tr>
      </thead>
      <tbody id="rows">
        {% include "{{app}}/partials/_{{entity}}_rows.html" %}
      </tbody>
    </table>
  </div>
  {# 4. Pagination ใต้ตาราง (เมื่อข้อมูลเกิน 1 หน้า) #}
{% endblock %}
```

```django
{# {{app}}/templates/{{app}}/partials/_{{entity}}_rows.html — htmx swap เข้ามาที่ #rows #}
{% for r in rows %}
  <tr class="border-t border-gray-100 hover:bg-gray-50">
    <td class="px-4 py-3">{{ r.{{name_field}} }}</td>
  </tr>
{% empty %}
  <tr><td class="text-center py-12 text-gray-500">
    {{ ยังไม่มีข้อมูล }} —
    <a href="{% url '{{app}}:{{entity}}_create' %}" class="text-{{app}}-600 underline">{{ สร้างรายการแรก }}</a>
  </td></tr>
{% endfor %}
```

---

## 6. หมายเหตุ Auth (django-allauth)

```python
# config/settings.py (ย่อ) — ล็อกอิน Google OAuth + Whitelist
INSTALLED_APPS += ["allauth", "allauth.account", "allauth.socialaccount", "allauth.socialaccount.providers.google"]
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend", "allauth.account.auth_backends.AuthenticationBackend"]
LOGIN_REDIRECT_URL = "/"
# ตรวจ Whitelist: ผูก signal `allauth.account.signals.user_signed_up` หรือ custom adapter
#   → เช็คว่า email อยู่ในรายชื่อที่อนุญาต ก่อนอนุญาต active
```

- **Authentication** (คุณคือใคร) = allauth + Google + Whitelist · **Authorization** (ทำอะไรได้) = Django permission/group บังคับที่ view — แยกคนละชั้น (§8 ใน guide)
- dev ไม่ต้องตั้ง Google OAuth ก็ได้ ใช้ `createsuperuser` + login ปกติทดสอบก่อน

---

## 7. Checklist ย่อก่อน commit

- [ ] ตาราง §1 กรอกครบทุก state และติ๊ก ☐ → ✅ ครบ (1 state = 1 path + view + template)
- [ ] ทุก template `{% extends "base.html" %}` · มี `{% csrf_token %}` ในทุกฟอร์ม post
- [ ] ทุกหน้าใช้ `app_styles`/`APP_STYLES` ไม่ hardcode สี / ไม่ประกอบ class แบบ dynamic
- [ ] loading / empty / error ครบทุกหน้า list (`{% empty %}`, messages toast, `hx-indicator`)
- [ ] เมนูและปุ่มกรองตาม role แล้ว **และ view บังคับสิทธิ์จริง** ด้วย mixin/decorator

ฉบับเต็มดู [`UI_django_frontend.md`](../guide/UI_django_frontend.md) §10
