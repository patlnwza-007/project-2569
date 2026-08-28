from django import forms
from .models import Item, Category


class ItemForm(forms.ModelForm):
    max_borrow_days = forms.IntegerField(
        required=False,
        initial=7,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'min': 1
        })
    )

    class Meta:
        model = Item
        fields = [
            'code', 'name', 'item_type', 'category', 'description', 
            'max_borrow_days', 'image', 'image_url', 
            'location', 'total_quantity', 'available_quantity', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'เช่น EQ-001, MAT-001'
            }),
            'name': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'ชื่อวัสดุ/ครุภัณฑ์'
            }),
            'item_type': forms.Select(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white font-semibold',
                'id': 'id_item_type'
            }),
            'category': forms.Select(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'รายละเอียด สเปกอุปกรณ์ เงื่อนไขการยืม'
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-gray-300 rounded-xl p-1',
                'accept': 'image/*'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'https://example.com/image.jpg (ถ้าไม่มีไฟล์)'
            }),
            'location': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'เช่น ตู้ A1 ชั้น 2'
            }),
            'total_quantity': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'min': 1
            }),
            'available_quantity': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'min': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }
