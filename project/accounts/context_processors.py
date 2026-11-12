from .navigation import ROLE_LABEL, build_menu
from .roles import ADMIN, available_roles, get_role, get_ubu_user


def shell(request):
    """ข้อมูลของ Top Bar / Side Bar ที่ทุกหน้าใช้ (templates/components/topbar.html, sidebar.html)"""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    role = get_role(user)
    ubu = get_ubu_user(user)
    if role == ADMIN:
        name = user.admin_account.name or user.username
    else:
        name = (ubu.name if ubu else "") or user.get_full_name() or user.username
    roles = available_roles(user)
    return {
        "role": role,
        "switch_roles": [(r, ROLE_LABEL[r]) for r in roles] if len(roles) > 1 else [],
        "role_label": ROLE_LABEL.get(role, "ไม่มีบทบาท"),
        "display_name": name,
        "nav_menu": build_menu(role, ubu, request.path) if role else [],
    }
