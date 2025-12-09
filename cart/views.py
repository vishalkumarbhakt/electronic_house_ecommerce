from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from products.models import Product
from .cart import SessionCart


def cart_detail(request):
    """Display the cart."""
    cart = SessionCart(request)
    items = cart.get_items_with_products()
    
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': items,
        'total': cart.get_total_price(),
    })


@require_POST
def cart_add(request, product_id):
    """Add a product to the cart."""
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    quantity = int(request.POST.get('quantity', 1))
    update = request.POST.get('update', False) == 'true'
    
    # Check stock
    if product.track_inventory and quantity > product.stock:
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': False,
                'error': f'Only {product.stock} items available'
            })
        return redirect('cart:cart_detail')
    
    cart.add(product, quantity=quantity, update_quantity=update)
    
    # HTMX response
    if request.headers.get('HX-Request'):
        items = cart.get_items_with_products()
        html = render_to_string('cart/partials/cart_mini.html', {
            'cart': cart,
            'cart_items': items,
        }, request=request)
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
            'html': html,
            'message': f'{product.name} added to cart'
        })
    
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """Update cart item quantity."""
    cart = SessionCart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check stock
    if product.track_inventory and quantity > product.stock:
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': False,
                'error': f'Only {product.stock} items available'
            })
        quantity = product.stock
    
    cart.update_quantity(product_id, quantity)
    
    if request.headers.get('HX-Request'):
        items = cart.get_items_with_products()
        html = render_to_string('cart/partials/cart_items.html', {
            'cart': cart,
            'cart_items': items,
        }, request=request)
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
            'html': html,
        })
    
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart."""
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id)
    
    cart.remove(product)
    
    if request.headers.get('HX-Request'):
        items = cart.get_items_with_products()
        html = render_to_string('cart/partials/cart_items.html', {
            'cart': cart,
            'cart_items': items,
        }, request=request)
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
            'html': html,
            'message': f'{product.name} removed from cart'
        })
    
    return redirect('cart:cart_detail')


def cart_clear(request):
    """Clear all items from cart."""
    cart = SessionCart(request)
    cart.clear()
    
    if request.headers.get('HX-Request'):
        return JsonResponse({
            'success': True,
            'cart_count': 0,
            'cart_total': '0',
            'message': 'Cart cleared'
        })
    
    return redirect('cart:cart_detail')


def cart_count(request):
    """Get cart item count (for header updates)."""
    cart = SessionCart(request)
    return JsonResponse({
        'count': len(cart),
        'total': str(cart.get_total_price()),
    })
