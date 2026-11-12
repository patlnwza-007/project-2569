"""
M1 · account — ผู้ใช้งานตาม ERD: ADMIN, USER, STUDENT, STAFF

ชั้น login ใช้ `auth_user` ของ Django (ไม่อยู่ใน ERD) ส่วนตารางข้างล่างคือชั้นข้อมูลตาม ERD
ดูรายละเอียดการออกแบบที่ docs/plan/phase1_model_plan.md หัวข้อ 2
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q

STUDENT_ID_VALIDATOR = RegexValidator(r"^\d{11}$", "รหัสนักศึกษาต้องเป็นตัวเลข 11 หลัก")
PHONE_VALIDATOR = RegexValidator(r"^0[689]\d{8}$", "เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลัก ขึ้นต้นด้วย 06, 08 หรือ 09")
UBU_EMAIL_DOMAIN = "ubu.ac.th"


class Admin(models.Model):
    """ERD: ADMIN — บัญชีผู้ดูแลระบบ (Django superuser) ตารางเดี่ยว ไม่อยู่ใน ISA ของ USER"""

    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin_account",
        verbose_name="บัญชี login (Django superuser)",
    )
    name = models.CharField("ชื่อผู้ดูแลระบบ", max_length=150, blank=True)
    email = models.EmailField("อีเมล (ไม่บังคับ @ubu)", blank=True)
    created_at = models.DateTimeField("วันที่สร้างบัญชี", auto_now_add=True)

    class Meta:
        db_table = "admin"
        verbose_name = "ผู้ดูแลระบบ (ADMIN)"
        verbose_name_plural = "ผู้ดูแลระบบ (ADMIN)"

    def __str__(self):
        return self.name or self.username

    @property
    def username(self):
        return self.auth_user.username

    @property
    def last_login(self):
        return self.auth_user.last_login

    def clean(self):
        if self.auth_user_id and not self.auth_user.is_superuser:
            raise ValidationError({"auth_user": "บัญชีผู้ดูแลระบบต้องเป็น Django superuser"})


class UbuUser(models.Model):
    """ERD: USER — บัญชีผู้ใช้ UBU SSO (supertype ของ STUDENT / STAFF)"""

    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name="ubu_user", verbose_name="บัญชี login",
        help_text="ว่างได้ กรณีแอดมินตั้ง Role Override ไว้ล่วงหน้าให้อีเมลที่ยังไม่เคย login (UC-33)",
    )
    name = models.CharField("ชื่อ-นามสกุล", max_length=150, blank=True)
    email = models.EmailField("อีเมล @ubu.ac.th", unique=True)
    first_login = models.DateTimeField("เข้าสู่ระบบครั้งแรก", null=True, blank=True)
    created_at = models.DateTimeField("วันที่สร้างบัญชี", auto_now_add=True)
    blocked = models.BooleanField("สถานะระงับสิทธิ์", default=False)
    block_reason = models.TextField("เหตุผลการระงับสิทธิ์", blank=True)
    blocked_by_staff = models.ForeignKey(
        "Staff", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="blocked_users", verbose_name="เจ้าหน้าที่ผู้สั่งระงับสิทธิ์",
    )
    blocked_by_admin = models.ForeignKey(
        Admin, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="blocked_users", verbose_name="แอดมินผู้สั่งระงับสิทธิ์",
    )

    class Meta:
        db_table = "user"
        verbose_name = "ผู้ใช้ UBU SSO (USER)"
        verbose_name_plural = "ผู้ใช้ UBU SSO (USER)"
        constraints = [
            models.CheckConstraint(
                condition=Q(blocked_by_staff__isnull=True) | Q(blocked_by_admin__isnull=True),
                name="user_blocked_by_only_one",
                violation_error_message="ผู้สั่งระงับสิทธิ์ต้องเป็นเจ้าหน้าที่หรือแอดมินอย่างใดอย่างหนึ่งเท่านั้น",
            ),
        ]

    def __str__(self):
        return f"{self.name or self.email}"

    @property
    def last_login(self):
        return self.auth_user.last_login if self.auth_user_id else None

    @property
    def is_student(self):
        return hasattr(self, "student")

    @property
    def is_staff_member(self):
        return hasattr(self, "staff")

    def clean(self):
        if self.email and not self.email.lower().endswith(f"@{UBU_EMAIL_DOMAIN}"):
            raise ValidationError({"email": f"ต้องเป็นอีเมล @{UBU_EMAIL_DOMAIN} เท่านั้น"})


class Student(models.Model):
    """ERD: STUDENT — subtype ของ USER (shared primary key)"""

    user = models.OneToOneField(
        UbuUser, on_delete=models.CASCADE, primary_key=True, db_column="user_id",
        related_name="student", verbose_name="บัญชีผู้ใช้",
    )
    student_id = models.CharField(
        "รหัสนักศึกษา", max_length=11, unique=True, null=True, blank=True,
        validators=[STUDENT_ID_VALIDATOR],
    )
    phone = models.CharField("เบอร์โทรศัพท์", max_length=10, blank=True, validators=[PHONE_VALIDATOR])

    class Meta:
        db_table = "student"
        verbose_name = "นักศึกษา (STUDENT)"
        verbose_name_plural = "นักศึกษา (STUDENT)"

    def __str__(self):
        return f"{self.student_id or '-'} {self.user}"

    @property
    def is_profile_complete(self):
        """UC-13 / UC-06: ต้องมีรหัสนักศึกษาและเบอร์โทรก่อนส่งคำขอยืม"""
        return bool(self.student_id and self.phone)


class Staff(models.Model):
    """ERD: STAFF — subtype ของ USER (shared primary key, overlapping กับ STUDENT ได้)"""

    user = models.OneToOneField(
        UbuUser, on_delete=models.CASCADE, primary_key=True, db_column="user_id",
        related_name="staff", verbose_name="บัญชีผู้ใช้",
    )
    is_override = models.BooleanField("ได้สิทธิ์จาก Role Override", default=False)
    override_reason = models.TextField("เหตุผลการกำหนดบทบาท", blank=True)
    assigned_by = models.ForeignKey(
        Admin, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_staff", verbose_name="ผู้แต่งตั้งสิทธิ์",
    )
    assigned_at = models.DateTimeField("วันที่แต่งตั้งสิทธิ์", null=True, blank=True)

    class Meta:
        db_table = "staff"
        verbose_name = "เจ้าหน้าที่ (STAFF)"
        verbose_name_plural = "เจ้าหน้าที่ (STAFF)"

    def __str__(self):
        return str(self.user)
