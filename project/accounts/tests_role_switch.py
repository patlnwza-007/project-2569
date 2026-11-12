"""UC-33 Role Switching: ผู้ใช้ Dual-Role สลับโหมดนักศึกษา ↔ เจ้าหน้าที่"""
from django.test import TestCase
from django.urls import reverse

from .models import Staff
from .navigation import MENU
from .roles import STAFF, STUDENT
from .tests_shell import make_admin, make_staff, make_student

SWITCH = reverse("accounts:switch_role")


def make_dual(email="dual@ubu.ac.th", complete=True):
    auth = make_student(email, complete=complete)
    Staff.objects.create(user=auth.ubu_user, is_override=True)
    return auth


class RoleSwitchTests(TestCase):
    def test_dual_user_defaults_to_staff_and_sees_switch(self):
        self.client.force_login(make_dual())
        r = self.client.get("/", follow=True)
        self.assertEqual(r.context["role"], STAFF)
        self.assertContains(r, 'id="role-switch-btn"')
        self.assertEqual(dict(r.context["switch_roles"]).keys(), {STAFF, STUDENT})

    def test_switch_to_student_changes_menu_and_access(self):
        self.client.force_login(make_dual())
        r = self.client.post(SWITCH, {"role": STUDENT})
        self.assertRedirects(r, reverse("coming_soon", args=[MENU[STUDENT][0].key]))
        r = self.client.get(reverse("accounts:profile"))
        self.assertEqual(r.status_code, 200)                       # หน้าของนักศึกษาเข้าได้
        self.assertEqual([m["key"] for m in r.context["nav_menu"]], [m.key for m in MENU[STUDENT]])
        self.assertContains(r, "นักศึกษา (ใช้อยู่)")
        self.assertEqual(self.client.get(reverse("catalog:item_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("coming_soon", args=["pending-requests"])).status_code, 403)

    def test_switch_back_to_staff(self):
        self.client.force_login(make_dual())
        self.client.post(SWITCH, {"role": STUDENT})
        self.client.post(SWITCH, {"role": STAFF})
        r = self.client.get(reverse("coming_soon", args=["staff-dashboard"]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 403)

    def test_choice_resets_after_logout(self):
        auth = make_dual()
        self.client.force_login(auth)
        self.client.post(SWITCH, {"role": STUDENT})
        self.client.post(reverse("accounts:logout"))
        self.client.force_login(auth)
        self.assertEqual(self.client.get("/", follow=True).context["role"], STAFF)

    def test_single_role_users_cannot_switch(self):
        for maker, target in [(make_student, STAFF), (make_staff, STUDENT), (make_admin, STUDENT)]:
            with self.subTest(target=target):
                self.client.force_login(maker())
                self.assertEqual(self.client.post(SWITCH, {"role": target}).status_code, 403)
                self.assertNotContains(self.client.get("/", follow=True), 'id="role-switch-btn"')

    def test_invalid_role_and_get_rejected(self):
        self.client.force_login(make_dual())
        self.assertEqual(self.client.post(SWITCH, {"role": "admin"}).status_code, 403)
        self.assertEqual(self.client.get(SWITCH).status_code, 405)

    def test_student_mode_still_requires_profile(self):
        """โหมดนักศึกษายังต้องกรอกข้อมูลครั้งแรกก่อน แต่โหมดเจ้าหน้าที่ใช้งานได้"""
        self.client.force_login(make_dual(complete=False))
        self.assertEqual(self.client.get(reverse("coming_soon", args=["staff-dashboard"])).status_code, 200)
        self.client.post(SWITCH, {"role": STUDENT})
        self.assertRedirects(self.client.get(reverse("catalog:item_list")), reverse("accounts:onboarding"))

    def test_losing_staff_row_falls_back_to_student(self):
        """แอดมินยกเลิก Override ระหว่างที่ผู้ใช้อยู่โหมดเจ้าหน้าที่ → กลับเป็นนักศึกษาทันที"""
        auth = make_dual()
        self.client.force_login(auth)
        Staff.objects.filter(pk=auth.ubu_user.pk).delete()
        r = self.client.get("/", follow=True)
        self.assertEqual(r.context["role"], STUDENT)
        self.assertNotContains(r, 'id="role-switch-btn"')
