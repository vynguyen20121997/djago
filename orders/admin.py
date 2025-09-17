from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_type', 'course', 'product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email')
    list_editable = ('status',)
    readonly_fields = ('id', 'user', 'total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'total_price', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Admin Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'get_item_name', 'item_type', 'quantity', 'price')
    list_filter = ('item_type', 'order__status')
    search_fields = ('order__id', 'course__title', 'product__name')
    
    def get_item_name(self, obj):
        return str(obj.get_item())
    get_item_name.short_description = 'Item'