from django.db import transaction
from django.utils import timezone

from .models import Student, UbuUser


@transaction.atomic
def link_sso_user(auth_user, name="", email=""):
    """UC-15: login SSO ครั้งแรก → ผูก/สร้าง USER และสร้าง STUDENT

    - ถ้ามี USER ที่แอดมินตั้ง Role Override ไว้ล่วงหน้า (อีเมลตรงกัน) ให้ผูกกับบัญชี login นี้
    - ถ้ายังไม่เป็นเจ้าหน้าที่ ให้เริ่มเป็นนักศึกษา (ตัดสินใจข้อ 1 = ก.)
    """
    email = (email or auth_user.email or "").lower()
    ubu_user, _ = UbuUser.objects.get_or_create(email=email, defaults={"name": name})
    changed = []
    if ubu_user.auth_user_id is None:
        ubu_user.auth_user = auth_user
        changed.append("auth_user")
    if not ubu_user.first_login:
        ubu_user.first_login = timezone.now()
        changed.append("first_login")
    if name and not ubu_user.name:
        ubu_user.name = name
        changed.append("name")
    if changed:
        ubu_user.save(update_fields=changed)
    if not ubu_user.is_staff_member and not ubu_user.is_student:
        Student.objects.create(user=ubu_user)
    return ubu_user
