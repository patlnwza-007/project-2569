from django.contrib import admin

from .models import DurableMaterial, Equipment, Item, Material


class MaterialInline(admin.StackedInline):
    model = Material
    max_num = 1
    extra = 0


class DurableMaterialInline(admin.StackedInline):
    model = DurableMaterial
    max_num = 1
    extra = 0


class EquipmentInline(admin.StackedInline):
    model = Equipment
    max_num = 1
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "item_type", "base_status", "location", "unit", "purchase_price")
    list_filter = ("item_type", "base_status")
    search_fields = ("name", "location", "equipment__asset_tag")
    inlines = [MaterialInline, DurableMaterialInline, EquipmentInline]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("item", "qty_available", "qty_total")
    search_fields = ("item__name",)


@admin.register(DurableMaterial)
class DurableMaterialAdmin(admin.ModelAdmin):
    list_display = ("item", "qty_available", "qty_total", "max_borrow_days", "fine_rate_per_day")
    search_fields = ("item__name",)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("asset_tag", "item", "status", "custodian", "max_borrow_days", "fine_rate_per_day")
    list_filter = ("status",)
    search_fields = ("asset_tag", "item__name", "custodian")
