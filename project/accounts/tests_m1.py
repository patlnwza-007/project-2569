"""M1 · account — UC-15 (เข้าสู่ระบบ + กรอกข้อมูลครั้งแรก) และ UC-13 (โปรไฟล์)"""
from types import SimpleNamespace

from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .adapters import UBUSocialAccountAdapter
from .forms import INVALID_LOGIN, PHONE_MESSAGE
from .models import Student, UbuUser
from .tests_shell import make_staff, make_student

User = get_user_model()
LOGIN = reverse("accounts:login")
ADMIN_LOGIN = reverse("accounts:admin_login")
ONBOARDING = reverse("accounts:onboarding")
PROFILE = reverse("accounts:profile")


class LoginPageTests(TestCase):
    """UC-15: หน้า login 2 แท็บ"""

    def test_sso_tab_is_default(self):
        r = self.client.get(LOGIN)
        self.assertEqual(r.context["active_tab"], "sso")
        self.assertContains(r, 'id="p_login_sso_btn"')

    def test_admin_tab_via_query(self):
        self.assertEqual(self.client.get(LOGIN + "?tab=admin").context["active_tab"], "admin")

    def test_anonymous_root_goes_to_login(self):
        """ตัดสินใจ M1 ข้อ 6: ไม่มีหน้าต้อนรับ"""
        self.assertRedirects(self.client.get("/"), LOGIN + "?next=/", fetch_redirect_response=False)


class AdminLoginTests(TestCase):
    """UC-15 ช่องทางที่ 2: Django superuser"""

    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "a@example.com", "s3cret-pass")

    def test_superuser_logs_in_and_lands_on_admin_home(self):
        r = self.client.post(ADMIN_LOGIN, {"username": "admin", "password": "s3cret-pass"}, follow=True)
        self.assertEqual(r.redirect_chain[-1][0], reverse("coming_soon", args=["user-list"]))
        self.admin.refresh_from_db()
        self.assertIsNotNone(self.admin.last_login)          # ADMIN.last_login อัปเดต
        self.assertEqual(self.client.get("/admin/").status_code, 200)  # เปิด /admin/ ได้โดยไม่ต้อง login ซ้ำ

    def test_wrong_password(self):
        r = self.client.post(ADMIN_LOGIN, {"username": "admin", "password": "nope"})
        self.assertContains(r, INVALID_LOGIN)
        self.assertEqual(r.context["active_tab"], "admin")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_non_superuser_rejected_with_same_message(self):
        """บัญชีที่ไม่ใช่ superuser (เช่น บัญชีทดสอบจาก seed ที่มีรหัสผ่าน) เข้าทางแอดมินไม่ได้"""
        User.objects.create_user("s001@ubu.ac.th", password="pw-123456")
        r = self.client.post(ADMIN_LOGIN, {"username": "s001@ubu.ac.th", "password": "pw-123456"})
        self.assertContains(r, INVALID_LOGIN)
        self.assertNotIn("_auth_user_id", self.client.session)


class SSOAdapterTests(TestCase):
    """UC-15 ช่องทางที่ 1: Alternative Flow ของ SSO"""

    def _request(self):
        req = RequestFactory().get("/accounts/google/login/callback/")
        req.session = {}
        req._messages = FallbackStorage(req)
        return req

    def _login(self, email):
        return SimpleNamespace(user=SimpleNamespace(email=email))

    def test_non_ubu_email_rejected(self):
        with self.assertRaises(ImmediateHttpResponse):
            UBUSocialAccountAdapter().pre_social_login(self._request(), self._login("x@gmail.com"))

    def test_blocked_user_rejected(self):
        UbuUser.objects.create(email="b@ubu.ac.th", blocked=True, block_reason="ค้างคืน")
        req = self._request()
        with self.assertRaises(ImmediateHttpResponse):
            UBUSocialAccountAdapter().pre_social_login(req, self._login("b@ubu.ac.th"))
        self.assertIn("ค้างคืน", [str(m) for m in req._messages][0])

    def test_normal_ubu_user_passes(self):
        UBUSocialAccountAdapter().pre_social_login(self._request(), self._login("ok@ubu.ac.th"))

    def test_rejection_message_shows_in_login_error_box(self):
        """ข้อความที่ adapter ส่งมา (เช่น ถูกระงับ) ต้องแสดงในกล่อง error ของหน้า login"""
        from django.contrib import messages
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.sessions.backends.db import SessionStore

        from .views import CustomLoginView

        req = RequestFactory().get(LOGIN)
        req.session = SessionStore()
        req.user = AnonymousUser()
        req._messages = FallbackStorage(req)
        messages.error(req, "บัญชีนี้ถูกระงับสิทธิ์การใช้งาน เหตุผล: ค้างคืน")
        resp = CustomLoginView.as_view()(req)
        resp.render()
        html = resp.content.decode()
        self.assertIn('id="p_login_login-error"', html)
        self.assertIn("เหตุผล: ค้างคืน", html)


class FirstTimeSetupTests(TestCase):
    """UC-15 ข้อ 3ก"""

    def setUp(self):
        self.auth = make_student("new@ubu.ac.th", complete=False)
        self.client.force_login(self.auth)

    def _post(self, **data):
        payload = {"name": "สมใจ ใหม่", "student_id": "66114549999", "phone": "0899999999"} | data
        return self.client.post(ONBOARDING, payload)

    def test_valid_saves_and_goes_home(self):
        r = self._post()
        self.assertRedirects(r, "/", fetch_redirect_response=False)
        s = Student.objects.get(pk=self.auth.ubu_user.pk)
        self.assertEqual((s.student_id, s.phone, s.user.name), ("66114549999", "0899999999", "สมใจ ใหม่"))
        self.assertTrue(s.is_profile_complete)

    def test_student_id_must_be_11_digits(self):
        r = self._post(student_id="6611")
        self.assertFormError(r.context["form"], "student_id", "กรุณากรอกรหัสนักศึกษาให้ถูกต้อง (เป็นตัวเลข 11 หลัก)")
        self.assertFalse(Student.objects.get(pk=self.auth.ubu_user.pk).is_profile_complete)

    def test_phone_format(self):
        """ตัดสินใจ M1 ข้อ 1: ^0[689]\\d{8}$"""
        for bad in ["0212345678", "08123", "08a2345678"]:
            with self.subTest(phone=bad):
                self.assertFormError(self._post(phone=bad).context["form"], "phone", PHONE_MESSAGE)

    def test_duplicate_student_id(self):
        make_student("other@ubu.ac.th")  # ใช้ 66114540001
        r = self._post(student_id="66114540001")
        self.assertIn("ถูกใช้งานแล้ว", r.context["form"].errors["student_id"][0])

    def test_complete_student_is_sent_home(self):
        self._post()
        self.assertRedirects(self.client.get(ONBOARDING), "/", fetch_redirect_response=False)

    def test_other_pages_blocked_until_done(self):
        self.assertRedirects(self.client.get(PROFILE), ONBOARDING)


class ProfileTests(TestCase):
    """UC-13"""

    def setUp(self):
        self.auth = make_student()
        self.client.force_login(self.auth)

    def test_view_mode_by_default(self):
        r = self.client.get(PROFILE)
        self.assertFalse(r.context["edit_mode"])
        self.assertContains(r, 'id="p_profile_btn_edit"')
        self.assertContains(r, "66114540001")
        self.assertContains(r, "s1@ubu.ac.th")
        self.assertNotContains(r, 'id="p_profile_f-phone"')

    def test_edit_mode(self):
        r = self.client.get(PROFILE + "?edit=1")
        self.assertTrue(r.context["edit_mode"])
        self.assertContains(r, 'id="p_profile_f-phone"')
        self.assertContains(r, 'id="p_profile_btn_cancel"')

    def test_save_success(self):
        r = self.client.post(PROFILE, {"phone": "0911111111"}, follow=True)
        self.assertEqual(r.redirect_chain[-1][0], PROFILE)
        self.assertFalse(r.context["edit_mode"])
        self.assertContains(r, "บันทึกข้อมูลส่วนตัวสำเร็จ")
        self.assertEqual(Student.objects.get(pk=self.auth.ubu_user.pk).phone, "0911111111")

    def test_invalid_phone_not_saved(self):
        r = self.client.post(PROFILE, {"phone": "12345"})
        self.assertTrue(r.context["edit_mode"])
        self.assertContains(r, PHONE_MESSAGE)
        self.assertEqual(Student.objects.get(pk=self.auth.ubu_user.pk).phone, "0812345678")

    def test_student_id_and_email_cannot_be_changed(self):
        self.client.post(PROFILE, {"phone": "0911111111", "student_id": "99999999999", "email": "h@ubu.ac.th"})
        s = Student.objects.get(pk=self.auth.ubu_user.pk)
        self.assertEqual((s.student_id, s.user.email), ("66114540001", "s1@ubu.ac.th"))

    def test_return_to_next_after_save(self):
        """UC-13 Alternative: มาจาก UC-06 → เปิดโหมดแก้ไข + แถบเตือน แล้วพากลับ"""
        r = self.client.get(PROFILE + "?next=/borrow/cart/")
        self.assertTrue(r.context["edit_mode"])
        self.assertContains(r, 'id="p_profile_notice-return"')
        r = self.client.post(PROFILE, {"phone": "0922222222", "next": "/borrow/cart/"})
        self.assertRedirects(r, "/borrow/cart/", fetch_redirect_response=False)

    def test_external_next_is_ignored(self):
        r = self.client.post(PROFILE, {"phone": "0922222222", "next": "https://evil.example.com/"})
        self.assertRedirects(r, PROFILE, fetch_redirect_response=False)

    def test_menu_link_is_live_and_active(self):
        r = self.client.get(PROFILE)
        profile = next(m for m in r.context["nav_menu"] if m["key"] == "profile")
        self.assertTrue(profile["ready"] and profile["active"])
        self.assertEqual(profile["url"], PROFILE)

    def test_staff_cannot_open_profile(self):
        """ตัดสินใจ M1 ข้อ 5"""
        self.client.force_login(make_staff())
        self.assertEqual(self.client.get(PROFILE).status_code, 403)
