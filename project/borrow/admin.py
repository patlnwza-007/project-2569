from django.contrib import admin

from .models import (
    BorrowItem, BorrowRequest, Cart, CartItem, DamageReport, Queue, ReturnItem, ReturnRequest,
)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("student", "updated_at")
    inlines = [CartItemInline]


class BorrowItemInline(admin.TabularInline):
    model = BorrowItem
    extra = 0


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "status", "is_special", "created_at", "approved_by")
    list_filter = ("status", "is_special")
    search_fields = ("student__student_id", "student__user__email")
    inlines = [BorrowItemInline]


@admin.register(BorrowItem)
class BorrowItemAdmin(admin.ModelAdmin):
    list_display = ("id", "borrow_request", "item", "qty", "due_date")
    search_fields = ("item__name", "item__equipment__asset_tag")


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "borrow_request", "status", "inspected_by", "custom_fine", "fine_paid", "created_at")
    list_filter = ("status", "fine_paid")
    inlines = [ReturnItemInline]


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "student", "status", "joined_at", "notified_at")
    list_filter = ("status",)


@admin.register(DamageReport)
class DamageReportAdmin(admin.ModelAdmin):
    list_display = ("id", "item_name", "student", "location", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("item_name", "location")
