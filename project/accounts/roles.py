"""บทบาทที่ใช้งานจริงของผู้ใช้ (ERD: หัวข้อ "บทบาทที่ใช้งานจริง")

มีแถว Admin → admin · มี Staff → staff · มีแค่ Student → student
"""
ADMIN = "admin"
STAFF = "staff"
STUDENT = "student"


def get_ubu_user(auth_user):
    """คืน UbuUser ของบัญชี login หรือ None (เช่น แอดมินที่ไม่มีบัญชี SSO)"""
    if not getattr(auth_user, "is_authenticated", False):
        return None
    return getattr(auth_user, "ubu_user", None)


def get_role(auth_user):
    """คืนบทบาทหลักของผู้ใช้: 'admin' / 'staff' / 'student' หรือ None ถ้ายังไม่ได้ login"""
    if not getattr(auth_user, "is_authenticated", False):
        return None
    if hasattr(auth_user, "admin_account"):
        return ADMIN
    ubu_user = get_ubu_user(auth_user)
    if ubu_user is None:
        return None
    if ubu_user.is_staff_member:
        return STAFF
    if ubu_user.is_student:
        return STUDENT
    return None
