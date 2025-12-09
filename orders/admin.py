from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Customer, Order, OrderItem, Wishlist, Coupon


class OrderItemInline(admin.TabularInline):
    """Inline for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_sku', 'product_price', 'quantity', 'total', 'warranty_info']
    fields = ['product_name', 'product_sku', 'product_price', 'quantity', 'total', 'warranty_info']
    can_delete = False
    
    def warranty_info(self, obj):
        if obj.warranty_end_date:
            days_left = (obj.warranty_end_date - timezone.now().date()).days
            if days_left > 0:
                return format_html('<span style="color: green;">{} months (expires {})</span>', 
                                   obj.warranty_months, obj.warranty_end_date)
            else:
                return format_html('<span style="color: red;">Expired</span>')
        return f'{obj.warranty_months} months'
    warranty_info.short_description = 'Warranty'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin for Customer model."""
    list_display = ['full_name', 'email', 'phone', 'city', 'state', 'order_count', 'created_at']
    list_filter = ['state', 'city', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'pincode']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_count(self, obj):
        return obj.orders.count()
    order_count.short_description = 'Orders'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Enhanced Admin for Order model."""
    list_display = [
        'order_number', 'customer_name', 'total_display', 'payment_status_badge',
        'status_badge', 'payment_method', 'emi_info', 'item_count', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'is_emi', 'created_at']
    search_fields = ['order_number', 'billing_email', 'billing_first_name', 'billing_last_name', 'billing_phone']
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at',
        'subtotal', 'total', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'
    ]
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    save_on_top = True
    list_per_page = 25
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'customer', 'user')
        }),
        ('Billing Details', {
            'fields': ('billing_first_name', 'billing_last_name', 'billing_email', 'billing_phone', 'billing_address')
        }),
        ('Shipping Details', {
            'fields': ('shipping_first_name', 'shipping_last_name', 'shipping_phone', 
                       'shipping_address', 'shipping_city', 'shipping_state', 'shipping_pincode')
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total', 'coupon_code')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'payment_id', 
                       'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('EMI Details', {
            'fields': ('is_emi', 'emi_months', 'emi_monthly_amount'),
            'classes': ('collapse',)
        }),
        ('Shipping & Tracking', {
            'fields': ('tracking_number', 'tracking_url', 'shipping_carrier'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return f"{obj.billing_first_name} {obj.billing_last_name}"
    customer_name.short_description = 'Customer'
    
    def total_display(self, obj):
        return format_html('<strong>₹{}</strong>', obj.total)
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'
    
    def payment_status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'paid': '#00A651',
            'failed': '#FF0000',
            'refunded': '#666666',
        }
        color = colors.get(obj.payment_status, '#666666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#3498db',
            'processing': '#9b59b6',
            'shipped': '#1abc9c',
            'out_for_delivery': '#2ecc71',
            'delivered': '#00A651',
            'cancelled': '#e74c3c',
            'refunded': '#95a5a6',
        }
        color = colors.get(obj.status, '#666666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def emi_info(self, obj):
        if obj.is_emi and obj.emi_months:
            return format_html('₹{}/mo × {}', obj.emi_monthly_amount, obj.emi_months)
        return '-'
    emi_info.short_description = 'EMI'
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'export_orders_csv']
    
    @admin.action(description='Mark selected as Confirmed')
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed', confirmed_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as confirmed.')
    
    @admin.action(description='Mark selected as Shipped')
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as shipped.')
    
    @admin.action(description='Mark selected as Delivered')
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as delivered.')
    
    @admin.action(description='Export selected orders to CSV')
    def export_orders_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order#', 'Date', 'Customer', 'Email', 'Phone', 'Total', 'Payment Status', 'Order Status'])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                f"{order.billing_first_name} {order.billing_last_name}",
                order.billing_email,
                order.billing_phone,
                order.total,
                order.get_payment_status_display(),
                order.get_status_display()
            ])
        
        return response


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for OrderItem model."""
    list_display = ['order', 'product_name', 'product_sku', 'product_price', 'quantity', 'total', 'warranty_months']
    list_filter = ['order__status', 'warranty_months']
    search_fields = ['order__order_number', 'product_name', 'product_sku']
    readonly_fields = ['order', 'product', 'product_name', 'product_sku', 'product_price', 'product_specs', 'quantity', 'total']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin for Wishlist model."""
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin for Coupon model."""
    list_display = ['code', 'discount_type', 'discount_value', 'min_order_amount', 
                    'usage_display', 'is_active', 'valid_from', 'valid_to', 'is_valid_now']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('Limits', {
            'fields': ('min_order_amount', 'max_discount', 'usage_limit', 'used_count')
        }),
        ('Validity', {
            'fields': ('is_active', 'valid_from', 'valid_to')
        }),
    )
    
    def usage_display(self, obj):
        if obj.usage_limit:
            return f"{obj.used_count}/{obj.usage_limit}"
        return f"{obj.used_count}/∞"
    usage_display.short_description = 'Usage'
    
    def is_valid_now(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Invalid</span>')
    is_valid_now.short_description = 'Status'

