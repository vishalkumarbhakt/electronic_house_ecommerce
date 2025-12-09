from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Product, Category, Brand, BundleDeal


class HomeView(TemplateView):
    """Homepage view."""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(
            is_active=True, 
            parent__isnull=True
        ).order_by('display_order')[:8]
        context['featured_products'] = Product.objects.filter(
            is_active=True, 
            is_featured=True, 
            stock__gt=0
        )[:8]
        context['bestsellers'] = Product.objects.filter(
            is_active=True, 
            is_bestseller=True, 
            stock__gt=0
        )[:8]
        context['new_arrivals'] = Product.objects.filter(
            is_active=True, 
            is_new_arrival=True, 
            stock__gt=0
        )[:8]
        context['deals'] = BundleDeal.objects.filter(is_active=True)[:4]
        return context


class ProductListView(ListView):
    """Product listing view with filters."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        
        # Category filter
        category_slug = self.kwargs.get('category_slug') or self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Brand filter
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Stock filter
        in_stock = self.request.GET.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        # Search query
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['price', '-price', 'name', '-name', '-created_at', '-rating', 'rating']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['brands'] = Brand.objects.filter(is_active=True)
        context['current_category'] = self.kwargs.get('category_slug')
        context['current_brand'] = self.request.GET.get('brand')
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context


class ProductDetailView(DetailView):
    """Product detail view."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'brand')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Related products (same category)
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True,
            stock__gt=0
        ).exclude(id=product.id)[:4]
        
        # EMI options
        context['emi_options'] = []
        if product.emi_available:
            for months in [3, 6, 9, 12, 18, 24]:
                if product.min_emi_months <= months <= product.max_emi_months:
                    emi_amount = product.get_emi_amount(months)
                    if emi_amount:
                        context['emi_options'].append({
                            'months': months,
                            'amount': emi_amount,
                            'no_cost': product.no_cost_emi
                        })
        
        # Bundle deals for this product
        context['bundle_deals'] = product.bundle_deals.filter(is_active=True)
        
        # Reviews
        context['reviews'] = product.reviews.filter(is_approved=True)[:10]
        
        return context


class CategoryDetailView(DetailView):
    """Category detail view (shows products in category)."""
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(
            category=self.object,
            is_active=True
        ).order_by('-created_at')[:24]
        context['subcategories'] = self.object.children.filter(is_active=True)
        return context


def product_search(request):
    """AJAX product search endpoint."""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(sku__icontains=query),
        is_active=True
    )[:10]
    
    results = [{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'price': str(p.price),
        'image': p.main_image.url if p.main_image else '',
        'category': p.category.name if p.category else '',
        'url': p.get_absolute_url(),
    } for p in products]
    
    return JsonResponse({'products': results})


def product_compare(request):
    """Product comparison view."""
    product_ids = request.GET.getlist('ids')
    if len(product_ids) > 4:
        product_ids = product_ids[:4]
    
    products = Product.objects.filter(id__in=product_ids, is_active=True)
    
    # Get all unique spec keys
    all_specs = set()
    for product in products:
        all_specs.update(product.specs.keys())
    
    return render(request, 'products/compare.html', {
        'products': products,
        'all_specs': sorted(all_specs),
    })


def calculate_emi(request):
    """API endpoint to calculate EMI."""
    try:
        amount = float(request.GET.get('amount', 0))
        months = int(request.GET.get('months', 6))
        no_cost = request.GET.get('no_cost', 'false').lower() == 'true'
        
        if no_cost:
            emi = amount / months
        else:
            interest_rate = 0.12 / 12  # 12% annual
            emi = amount * interest_rate * ((1 + interest_rate) ** months) / (((1 + interest_rate) ** months) - 1)
        
        return JsonResponse({
            'success': True,
            'emi': round(emi, 2),
            'total': round(emi * months, 2),
            'interest': round((emi * months) - amount, 2) if not no_cost else 0,
        })
    except (ValueError, TypeError, ZeroDivisionError):
        return JsonResponse({'success': False, 'error': 'Invalid input'})

