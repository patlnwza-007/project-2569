"""บทบาทที่ใช้งานจริงของผู้ใช้ (ERD: หัวข้อ "บทบาทที่ใช้งานจริง")

มีแถว Admin → admin · มี Staff → staff · มีแค่ Student → student

ผู้ใช้ที่มีทั้ง Student และ Staff (Dual-Role, UC-33) สลับโหมดได้ → โหมดที่เลือกเก็บใน session
แล้ว AccessGateMiddleware ใส่ไว้ที่ request.user._active_role ก่อนทุก view
"""
ADMIN = "admin"
STAFF = "staff"
STUDENT = "student"
SESSION_KEY = "active_role"


def get_ubu_user(auth_user):
    """คืน UbuUser ของบัญชี login หรือ None (เช่น แอดมินที่ไม่มีบัญชี SSO)"""
    if not getattr(auth_user, "is_authenticated", False):
        return None
    return getattr(auth_user, "ubu_user", None)


def available_roles(auth_user):
    """บทบาททั้งหมดที่บัญชีนี้มีสิทธิ์ใช้ เรียงตามบทบาทเริ่มต้นก่อน"""
    if not getattr(auth_user, "is_authenticated", False):
        return []
    if hasattr(auth_user, "admin_account"):
        return [ADMIN]
    ubu = get_ubu_user(auth_user)
    if ubu is None:
        return []
    roles = []
    if ubu.is_staff_member:
        roles.append(STAFF)
    if ubu.is_student:
        roles.append(STUDENT)
    return roles


def get_role(auth_user):
    """คืนบทบาทที่ใช้งานอยู่: 'admin' / 'staff' / 'student' หรือ None

    ค่าเริ่มต้น = บทบาทแรกใน available_roles (staff มาก่อน student)
    ผู้ใช้ Dual-Role ที่สลับโหมดแล้ว → ใช้โหมดที่เลือก (UC-33 Role Switching)
    """
    roles = available_roles(auth_user)
    if not roles:
        return None
    chosen = getattr(auth_user, "_active_role", None)
    return chosen if chosen in roles else roles[0]
