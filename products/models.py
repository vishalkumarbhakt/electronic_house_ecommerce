from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import shortuuid


class Category(models.Model):
    """Category model for product categorization."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="FontAwesome or similar icon class")
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'display_order']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    @property
    def product_count(self):
        return self.products.filter(is_active=True, stock__gt=0).count()


class Brand(models.Model):
    """Brand model for electronics manufacturers."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model for electronics with JSON specs."""
    
    # Basic Info
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Relationships
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Original price for showing discount"
    )
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost price for profit calculation"
    )
    
    # Electronics-specific specs (JSON)
    specs = models.JSONField(
        default=dict,
        blank=True,
        help_text="Electronics specs like RAM, storage, camera, processor, etc."
    )
    
    # Images (stored as JSON array of URLs or Image objects)
    images = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of image URLs"
    )
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Inventory
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    track_inventory = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(default=False)
    
    # Warranty & Support
    warranty_months = models.PositiveIntegerField(
        default=12,
        validators=[MinValueValidator(0), MaxValueValidator(120)]
    )
    warranty_type = models.CharField(
        max_length=50,
        choices=[
            ('manufacturer', 'Manufacturer Warranty'),
            ('seller', 'Seller Warranty'),
            ('extended', 'Extended Warranty'),
            ('none', 'No Warranty'),
        ],
        default='manufacturer'
    )
    
    # EMI & Offers
    emi_available = models.BooleanField(default=True)
    no_cost_emi = models.BooleanField(default=False)
    min_emi_months = models.PositiveIntegerField(default=3)
    max_emi_months = models.PositiveIntegerField(default=24)
    
    # Shipping
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.5, help_text="Weight in kg")
    free_shipping = models.BooleanField(default=False)
    shipping_time = models.CharField(max_length=50, default="3-5 business days")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    
    # Ratings
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'stock']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['price']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            if Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{shortuuid.uuid()[:6]}"
        if not self.sku:
            self.sku = f"EH-{shortuuid.uuid()[:8].upper()}"
        if not self.meta_title:
            self.meta_title = self.name[:60]
        if not self.meta_description:
            self.meta_description = self.short_description[:160] if self.short_description else self.description[:160]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.stock > 0 or self.allow_backorder
    
    @property
    def is_low_stock(self):
        """Check if stock is below threshold."""
        return self.track_inventory and self.stock <= self.low_stock_threshold and self.stock > 0
    
    @property
    def stock_status(self):
        """Get stock status label."""
        if not self.track_inventory:
            return "Available"
        if self.stock <= 0:
            return "Out of Stock" if not self.allow_backorder else "Available for Backorder"
        if self.is_low_stock:
            return f"Only {self.stock} left!"
        return "In Stock"
    
    def get_emi_amount(self, months=6):
        """Calculate EMI amount for given months."""
        if not self.emi_available or months < self.min_emi_months or months > self.max_emi_months:
            return None
        # Simple EMI calculation (no interest for no_cost_emi)
        if self.no_cost_emi:
            return round(float(self.price) / months, 2)
        # Standard EMI with 12% annual interest
        interest_rate = 0.12 / 12
        emi = float(self.price) * interest_rate * ((1 + interest_rate) ** months) / (((1 + interest_rate) ** months) - 1)
        return round(emi, 2)


class ProductImage(models.Model):
    """Additional product images."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.display_order}"


class ProductReview(models.Model):
    """Product reviews and ratings."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.user_name}"


class BundleDeal(models.Model):
    """Bundle deals for products (e.g., Phone + Case + Charger)."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    products = models.ManyToManyField(Product, related_name='bundle_deals')
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def total_original_price(self):
        return sum(p.price for p in self.products.all())
    
    @property
    def bundle_price(self):
        total = self.total_original_price
        return round(float(total) * (1 - float(self.discount_percentage) / 100), 2)

