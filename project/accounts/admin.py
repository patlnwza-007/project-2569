from django.contrib import admin

from .models import Admin, Staff, Student, UbuUser


class StudentInline(admin.StackedInline):
    model = Student
    can_delete = True
    extra = 0


class StaffInline(admin.StackedInline):
    model = Staff
    fk_name = "user"
    can_delete = True
    extra = 0


@admin.register(UbuUser)
class UbuUserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "is_student", "is_staff_member", "blocked", "first_login")
    list_filter = ("blocked",)
    search_fields = ("email", "name", "student__student_id")
    readonly_fields = ("created_at",)
    inlines = [StudentInline, StaffInline]

    @admin.display(boolean=True, description="นักศึกษา")
    def is_student(self, obj):
        return obj.is_student

    @admin.display(boolean=True, description="เจ้าหน้าที่")
    def is_staff_member(self, obj):
        return obj.is_staff_member


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "phone")
    search_fields = ("student_id", "user__email", "user__name", "phone")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("user", "is_override", "assigned_by", "assigned_at")
    list_filter = ("is_override",)
    search_fields = ("user__email", "user__name")


@admin.register(Admin)
class AdminAccountAdmin(admin.ModelAdmin):
    list_display = ("username", "name", "email", "last_login", "created_at")
    search_fields = ("auth_user__username", "name", "email")
