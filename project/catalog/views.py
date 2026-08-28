from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Item, Category
from .forms import ItemForm


def is_staff_user(user):
    if not user.is_authenticated:
        return False
    try:
        return user.profile.get_effective_role() in ['STAFF', 'ADMIN']
    except (AttributeError, Exception):
        return False


@login_required
def item_list_view(request):
    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    item_type = request.GET.get('item_type', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort_by = request.GET.get('sort', '').strip()

    items = Item.objects.select_related('category').prefetch_related('asset_tags').all()

    # Search Query
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Category Filter
    if category_id:
        items = items.filter(category_id=category_id)

    # Item Type Filter (Material vs Equipment)
    if item_type:
        items = items.filter(item_type=item_type.upper())

    # Status Filter
    if status_filter == 'available':
        items = items.filter(available_quantity__gt=0, is_active=True)
    elif status_filter == 'empty':
        items = items.filter(available_quantity=0, is_active=True)
    elif status_filter == 'unavailable':
        items = items.filter(is_active=False)

    # Sorting
    if sort_by == 'qty-desc':
        items = items.order_by('-available_quantity')
    elif sort_by == 'qty-asc':
        items = items.order_by('available_quantity')
    elif sort_by == 'name-asc':
        items = items.order_by('name')
    elif sort_by == 'days-desc':
        items = items.order_by('-max_borrow_days')
    else:
        items = items.order_by('-created_at')

    categories = Category.objects.all()

    context = {
        'items': items,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_type': item_type,
        'selected_status': status_filter,
        'selected_sort': sort_by,
        'total_count': items.count(),
        'is_staff': is_staff_user(request.user),
    }
    return render(request, 'catalog/item_list.html', context)


@login_required
def item_detail_view(request, pk):
    item = get_object_or_404(Item.objects.select_related('category').prefetch_related('asset_tags'), pk=pk)
    context = {
        'item': item,
        'asset_tags': item.asset_tags.all() if item.is_equipment else [],
        'is_staff': is_staff_user(request.user),
    }
    return render(request, 'catalog/item_detail.html', context)


@login_required
def item_create_view(request):
    if not is_staff_user(request.user):
        messages.error(request, "คุณไม่มีสิทธิ์ในการเพิ่มพัสดุ (สำหรับเจ้าหน้าที่เท่านั้น)")
        return redirect('catalog:item_list')

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            if item.item_type == 'MATERIAL':
                item.max_borrow_days = 0
            item.save()
            messages.success(request, f"เพิ่มรายการ '{item.name}' เข้าสู่คลังเรียบร้อยแล้ว!")
            return redirect('catalog:item_list')
    else:
        form = ItemForm()

    context = {
        'form': form,
        'title': 'เพิ่มวัสดุ/ครุภัณฑ์ใหม่',
        'is_edit': False,
    }
    return render(request, 'catalog/item_form.html', context)


@login_required
def item_edit_view(request, pk):
    if not is_staff_user(request.user):
        messages.error(request, "คุณไม่มีสิทธิ์ในการแก้ไขพัสดุ (สำหรับเจ้าหน้าที่เท่านั้น)")
        return redirect('catalog:item_list')

    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            if item.item_type == 'MATERIAL':
                item.max_borrow_days = 0
            item.save()
            messages.success(request, f"แก้ไขข้อมูล '{item.name}' เรียบร้อยแล้ว!")
            return redirect('catalog:item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)

    context = {
        'form': form,
        'item': item,
        'title': f'แก้ไขสิ่งของ: {item.name}',
        'is_edit': True,
    }
    return render(request, 'catalog/item_form.html', context)
