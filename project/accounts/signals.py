from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Admin


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_admin_for_superuser(sender, instance, **kwargs):
    """createsuperuser → สร้างแถว ADMIN คู่กันอัตโนมัติ (UC-15 ช่องทางที่ 2)"""
    if instance.is_superuser and not hasattr(instance, "admin_account"):
        Admin.objects.create(
            auth_user=instance,
            name=instance.get_full_name(),
            email=instance.email or "",
        )
