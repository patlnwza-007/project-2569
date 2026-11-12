from django.contrib import admin

from .models import PurchasePlan, Suggestion


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("name", "student", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name",)


@admin.register(PurchasePlan)
class PurchasePlanAdmin(admin.ModelAdmin):
    list_display = ("name", "suggestion", "created_by", "created_at")
    search_fields = ("name",)
