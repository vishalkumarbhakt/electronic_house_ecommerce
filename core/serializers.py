"""
Serializers for Electronic House API.
"""
from rest_framework import serializers
from products.models import Product, Category, Brand, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    product_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image', 
            'icon_class', 'product_count', 'meta_title', 'meta_description'
        ]


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model."""
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'description', 'website']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product listing."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'short_description',
            'category', 'category_name', 'brand', 'brand_name',
            'price', 'compare_price', 'discount_percentage',
            'main_image', 'stock', 'stock_status', 'in_stock',
            'warranty_months', 'emi_available', 'no_cost_emi',
            'rating', 'review_count',
            'is_featured', 'is_bestseller', 'is_new_arrival',
            'created_at'
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for ProductReview model."""
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'user_name', 'rating', 'title', 'comment',
            'is_verified_purchase', 'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view."""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True, source='reviews.all')
    discount_percentage = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'description', 'short_description',
            'category', 'brand',
            'price', 'compare_price', 'discount_percentage',
            'specs', 'images', 'main_image',
            'stock', 'stock_status', 'in_stock', 'is_low_stock',
            'warranty_months', 'warranty_type',
            'emi_available', 'no_cost_emi', 'min_emi_months', 'max_emi_months',
            'weight', 'free_shipping', 'shipping_time',
            'rating', 'review_count', 'reviews',
            'is_featured', 'is_bestseller', 'is_new_arrival',
            'meta_title', 'meta_description',
            'created_at', 'updated_at'
        ]
