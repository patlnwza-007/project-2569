"""เฟส 2: โครงหน้ากลาง — เมนูตามบทบาท, สิทธิ์, ผู้ถูกระงับ, กรอกข้อมูลครั้งแรก"""
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from borrow.models import BorrowRequest, Cart, CartItem
from catalog.models import Item
from catalog.services import create_item

from .models import Staff, Student, UbuUser
from .navigation import MENU, home_url
from .permissions import RoleRequiredMixin, role_required
from .roles import ADMIN, STAFF, STUDENT

User = get_user_model()


def make_student(email="s1@ubu.ac.th", complete=True):
    auth = User.objects.create_user(email, email=email)
    ubu = UbuUser.objects.create(email=email, name="นักศึกษา ทดสอบ", auth_user=auth)
    Student.objects.create(user=ubu, student_id="66114540001" if complete else None,
                           phone="0812345678" if complete else "")
    return auth


def make_staff(email="st1@ubu.ac.th"):
    auth = User.objects.create_user(email, email=email)
    Staff.objects.create(user=UbuUser.objects.create(email=email, name="เจ้าหน้าที่ ทดสอบ", auth_user=auth))
    return auth


def make_admin():
    return User.objects.create_superuser("root", "root@example.com", "x")


class HomeRedirectTests(TestCase):
    """UC-15 ข้อ 5: หน้าแรกตามบทบาท"""

    def test_anonymous_goes_to_login(self):
        r = self.client.get("/")
        self.assertRedirects(r, "/accounts/login/?next=/", fetch_redirect_response=False)

    def test_each_role_lands_on_its_first_menu(self):
        for maker, role in [(make_student, STUDENT), (make_staff, STAFF), (make_admin, ADMIN)]:
            with self.subTest(role=role):
                self.client.force_login(maker())
                r = self.client.get("/")
                self.assertRedirects(r, home_url(role), fetch_redirect_response=False)

    def test_user_without_role_gets_403(self):
        self.client.force_login(User.objects.create_user("norole"))
        self.assertEqual(self.client.get("/").status_code, 403)


class MenuTests(TestCase):
    def _menu_keys(self, response):
        return [m["key"] for m in response.context["nav_menu"]]

    def test_student_sees_student_menu_only(self):
        self.client.force_login(make_student())
        r = self.client.get(reverse("coming_soon", args=["profile"]))
        self.assertEqual(self._menu_keys(r), [m.key for m in MENU[STUDENT]])
        self.assertContains(r, "นักศึกษา ทดสอบ")
        self.assertContains(r, 'id="topbar-role"')
        self.assertNotContains(r, "คำขอรออนุมัติ")

    def test_staff_and_admin_menus(self):
        self.client.force_login(make_staff())
        r = self.client.get(reverse("coming_soon", args=["staff-dashboard"]))
        self.assertEqual(self._menu_keys(r), [m.key for m in MENU[STAFF]])
        self.client.force_login(make_admin())
        r = self.client.get(reverse("coming_soon", args=["user-list"]))
        self.assertEqual(self._menu_keys(r), [m.key for m in MENU[ADMIN]])

    def test_active_menu_is_marked(self):
        self.client.force_login(make_student())
        r = self.client.get(reverse("borrow:cart"))
        active = [m["key"] for m in r.context["nav_menu"] if m["active"]]
        self.assertEqual(active, ["cart"])

    def test_cart_badge_is_sum_of_qty(self):
        """00_shell_navigation: badge ตะกร้า = SUM(CART_ITEM.qty)"""
        auth = make_student()
        cart = Cart.objects.create(student=auth.ubu_user.student)
        CartItem.objects.create(cart=cart, item=create_item(Item.ItemType.MATERIAL, name="A", qty_total=9), qty=3)
        CartItem.objects.create(cart=cart, item=create_item(Item.ItemType.MATERIAL, name="B", qty_total=9), qty=2)
        self.client.force_login(auth)
        r = self.client.get(reverse("coming_soon", args=["cart"]))
        badges = {m["key"]: m["badge"] for m in r.context["nav_menu"]}
        self.assertEqual(badges["cart"], 5)

    def test_staff_pending_badge(self):
        BorrowRequest.objects.create(student=make_student().ubu_user.student)
        self.client.force_login(make_staff())
        r = self.client.get(reverse("coming_soon", args=["staff-dashboard"]))
        badges = {m["key"]: m["badge"] for m in r.context["nav_menu"]}
        self.assertEqual(badges["pending-requests"], 1)

    def test_other_roles_page_is_forbidden(self):
        self.client.force_login(make_student())
        self.assertEqual(self.client.get(reverse("coming_soon", args=["pending-requests"])).status_code, 403)

    def test_unknown_page_404(self):
        self.client.force_login(make_student())
        self.assertEqual(self.client.get(reverse("coming_soon", args=["nope"])).status_code, 404)


class PermissionHelperTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

        @role_required(STAFF)
        def staff_only(request):
            return HttpResponse("ok")
        self.staff_only = staff_only

    def _request(self, user):
        req = self.rf.get("/x/")
        req.user = user
        return req

    def test_decorator_allows_matching_role(self):
        self.assertEqual(self.staff_only(self._request(make_staff())).status_code, 200)

    def test_decorator_denies_other_role(self):
        with self.assertRaises(PermissionDenied):
            self.staff_only(self._request(make_student()))

    def test_decorator_redirects_anonymous(self):
        from django.contrib.auth.models import AnonymousUser
        r = self.staff_only(self._request(AnonymousUser()))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.url)

    def test_mixin(self):
        from django.views import View

        class V(RoleRequiredMixin, View):
            allowed_roles = (STUDENT, STAFF)

            def get(self, request):
                return HttpResponse("ok")

        self.assertEqual(V.as_view()(self._request(make_student())).status_code, 200)
        with self.assertRaises(PermissionDenied):
            V.as_view()(self._request(make_admin()))


class AccessGateTests(TestCase):
    def test_blocked_user_is_sent_to_blocked_page(self):
        """ถูกระงับระหว่าง login ค้างไว้ → ถูกบล็อกทุกหน้า"""
        auth = make_student()
        self.client.force_login(auth)
        UbuUser.objects.filter(pk=auth.ubu_user.pk).update(blocked=True, block_reason="ค้างคืนของเกินกำหนด")
        r = self.client.get(reverse("coming_soon", args=["cart"]))
        self.assertRedirects(r, reverse("accounts:blocked"))
        r = self.client.get(reverse("accounts:blocked"))
        self.assertContains(r, "ค้างคืนของเกินกำหนด")

    def test_unblocked_user_cannot_stay_on_blocked_page(self):
        self.client.force_login(make_student())
        self.assertRedirects(self.client.get(reverse("accounts:blocked")), "/", fetch_redirect_response=False)

    def test_incomplete_student_goes_to_onboarding(self):
        """UC-15 ข้อ 3ก"""
        self.client.force_login(make_student(complete=False))
        r = self.client.get(reverse("coming_soon", args=["cart"]))
        self.assertRedirects(r, reverse("accounts:onboarding"))
        self.assertEqual(self.client.get(reverse("accounts:onboarding")).status_code, 200)

    def test_staff_is_never_sent_to_onboarding(self):
        self.client.force_login(make_staff())
        self.assertEqual(self.client.get(reverse("coming_soon", args=["staff-dashboard"])).status_code, 200)

    def test_logout_reachable_while_blocked(self):
        auth = make_student()
        UbuUser.objects.filter(pk=auth.ubu_user.pk).update(blocked=True)
        self.client.force_login(auth)
        r = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(r, reverse("accounts:login"))
