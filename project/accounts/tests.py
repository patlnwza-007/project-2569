from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Admin, Staff, Student, UbuUser
from .roles import ADMIN, STAFF, STUDENT, get_role
from .services import link_sso_user

User = get_user_model()


class AdminAccountTests(TestCase):
    def test_createsuperuser_creates_admin_row(self):
        """UC-15 ช่องทางที่ 2: superuser ต้องมีแถว ADMIN คู่กัน"""
        su = User.objects.create_superuser("root", "root@example.com", "x")
        self.assertTrue(Admin.objects.filter(auth_user=su).exists())
        self.assertEqual(get_role(su), ADMIN)
        self.assertEqual(su.admin_account.username, "root")

    def test_normal_user_gets_no_admin_row(self):
        u = User.objects.create_user("a@ubu.ac.th")
        self.assertFalse(Admin.objects.filter(auth_user=u).exists())

    def test_admin_must_be_superuser(self):
        u = User.objects.create_user("plain")
        with self.assertRaises(ValidationError):
            Admin(auth_user=u).full_clean()


class SSOLinkTests(TestCase):
    def test_first_login_creates_user_and_student(self):
        """UC-15 ข้อ 3ก: login ครั้งแรก → USER + STUDENT, role = student"""
        auth = User.objects.create_user("new@ubu.ac.th", email="new@ubu.ac.th")
        ubu = link_sso_user(auth, name="นักศึกษาใหม่")
        self.assertTrue(ubu.is_student)
        self.assertFalse(ubu.student.is_profile_complete)
        self.assertIsNotNone(ubu.first_login)
        self.assertEqual(get_role(auth), STUDENT)

    def test_second_login_does_not_duplicate(self):
        auth = User.objects.create_user("x@ubu.ac.th", email="x@ubu.ac.th")
        link_sso_user(auth)
        link_sso_user(auth)
        self.assertEqual(UbuUser.objects.count(), 1)
        self.assertEqual(Student.objects.count(), 1)

    def test_preassigned_override_links_and_stays_staff(self):
        """ERD: Role Override ล่วงหน้า → login ครั้งแรกผูกบัญชี ไม่สร้าง STUDENT"""
        ubu = UbuUser.objects.create(email="pre@ubu.ac.th")
        Staff.objects.create(user=ubu, is_override=True)
        auth = User.objects.create_user("pre@ubu.ac.th", email="pre@ubu.ac.th")
        link_sso_user(auth)
        ubu.refresh_from_db()
        self.assertEqual(ubu.auth_user, auth)
        self.assertFalse(ubu.is_student)
        self.assertEqual(get_role(auth), STAFF)


class UbuUserRuleTests(TestCase):
    def test_email_must_be_ubu(self):
        with self.assertRaises(ValidationError):
            UbuUser(email="someone@gmail.com").full_clean()

    def test_blocked_by_only_one(self):
        """ERD: blocked_by_staff / blocked_by_admin อย่างใดอย่างหนึ่งเท่านั้น"""
        staff = Staff.objects.create(user=UbuUser.objects.create(email="st@ubu.ac.th"))
        admin = User.objects.create_superuser("root2", "r@x.com", "x").admin_account
        with self.assertRaises(IntegrityError), transaction.atomic():
            UbuUser.objects.create(email="b@ubu.ac.th", blocked=True, blocked_by_staff=staff, blocked_by_admin=admin)

    def test_overlapping_student_and_staff(self):
        ubu = UbuUser.objects.create(email="both@ubu.ac.th")
        Student.objects.create(user=ubu, student_id="66114540099", phone="0812345699")
        Staff.objects.create(user=ubu, is_override=True)
        self.assertTrue(ubu.is_student and ubu.is_staff_member)


class StudentValidationTests(TestCase):
    def _student(self, **kw):
        return Student(user=UbuUser.objects.create(email="v@ubu.ac.th"), **kw)

    def test_valid(self):
        self._student(student_id="66114540001", phone="0812345678").full_clean()

    def test_student_id_must_be_11_digits(self):
        with self.assertRaises(ValidationError):
            self._student(student_id="6611454", phone="0812345678").full_clean()

    def test_phone_format(self):
        """UC-15: เบอร์โทร ^0[689]\\d{8}$"""
        with self.assertRaises(ValidationError):
            self._student(student_id="66114540001", phone="0212345678").full_clean()


class RoleTests(TestCase):
    def test_anonymous(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertIsNone(get_role(AnonymousUser()))
