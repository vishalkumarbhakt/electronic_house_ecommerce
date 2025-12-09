from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Category, Brand, Product, ProductImage, ProductReview, BundleDeal


class ProductImageInline(admin.TabularInline):
    """Inline for product images."""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'display_order']


class ProductReviewInline(admin.TabularInline):
    """Inline for product reviews."""
    model = ProductReview
    extra = 0
    readonly_fields = ['user_name', 'user_email', 'rating', 'title', 'comment', 'created_at']
    fields = ['user_name', 'rating', 'title', 'is_verified_purchase', 'is_approved', 'created_at']
    can_delete = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model."""
    list_display = ['name', 'parent', 'is_active', 'product_count_display', 'display_order', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']
    list_editable = ['is_active', 'display_order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'parent', 'description', 'image', 'icon_class')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count_display(self, obj):
        return obj.product_count
    product_count_display.short_description = 'Products'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin for Brand model."""
    list_display = ['name', 'is_active', 'is_featured', 'logo_preview', 'website', 'created_at']
    list_filter = ['is_active', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', obj.logo.url)
        return '-'
    logo_preview.short_description = 'Logo'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Enhanced Admin for Product model with electronics-specific features."""
    list_display = [
        'name', 'sku', 'category', 'brand', 'price_display', 
        'stock_status_display', 'is_active', 'is_featured', 'rating_display', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_featured', 'is_bestseller', 'is_new_arrival',
        'category', 'brand', 'emi_available', 'warranty_type',
        ('stock', admin.EmptyFieldListFilter),
    ]
    search_fields = ['name', 'sku', 'description', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['sku', 'created_at', 'updated_at', 'image_preview']
    inlines = [ProductImageInline, ProductReviewInline]
    save_on_top = True
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'brand', 'image_preview', 'main_image')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price'),
            'description': 'Set product pricing. Compare price shows the original price for discount display.'
        }),
        ('Electronics Specifications (JSON)', {
            'fields': ('specs',),
            'description': 'Enter specifications as JSON: {"ram": "8GB", "storage": "256GB", "processor": "A17 Pro"}'
        }),
        ('Images (JSON URLs)', {
            'fields': ('images',),
            'classes': ('collapse',),
            'description': 'Enter image URLs as JSON array: ["url1", "url2"]'
        }),
        ('Inventory', {
            'fields': ('stock', 'low_stock_threshold', 'track_inventory', 'allow_backorder'),
        }),
        ('Warranty & Support', {
            'fields': ('warranty_months', 'warranty_type'),
        }),
        ('EMI Options', {
            'fields': ('emi_available', 'no_cost_emi', 'min_emi_months', 'max_emi_months'),
            'classes': ('collapse',),
        }),
        ('Shipping', {
            'fields': ('weight', 'free_shipping', 'shipping_time'),
            'classes': ('collapse',),
        }),
        ('Status & Visibility', {
            'fields': ('is_active', 'is_featured', 'is_bestseller', 'is_new_arrival'),
        }),
        ('Ratings', {
            'fields': ('rating', 'review_count'),
            'classes': ('collapse',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def price_display(self, obj):
        """Display price with discount if applicable."""
        if obj.compare_price and obj.discount_percentage > 0:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">₹{}</span><br>'
                '<strong style="color: #00A651;">₹{}</strong> '
                '<span style="color: #FF6B35;">(-{}%)</span>',
                obj.compare_price, obj.price, obj.discount_percentage
            )
        return format_html('<strong>₹{}</strong>', obj.price)
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def stock_status_display(self, obj):
        """Display stock status with color coding."""
        if not obj.track_inventory:
            return format_html('<span style="color: #666;">Not tracked</span>')
        if obj.stock <= 0:
            return format_html('<span style="color: red; font-weight: bold;">Out of Stock</span>')
        if obj.is_low_stock:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠️ {} left</span>',
                obj.stock
            )
        return format_html('<span style="color: green;">{} in stock</span>', obj.stock)
    stock_status_display.short_description = 'Stock'
    stock_status_display.admin_order_field = 'stock'
    
    def rating_display(self, obj):
        """Display rating with stars."""
        if obj.rating > 0:
            stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
            return format_html(
                '<span style="color: #FFD700;">{}</span> ({} reviews)',
                stars, obj.review_count
            )
        return format_html('<span style="color: #999;">No reviews</span>')
    rating_display.short_description = 'Rating'
    
    def image_preview(self, obj):
        """Display main image preview."""
        if obj.main_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: contain; border: 1px solid #ddd;" />',
                obj.main_image.url
            )
        return '-'
    image_preview.short_description = 'Image Preview'
    
    actions = ['make_featured', 'make_bestseller', 'mark_out_of_stock', 'export_as_csv']
    
    @admin.action(description='Mark selected as featured')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} products marked as featured.')
    
    @admin.action(description='Mark selected as bestseller')
    def make_bestseller(self, request, queryset):
        queryset.update(is_bestseller=True)
        self.message_user(request, f'{queryset.count()} products marked as bestseller.')
    
    @admin.action(description='Mark selected as out of stock')
    def mark_out_of_stock(self, request, queryset):
        queryset.update(stock=0)
        self.message_user(request, f'{queryset.count()} products marked as out of stock.')
    
    @admin.action(description='Export selected to CSV')
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Name', 'Category', 'Brand', 'Price', 'Stock', 'Status'])
        
        for product in queryset:
            writer.writerow([
                product.sku,
                product.name,
                product.category.name if product.category else '',
                product.brand.name if product.brand else '',
                product.price,
                product.stock,
                'Active' if product.is_active else 'Inactive'
            ])
        
        return response


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin for ProductImage model."""
    list_display = ['product', 'image_preview', 'is_primary', 'display_order']
    list_filter = ['is_primary', 'product__category']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'display_order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin for ProductReview model."""
    list_display = ['product', 'user_name', 'rating_stars', 'title', 'is_verified_purchase', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user_name', 'user_email', 'title', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['product', 'user_name', 'user_email', 'rating', 'title', 'comment', 'created_at']
    date_hierarchy = 'created_at'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    actions = ['approve_reviews', 'reject_reviews']
    
    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} reviews approved.')
    
    @admin.action(description='Reject selected reviews')
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} reviews rejected.')


@admin.register(BundleDeal)
class BundleDealAdmin(admin.ModelAdmin):
    """Admin for BundleDeal model."""
    list_display = ['name', 'discount_percentage', 'is_active', 'product_list', 'bundle_price_display', 'start_date', 'end_date']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['products']
    
    def product_list(self, obj):
        products = obj.products.all()[:3]
        names = [p.name for p in products]
        if obj.products.count() > 3:
            names.append(f'... +{obj.products.count() - 3} more')
        return ', '.join(names)
    product_list.short_description = 'Products'
    
    def bundle_price_display(self, obj):
        return format_html(
            '<span style="text-decoration: line-through; color: #999;">₹{}</span> → '
            '<strong style="color: #00A651;">₹{}</strong>',
            obj.total_original_price, obj.bundle_price
        )
    bundle_price_display.short_description = 'Bundle Price'

