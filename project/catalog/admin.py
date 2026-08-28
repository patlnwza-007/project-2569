from django.contrib import admin
from .models import Category, Item, AssetTag


class AssetTagInline(admin.TabularInline):
    model = AssetTag
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'description')
    search_fields = ('name',)
    list_per_page = 500


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'item_type', 'category', 'total_quantity', 'available_quantity', 'location', 'is_active')
    list_filter = ('item_type', 'category', 'is_active')
    search_fields = ('code', 'name', 'location')
    list_per_page = 500
    actions_on_top = True
    actions_on_bottom = True
    inlines = [AssetTagInline]


@admin.register(AssetTag)
class AssetTagAdmin(admin.ModelAdmin):
    list_display = ('asset_code', 'item', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('asset_code', 'item__name')
    list_per_page = 500
