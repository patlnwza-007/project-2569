from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อหมวดหมู่")
    description = models.TextField(blank=True, null=True, verbose_name="รายละเอียดหมวดหมู่")
    icon = models.CharField(max_length=50, default="package", verbose_name="ชื่อไอคอน (Lucide Icon)")

    class Meta:
        verbose_name = "หมวดหมู่พัสดุ"
        verbose_name_plural = "หมวดหมู่พัสดุ"
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    class ItemType(models.TextChoices):
        MATERIAL = 'MATERIAL', 'วัสดุ (เบิกใช้แล้วหมดไป)'
        EQUIPMENT = 'EQUIPMENT', 'ครุภัณฑ์ (ยืมใช้งานแล้วนำมาคืน)'

    code = models.CharField(max_length=50, unique=True, verbose_name="รหัสพัสดุ/ครุภัณฑ์")
    name = models.CharField(max_length=200, verbose_name="ชื่อพัสดุ/ครุภัณฑ์")
    item_type = models.CharField(
        max_length=20, 
        choices=ItemType.choices, 
        default=ItemType.EQUIPMENT, 
        verbose_name="ประเภทสิ่งของ"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="items", 
        verbose_name="หมวดหมู่"
    )
    description = models.TextField(blank=True, null=True, verbose_name="รายละเอียดและสเปกพัสดุ")
    
    unit = models.CharField(max_length=30, default="ชิ้น", verbose_name="หน่วยนับ (เช่น ชิ้น, เครื่อง, ชุด, กล่อง)")
    max_borrow_days = models.PositiveIntegerField(default=7, verbose_name="จำนวนวันยืมสูงสุด (สำหรับครุภัณฑ์)")
    
    image = models.ImageField(upload_to='items/', blank=True, null=True, verbose_name="อัปโหลดรูปภาพพัสดุ")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="หรือลิงก์รูปภาพ (Image URL)")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="ตำแหน่งชั้นวาง (Position Map)")
    
    total_quantity = models.PositiveIntegerField(default=1, verbose_name="จำนวนทั้งหมดในคลัง")
    available_quantity = models.PositiveIntegerField(default=1, verbose_name="จำนวนพร้อมใช้งาน")
    
    is_active = models.BooleanField(default=True, verbose_name="สถานะพร้อมให้บริการ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่เพิ่มพัสดุ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุด")

    class Meta:
        verbose_name = "รายการสิ่งของ"
        verbose_name_plural = "รายการสิ่งของทั้งหมด"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_item_type_display()}] {self.code} - {self.name}"

    @property
    def is_available(self):
        return self.available_quantity > 0 and self.is_active

    @property
    def is_equipment(self):
        return self.item_type == self.ItemType.EQUIPMENT

    @property
    def is_material(self):
        return self.item_type == self.ItemType.MATERIAL

    @property
    def image_display(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return None


class AssetTag(models.Model):
    class AssetStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'พร้อมให้ยืม'
        BORROWED = 'BORROWED', 'กำลังถูกยืม'
        DAMAGED = 'DAMAGED', 'ครุภัณฑ์เสียหาย/ชำรุด'
        REPAIRING = 'REPAIRING', 'กำลังส่งซ่อม'
        RETIRED = 'RETIRED', 'ปลดระวาง/เลิกใช้งาน'

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='asset_tags', verbose_name="ครุภัณฑ์หลัก")
    asset_code = models.CharField(max_length=100, unique=True, verbose_name="รหัส Asset Tag รายชิ้น (เช่น UBU-EQ-001)")
    status = models.CharField(
        max_length=20, 
        choices=AssetStatus.choices, 
        default=AssetStatus.AVAILABLE, 
        verbose_name="สถานะรายชิ้น"
    )
    note = models.TextField(blank=True, null=True, verbose_name="หมายเหตุสภาพครุภัณฑ์")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ลงทะเบียนชิ้นงาน")

    class Meta:
        verbose_name = "รหัสครุภัณฑ์รายชิ้น (Asset Tag)"
        verbose_name_plural = "รหัสครุภัณฑ์รายชิ้น (Asset Tags)"
        ordering = ['asset_code']

    def __str__(self):
        return f"{self.asset_code} ({self.get_status_display()})"
