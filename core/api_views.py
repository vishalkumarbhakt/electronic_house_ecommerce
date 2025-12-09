"""
API Views for Electronic House using Django REST Framework.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from products.models import Product, Category
from cart.cart import SessionCart
from .serializers import ProductSerializer, CategorySerializer, ProductDetailSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for categories."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for products."""
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by brand
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter in stock only
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products."""
        products = self.get_queryset().filter(is_featured=True)[:12]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def bestsellers(self, request):
        """Get bestseller products."""
        products = self.get_queryset().filter(is_bestseller=True)[:12]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def emi_options(self, request, slug=None):
        """Get EMI options for a product."""
        product = self.get_object()
        if not product.emi_available:
            return Response({'available': False})
        
        options = []
        for months in [3, 6, 9, 12, 18, 24]:
            if product.min_emi_months <= months <= product.max_emi_months:
                emi_amount = product.get_emi_amount(months)
                if emi_amount:
                    options.append({
                        'months': months,
                        'amount': emi_amount,
                        'no_cost': product.no_cost_emi
                    })
        
        return Response({
            'available': True,
            'options': options
        })


class CartAPIView(APIView):
    """API view for cart operations."""
    
    def get(self, request):
        """Get current cart."""
        cart = SessionCart(request)
        items = cart.get_items_with_products()
        
        return Response({
            'items': [{
                'product_id': item['product'].id,
                'name': item['product'].name,
                'price': str(item['product'].price),
                'quantity': item['quantity'],
                'total': str(item['total_price']),
                'image': item['product'].main_image.url if item['product'].main_image else None,
            } for item in items],
            'total_items': len(cart),
            'total_price': str(cart.get_total_price()),
        })
    
    def post(self, request):
        """Add item to cart."""
        cart = SessionCart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        if product.track_inventory and quantity > product.stock:
            return Response({
                'success': False,
                'error': f'Only {product.stock} items available'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart.add(product, quantity=quantity)
        
        return Response({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })
    
    def put(self, request):
        """Update cart item quantity."""
        cart = SessionCart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        if product.track_inventory and quantity > product.stock:
            quantity = product.stock
        
        cart.update_quantity(product_id, quantity)
        
        return Response({
            'success': True,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })
    
    def delete(self, request):
        """Remove item from cart or clear cart."""
        cart = SessionCart(request)
        product_id = request.data.get('product_id')
        
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            cart.remove(product)
            message = f'{product.name} removed from cart'
        else:
            cart.clear()
            message = 'Cart cleared'
        
        return Response({
            'success': True,
            'message': message,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })
