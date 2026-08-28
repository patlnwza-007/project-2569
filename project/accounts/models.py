from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'นักศึกษา (Student)'
        STAFF = 'STAFF', 'เจ้าหน้าที่ (Staff)'
        ADMIN = 'ADMIN', 'ผู้ดูแลระบบ (Admin)'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, verbose_name="บทบาทหลัก")
    role_override = models.CharField(max_length=20, choices=Role.choices, blank=True, null=True, verbose_name="บทบาทสวมสิทธิ์ (Role Override)")
    
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="เบอร์โทรศัพท์ติดต่อ")
    
    is_blocked = models.BooleanField(default=False, verbose_name="ถูกระงับสิทธิ์ใช้งาน")
    block_reason = models.TextField(blank=True, null=True, verbose_name="เหตุผลที่ถูกระงับสิทธิ์")
    
    first_login = models.DateTimeField(auto_now_add=True, verbose_name="เข้าสู่ระบบครั้งแรก")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุด")

    def __str__(self):
        return f"{self.user.username} ({self.get_effective_role_display()})"

    def get_effective_role(self):
        """คำนวณบทบาทที่มีผลใช้งานจริง (Role Override มีผลเหนือกว่า Role เริ่มต้น ตาม FR-17 / FR-34)"""
        return self.role_override if self.role_override else self.role

    def get_effective_role_display(self):
        effective_role = self.get_effective_role()
        for choice in self.Role.choices:
            if choice[0] == effective_role:
                return choice[1]
        return effective_role


# Signal สร้าง UserProfile อัตโนมัติเมื่อมีการสร้าง User ใหม่ (รวมถึงจาก Google SSO)
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
