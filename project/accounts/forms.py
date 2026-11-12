from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator

from .models import Student

INVALID_LOGIN = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
PHONE_MESSAGE = "กรุณากรอกเบอร์โทรศัพท์ให้ถูกต้อง (เป็นตัวเลข 10 หลัก)"
STUDENT_ID_MESSAGE = "กรุณากรอกรหัสนักศึกษาให้ถูกต้อง (เป็นตัวเลข 11 หลัก)"

phone_validator = RegexValidator(r"^0[689]\d{8}$", PHONE_MESSAGE)  # ตัดสินใจ M1 ข้อ 1
student_id_validator = RegexValidator(r"^\d{11}$", STUDENT_ID_MESSAGE)

INPUT = "w-full border border-gray-300 rounded-xl px-3.5 py-2 text-sm focus:outline-none focus:ring-2"


class AdminLoginForm(AuthenticationForm):
    """UC-15 ช่องทางที่ 2: รับเฉพาะ Django superuser · ผิดทุกกรณีใช้ข้อความเดียวกัน (ไม่บอกว่าผิดที่ช่องไหน)"""

    error_messages = {"invalid_login": INVALID_LOGIN, "inactive": INVALID_LOGIN}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls = f"{INPUT} font-mono focus:ring-purple-500/20 focus:border-purple-500"
        self.fields["username"].widget.attrs.update({"class": cls, "id": "p_login_admin_user", "autocomplete": "username"})
        self.fields["password"].widget.attrs.update({"class": cls, "id": "p_login_admin_pass"})

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_superuser:
            raise forms.ValidationError(INVALID_LOGIN, code="invalid_login")


class FirstTimeSetupForm(forms.Form):
    """UC-15 ข้อ 3ก: นักศึกษากรอกรหัสนักศึกษา + เบอร์โทร (และตรวจชื่อ) ก่อนเข้าใช้งานครั้งแรก"""

    name = forms.CharField(label="ชื่อ - นามสกุล", max_length=150)
    student_id = forms.CharField(label="รหัสนักศึกษา (11 หลัก)", max_length=11, validators=[student_id_validator])
    phone = forms.CharField(label="เบอร์โทรศัพท์ติดต่อ (10 หลัก)", max_length=10, validators=[phone_validator])

    def __init__(self, *args, student, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)
        attrs = {"class": f"{INPUT} focus:ring-blue-500/20 focus:border-blue-500"}
        self.fields["name"].widget.attrs.update(attrs)
        self.fields["student_id"].widget.attrs.update(attrs | {"inputmode": "numeric", "placeholder": "เช่น 66114540001"})
        self.fields["phone"].widget.attrs.update(attrs | {"inputmode": "numeric", "placeholder": "เช่น 0812345678"})

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_student_id(self):
        sid = self.cleaned_data["student_id"]
        if Student.objects.filter(student_id=sid).exclude(pk=self.student.pk).exists():
            raise forms.ValidationError("รหัสนักศึกษานี้ถูกใช้งานแล้ว กรุณาตรวจสอบหรือติดต่อเจ้าหน้าที่")
        return sid

    def save(self):
        ubu = self.student.user
        ubu.name = self.cleaned_data["name"]
        ubu.save(update_fields=["name"])
        self.student.student_id = self.cleaned_data["student_id"]
        self.student.phone = self.cleaned_data["phone"]
        self.student.save(update_fields=["student_id", "phone"])
        return self.student


class ProfileForm(forms.ModelForm):
    """UC-13: โหมดแก้ไขของโปรไฟล์ แก้ได้ชื่อ-นามสกุลและเบอร์โทร (รหัสนักศึกษาและอีเมลล็อก)

    ชื่อแก้ได้เพิ่มจาก UC-13 (ผู้ใช้ขอ 2026-11-13 · ดู docs/conflicts.md)
    """

    name = forms.CharField(label="ชื่อ - นามสกุล", max_length=150)
    phone = forms.CharField(label="เบอร์โทรศัพท์ติดต่อ", max_length=10, validators=[phone_validator])

    class Meta:
        model = Student
        fields = ["phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].initial = self.instance.user.name
        self.fields["name"].widget.attrs.update({
            "id": "p_profile_f-name",
            "class": "w-full border border-blue-400 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20",
        })
        self.fields["phone"].widget.attrs.update({
            "id": "p_profile_f-phone", "maxlength": "10", "inputmode": "numeric",
            "placeholder": "ระบุเบอร์โทรศัพท์ 10 หลัก เช่น 0812345678",
            "class": "w-full border border-blue-400 rounded-xl px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/20",
        })

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("กรุณากรอกชื่อ - นามสกุล")
        return name

    def save(self, commit=True):
        student = super().save(commit=commit)
        ubu = student.user
        ubu.name = self.cleaned_data["name"]
        if commit:
            ubu.save(update_fields=["name"])
        return student
