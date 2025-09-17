from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    instructor = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in hours")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('store:course_detail', kwargs={'pk': self.pk})


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='lessons/videos/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='lessons/pdfs/', null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('sensors', 'Sensors'),
        ('boards', 'Development Boards'),
        ('modules', 'Modules'),
        ('kits', 'Starter Kits'),
        ('accessories', 'Accessories'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'pk': self.pk})
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    @property
    def total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('course', 'Course'),
        ('product', 'Product'),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'course', 'product')
    
    def __str__(self):
        if self.item_type == 'course':
            return f"{self.course.title} x {self.quantity}"
        else:
            return f"{self.product.name} x {self.quantity}"
    
    def get_item(self):
        return self.course if self.item_type == 'course' else self.product
    
    def get_item_price(self):
        item = self.get_item()
        return item.price if item else 0
    
    def get_total_price(self):
        return self.get_item_price() * self.quantity